"""Analysis API routes for AI-powered screenshot analysis."""
from fastapi import APIRouter, HTTPException

from app.schemas.analysis_request import AnalysisRequest
from app.schemas.analysis_response import AnalysisResponse
from app.services.ai_analyzer import get_analyzer

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_screenshot(request: AnalysisRequest) -> AnalysisResponse:
    """
    Analyze a screenshot using AI to generate a bug report suggestion.
    
    This endpoint takes an image path (from a previously uploaded file),
    optionally user notes and page URL, then uses AI vision to analyze
    the screenshot and return structured bug report fields.
    
    Args:
        request: AnalysisRequest with image_path and optional context.
        
    Returns:
        AnalysisResponse with structured bug report suggestion.
        
    Raises:
        HTTPException 404: If the image file doesn't exist.
        HTTPException 400: If the file is not a valid image.
        HTTPException 500: If AI analysis fails.
    """
    try:
        analyzer = get_analyzer()
        result = analyzer.analyze(
            image_path=request.image_path,
            user_note=request.user_note,
            page_url=request.page_url,
        )
        return result
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IOError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")