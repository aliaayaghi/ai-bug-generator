"""Repository for Report database access."""

from datetime import datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.report import Report


class ReportRepository:
    """Handles database operations for bug reports."""

    def __init__(self, session: Session):
        """Initialize with a database session.
        
        Args:
            session: SQLAlchemy session for database operations.
        """
        self._session = session

    def create(
        self,
        image_path: str,
        title: str,
        summary: str,
        severity: str,
        expected_behavior: str,
        actual_behavior: str,
        user_note: str | None = None,
        page_url: str | None = None,
        reproduction_steps: str | None = None,
        suspected_area: str | None = None,
        confidence: float | None = None,
    ) -> Report:
        """Create a new bug report in the database.
        
        Args:
            image_path: Path to the uploaded screenshot.
            title: Brief title describing the bug.
            summary: AI-generated or manual summary.
            severity: Severity level (critical, high, medium, low, info).
            expected_behavior: What should have happened.
            actual_behavior: What actually happened.
            user_note: Optional user-provided note.
            page_url: Optional URL where the bug was found.
            reproduction_steps: Optional steps to reproduce.
            suspected_area: Optional suspected area causing the issue.
            confidence: Optional AI confidence score (0.0 to 1.0).
            
        Returns:
            The created Report instance.
        """
        report = Report(
            image_path=image_path,
            title=title,
            summary=summary,
            severity=severity,
            expected_behavior=expected_behavior,
            actual_behavior=actual_behavior,
            user_note=user_note,
            page_url=page_url,
            reproduction_steps=reproduction_steps,
            suspected_area=suspected_area,
            confidence=confidence,
            created_at=datetime.utcnow(),
        )
        self._session.add(report)
        self._session.commit()
        self._session.refresh(report)
        return report

    def get_by_id(self, report_id: int) -> Report | None:
        """Retrieve a report by its ID.
        
        Args:
            report_id: The unique identifier of the report.
            
        Returns:
            The Report if found, None otherwise.
        """
        stmt = select(Report).where(Report.id == report_id)
        return self._session.execute(stmt).scalar_one_or_none()

    def list_reports(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Report]:
        """List reports with pagination.
        
        Args:
            limit: Maximum number of reports to return.
            offset: Number of reports to skip (for pagination).
            
        Returns:
            List of Report instances ordered by creation date (newest first).
        """
        stmt = (
            select(Report)
            .order_by(Report.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self._session.execute(stmt).scalars().all())

    def delete(self, report_id: int) -> bool:
        """Delete a report by its ID.
        
        Args:
            report_id: The unique identifier of the report to delete.
            
        Returns:
            True if the report was deleted, False if not found.
        """
        report = self.get_by_id(report_id)
        if report is None:
            return False
        
        self._session.delete(report)
        self._session.commit()
        return True