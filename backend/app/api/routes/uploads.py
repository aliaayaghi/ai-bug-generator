"""Upload API routes."""
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.services.file_storage import (
    get_file_size_limit,
    save_uploaded_file,
    validate_image_file,
)

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> JSONResponse:
    """
    Upload an image file.
    
    Accepts image files only (jpg, jpeg, png, gif, webp, bmp).
    Max file size: 10MB.
    
    Returns:
        JSON with file_path, original_filename, and content_type
    """
    # Check content type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image (jpg, jpeg, png, gif, webp, or bmp)"
        )
    
    # Validate file extension
    if not validate_image_file(file.filename, file.content_type):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only image files are allowed."
        )
    
    # Check file size
    max_size = get_file_size_limit()
    contents = await file.read()
    
    if len(contents) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {max_size // (1024 * 1024)}MB."
        )
    
    if len(contents) == 0:
        raise HTTPException(
            status_code=400,
            detail="Empty file uploaded."
        )
    
    # Save the file
    try:
        file_path = save_uploaded_file(contents, file.filename)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )
    
    return JSONResponse({
        "file_path": file_path,
        "original_filename": file.filename,
        "content_type": file.content_type,
    })