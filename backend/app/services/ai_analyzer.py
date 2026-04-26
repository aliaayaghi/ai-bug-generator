"""AI-powered screenshot analysis service.

This module provides the AIAnalyzer class which uses OpenRouter's API
(OpenAI-compatible) to analyze screenshots and generate structured bug report suggestions.
"""
import base64
import json
from pathlib import Path
from typing import Optional

from openai import OpenAI, APIError

from app.core.config import get_settings
from app.schemas.analysis_response import AnalysisResponse


class AIAnalyzer:
    """Service for analyzing screenshots using AI vision.
    
    This class handles communication with the OpenRouter API (OpenAI-compatible)
    to analyze uploaded images and generate structured bug report suggestions.
    """
    
    # Default prompt for bug report analysis
    DEFAULT_PROMPT = """You are a bug report analyzer. Analyze this screenshot and provide a structured bug report in JSON format with these exact fields:
- title: A short descriptive title for the bug (max 100 chars)
- summary: A brief summary of what you observe (max 200 chars)
- severity: One of: low, medium, high, critical
- reproduction_steps: Steps to reproduce as a numbered list (if observable)
- expected_behavior: What should have happened
- actual_behavior: What you observe in the screenshot
- suspected_area: The UI area/component where the issue appears
- confidence: Integer 0-100 indicating how confident you are in this analysis

Respond ONLY with valid JSON, no other text."""

    def __init__(self) -> None:
        """Initialize the AI analyzer with settings."""
        self._settings = get_settings()
        self._client: Optional[OpenAI] = None
    
    @property
    def client(self) -> OpenAI:
        """Lazy initialization of OpenRouter client (OpenAI-compatible)."""
        if self._client is None:
            api_key = self._settings.OPENROUTER_API_KEY
            if not api_key:
                raise ValueError(
                    "OpenRouter API key not configured. "
                    "Set OPENROUTER_API_KEY environment variable."
                )
            self._client = OpenAI(
                api_key=api_key,
                base_url=self._settings.OPENROUTER_BASE_URL,
            )
        return self._client
    
    def _resolve_image_path(self, image_path: str) -> Path:
        """Resolve image path relative to upload directory or as absolute path.
        
        Args:
            image_path: The image path from the request.
            
        Returns:
            Resolved absolute Path object.
        """
        path = Path(image_path)
        
        # If already absolute and exists, use it
        if path.is_absolute() and path.exists():
            return path
        
        # Try relative to upload directory
        upload_dir = Path(self._settings.UPLOAD_DIR)
        candidate = upload_dir / path.name
        
        if candidate.exists():
            return candidate
        
        # Try relative to project root
        project_root = Path(self._settings.UPLOAD_DIR).parent
        candidate = project_root / path
        
        if candidate.exists():
            return candidate
        
        # Return original path for error reporting
        return path
    
    def validate_image_path(self, image_path: str) -> Path:
        """Validate that the image file exists and is readable.
        
        Args:
            image_path: Path to the image file.
            
        Returns:
            Path object if valid.
            
        Raises:
            FileNotFoundError: If the file doesn't exist.
            ValueError: If the file is not a valid image.
        """
        # Resolve the path first
        path = self._resolve_image_path(image_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {image_path}")
        
        # Check file extension
        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        if path.suffix.lower() not in valid_extensions:
            raise ValueError(
                f"Invalid file type. Supported: {', '.join(valid_extensions)}"
            )
        
        return path
    
    def _build_user_message(
        self,
        image_path: Path,
        user_note: Optional[str] = None,
        page_url: Optional[str] = None
    ) -> str:
        """Build the user message with analysis instruction and context."""
        # Include analysis instruction in user message to avoid provider errors
        instruction = """Analyze this screenshot and provide a structured bug report in JSON format with these exact fields:
- title: A short descriptive title for the bug (max 100 chars)
- summary: A brief summary of what you observe (max 200 chars)
- severity: One of: low, medium, high, critical
- reproduction_steps: Steps to reproduce as a numbered list (if observable)
- expected_behavior: What should have happened
- actual_behavior: What you observe in the screenshot
- suspected_area: The UI area/component where the issue appears
- confidence: Integer 0-100 indicating how confident you are in this analysis

Respond ONLY with valid JSON, no other text."""
        
        parts = [instruction]
        
        if user_note:
            parts.append(f"\nUser note: {user_note}")
        
        if page_url:
            parts.append(f"Page URL: {page_url}")
        
        return "\n".join(parts)
    
    def analyze(
        self,
        image_path: str,
        user_note: Optional[str] = None,
        page_url: Optional[str] = None
    ) -> AnalysisResponse:
        """Analyze a screenshot and generate a bug report suggestion.
        
        Args:
            image_path: Path to the image file to analyze.
            user_note: Optional user-provided note about the screenshot.
            page_url: Optional URL of the page where screenshot was taken.
            
        Returns:
            AnalysisResponse with structured bug report suggestion.
            
        Raises:
            FileNotFoundError: If the image file doesn't exist.
            ValueError: If the file is not a valid image.
            Exception: If the AI API call fails.
        """
        # Validate and resolve the image path
        path = self.validate_image_path(image_path)
        
        # Read and encode the image file as base64
        try:
            with open(path, "rb") as image_file:
                image_data = image_file.read()
                image_base64 = base64.b64encode(image_data).decode("utf-8")
        except Exception as e:
            raise IOError(f"Failed to read image file: {e}")
        
        # Determine MIME type from extension
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp',
        }
        mime_type = mime_types.get(path.suffix.lower(), 'image/png')
        
        # Build the user message
        user_message = self._build_user_message(path, user_note, page_url)
        
        # Call OpenAI API using Chat Completions with base64 image
        try:
            response = self.client.chat.completions.create(
                model=self._settings.OPENROUTER_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": user_message
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.3,
            )
        except APIError as e:
          raise Exception(f"AI API error: {e}")
        except Exception as e:
          raise Exception(f"Failed to analyze image: {e}")
        
        # Parse the response
        content = response.choices[0].message.content
        
        if not content:
            raise Exception("Empty response from AI")
        
        # Extract JSON from response
        try:
            # Try to find JSON in the response (in case there's extra text)
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                data = json.loads(json_str)
            else:
                data = json.loads(content)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI response as JSON: {e}")
        
        # Handle reproduction_steps - convert from list to string if needed
        repro_steps = data.get("reproduction_steps", "")
        if isinstance(repro_steps, list):
            repro_steps = "\n".join(f"{i+1}. {step}" for i, step in enumerate(repro_steps))
        
        # Validate and create response
        return AnalysisResponse(
            title=data.get("title", "Untitled Issue"),
            summary=data.get("summary", ""),
            severity=data.get("severity", "medium"),
            reproduction_steps=repro_steps,
            expected_behavior=data.get("expected_behavior", ""),
            actual_behavior=data.get("actual_behavior", ""),
            suspected_area=data.get("suspected_area", "Unknown"),
            confidence=data.get("confidence", 50)
        )


# Singleton instance for convenience
_analyzer: Optional[AIAnalyzer] = None


def get_analyzer() -> AIAnalyzer:
    """Get the global AI analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = AIAnalyzer()
    return _analyzer