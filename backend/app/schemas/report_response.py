"""Pydantic schemas for report responses."""

from datetime import datetime

from pydantic import BaseModel, Field


class ReportResponse(BaseModel):
    """Schema for returning a bug report to the frontend.
    
    This is the output schema used when sending report data
    to the client. It includes all stored fields plus the
    auto-generated ID and timestamp.
    """

    id: int = Field(
        description="Unique identifier for the report"
    )
    image_path: str = Field(
        description="Path or URL to the uploaded screenshot"
    )
    user_note: str | None = Field(
        default=None,
        description="Optional user-provided note or context"
    )
    page_url: str | None = Field(
        default=None,
        description="URL of the page where the bug was found"
    )
    title: str = Field(
        description="Brief title describing the bug"
    )
    summary: str = Field(
        description="AI-generated or manual summary of the issue"
    )
    severity: str = Field(
        description="Severity level: critical, high, medium, low, or info"
    )
    reproduction_steps: str | None = Field(
        default=None,
        description="Steps to reproduce the bug"
    )
    expected_behavior: str = Field(
        description="What should have happened"
    )
    actual_behavior: str = Field(
        description="What actually happened"
    )
    suspected_area: str | None = Field(
        default=None,
        description="Suspected area or component causing the issue"
    )
    confidence: float | None = Field(
        default=None,
        description="AI confidence score (0.0 to 1.0)"
    )
    created_at: datetime = Field(
        description="Timestamp when the report was created"
    )

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "image_path": "/uploads/screenshot.png",
                "user_note": "Found on the login page",
                "page_url": "https://example.com/login",
                "title": "Submit button not responding",
                "summary": "The submit button on the login form does not respond to clicks.",
                "severity": "high",
                "reproduction_steps": "1. Navigate to login page\n2. Enter credentials\n3. Click submit",
                "expected_behavior": "Form should submit and redirect to dashboard",
                "actual_behavior": "Button shows no response to click",
                "suspected_area": "Login form component",
                "confidence": 0.85,
                "created_at": "2026-04-24T10:30:00Z"
            }
        }
    }