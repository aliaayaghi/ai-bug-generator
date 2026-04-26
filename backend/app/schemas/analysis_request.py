"""Request schema for AI analysis endpoint."""
from typing import Optional

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """Request schema for analyzing a screenshot.
    
    Attributes:
        image_path: Absolute or relative path to the uploaded image file.
        user_note: Optional user-provided note or context about the screenshot.
        page_url: Optional URL of the page where the screenshot was taken.
    """
    
    image_path: str = Field(
        ...,
        description="Path to the uploaded image file to analyze"
    )
    user_note: Optional[str] = Field(
        default=None,
        description="Optional user note or context about the screenshot"
    )
    page_url: Optional[str] = Field(
        default=None,
        description="Optional URL of the page where the screenshot was taken"
    )