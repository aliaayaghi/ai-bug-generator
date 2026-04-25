"""Report CRUD API routes.

This module contains the API endpoints for creating, reading, listing,
and deleting bug reports. Routes are kept thin - they parse requests,
call the service, and return responses.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.repositories.report_repository import ReportRepository
from app.schemas.report_request import ReportCreate
from app.schemas.report_response import ReportResponse
from app.services.report_service import ReportService

router = APIRouter()


def get_report_service(db: Session = Depends(get_db)) -> ReportService:
    """Dependency that provides a ReportService instance.

    Args:
        db: Database session from dependency injection.

    Returns:
        Configured ReportService instance.
    """
    repository = ReportRepository(db)
    return ReportService(repository)


@router.post(
    "/reports",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["reports"],
)
def create_report(
    data: ReportCreate,
    service: ReportService = Depends(get_report_service),
) -> ReportResponse:
    """Create a new bug report.

    Args:
        data: Validated report creation data.
        service: Report service instance.

    Returns:
        The created report as a response schema.
    """
    return service.create_report(data)


@router.get(
    "/reports",
    response_model=list[ReportResponse],
    tags=["reports"],
)
def list_reports(
    service: ReportService = Depends(get_report_service),
    limit: int = 50,
    offset: int = 0,
) -> list[ReportResponse]:
    """List all bug reports with pagination.

    Args:
        service: Report service instance.
        limit: Maximum number of reports to return.
        offset: Number of reports to skip.

    Returns:
        List of reports as response schemas.
    """
    return service.list_reports(limit=limit, offset=offset)


@router.get(
    "/reports/{report_id}",
    response_model=ReportResponse,
    tags=["reports"],
)
def get_report(
    report_id: int,
    service: ReportService = Depends(get_report_service),
) -> ReportResponse:
    """Get a single bug report by ID.

    Args:
        report_id: The unique identifier of the report.
        service: Report service instance.

    Returns:
        The report as a response schema.

    Raises:
        HTTPException: 404 if report not found.
    """
    report = service.get_report(report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with id {report_id} not found",
        )
    return report


@router.delete(
    "/reports/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["reports"],
)
def delete_report(
    report_id: int,
    service: ReportService = Depends(get_report_service),
) -> None:
    """Delete a bug report by ID.

    Args:
        report_id: The unique identifier of the report to delete.
        service: Report service instance.

    Raises:
        HTTPException: 404 if report not found.
    """
    deleted = service.delete_report(report_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with id {report_id} not found",
        )