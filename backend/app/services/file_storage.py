"""File storage service for handling uploaded files."""
import os
import uuid
from pathlib import Path
from typing import Optional

from app.core.config import get_settings


def get_upload_dir() -> Path:
    """Get the upload directory path, creating it if needed."""
    settings = get_settings()
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def generate_safe_filename(original_filename: str) -> str:
    """Generate a safe unique filename to avoid collisions."""
    # Get file extension
    ext = Path(original_filename).suffix.lower()
    
    # Generate unique ID
    unique_id = uuid.uuid4().hex[:12]
    
    # Create safe base name (remove special chars, limit length)
    base_name = Path(original_filename).stem
    safe_base = "".join(c for c in base_name if c.isalnum() or c in "-_")[:50]
    
    return f"{safe_base}_{unique_id}{ext}"


def save_uploaded_file(file_content: bytes, original_filename: str) -> str:
    """
    Save an uploaded file to the uploads directory.
    
    Args:
        file_content: The binary content of the file
        original_filename: The original filename from the client
        
    Returns:
        The relative path to the saved file
    """
    upload_dir = get_upload_dir()
    
    # Generate safe unique filename
    safe_filename = generate_safe_filename(original_filename)
    file_path = upload_dir / safe_filename
    
    # Write the file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Return relative path from project root
    return f"uploads/{safe_filename}"


def validate_image_file(filename: str, content_type: Optional[str] = None) -> bool:
    """
    Validate that a file is an allowed image type.
    
    Args:
        filename: The filename to validate
        content_type: Optional content type to validate
        
    Returns:
        True if the file is a valid image type
    """
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
    
    ext = Path(filename).suffix.lower()
    if ext not in allowed_extensions:
        return False
    
    # Also check content type if provided
    if content_type:
        allowed_types = {
            "image/jpeg",
            "image/png", 
            "image/gif",
            "image/webp",
            "image/bmp",
        }
        if content_type not in allowed_types:
            return False
    
    return True


def get_file_size_limit() -> int:
    """Get the maximum allowed file size in bytes (10MB default)."""
    settings = get_settings()
    return settings.MAX_UPLOAD_SIZE