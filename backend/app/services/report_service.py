"""Service layer for bug report operations.

This module contains the ReportService which orchestrates report-related
workflows. It acts as an intermediary between API routes and the repository,
keeping business logic out of routes while making it easy to extend for
future features like file uploads and AI analysis.
"""

from typing import List

from app.repositories.report_repository import ReportRepository
from app.schemas.report_request import ReportCreate
from app.schemas.report_response import ReportResponse


class ReportService:
    """Orchestrates bug report operations.

    This service wraps repository actions and provides a clean interface
    for the API layer. It handles the translation between Pydantic schemas
    and repository calls.
    """

    def __init__(self, repository: ReportRepository):
        """Initialize with a repository instance.

        Args:
            repository: The report repository for database operations.
        """
        self._repository = repository

    def create_report(self, data: ReportCreate) -> ReportResponse:
        """Create a new bug report from validated input data.

        Args:
            data: Validated report creation data.

        Returns:
            The created report as a response schema.
        """
        report = self._repository.create(
            image_path=data.image_path,
            title=data.title,
            summary=data.summary,
            severity=data.severity,
            expected_behavior=data.expected_behavior,
            actual_behavior=data.actual_behavior,
            user_note=data.user_note,
            page_url=data.page_url,
            reproduction_steps=data.reproduction_steps,
            suspected_area=data.suspected_area,
            confidence=data.confidence,
        )
        return ReportResponse.model_validate(report)

    def get_report(self, report_id: int) -> ReportResponse | None:
        """Retrieve a single report by ID.

        Args:
            report_id: The unique identifier of the report.

        Returns:
            The report as a response schema, or None if not found.
        """
        report = self._repository.get_by_id(report_id)
        if report is None:
            return None
        return ReportResponse.model_validate(report)

    def list_reports(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ReportResponse]:
        """List reports with pagination.

        Args:
            limit: Maximum number of reports to return.
            offset: Number of reports to skip.

        Returns:
            List of reports as response schemas.
        """
        reports = self._repository.list_reports(limit=limit, offset=offset)
        return [ReportResponse.model_validate(r) for r in reports]

    def delete_report(self, report_id: int) -> bool:
        """Delete a report by ID.

        Args:
            report_id: The unique identifier of the report to delete.

        Returns:
            True if the report was deleted, False if not found.
        """
        return self._repository.delete(report_id)