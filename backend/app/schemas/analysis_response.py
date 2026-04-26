"""Response schema for AI analysis endpoint."""
from typing import Optional

from pydantic import BaseModel, Field


class AnalysisResponse(BaseModel):
    """Response schema for AI-analyzed bug report suggestion.
    
    This represents the structured bug report generated from analyzing
    a screenshot using AI vision capabilities.
    
    Attributes:
        title: Suggested title for the bug report.
        summary: Brief summary of the issue observed in the screenshot.
        severity: Suggested severity level (low, medium, high, critical).
        reproduction_steps: Suggested steps to reproduce the issue as a string.
        expected_behavior: What should have happened.
        actual_behavior: What actually happened (observed in screenshot).
        suspected_area: Suspected area/component where the issue lies.
        confidence: Confidence score of the analysis (0-100).
    """
    
    title: str = Field(..., description="Suggested title for the bug report")
    summary: str = Field(..., description="Brief summary of the issue")
    severity: str = Field(
        ...,
        description="Suggested severity: low, medium, high, or critical"
    )
    reproduction_steps: str = Field(
        default="",
        description="Suggested steps to reproduce the issue"
    )
    expected_behavior: str = Field(
        ...,
        description="What should have happened"
    )
    actual_behavior: str = Field(
        ...,
        description="What actually happened (observed in screenshot)"
    )
    suspected_area: str = Field(
        ...,
        description="Suspected area/component where the issue lies"
    )
    confidence: int = Field(
        ...,
        ge=0,
        le=100,
        description="Confidence score of the analysis (0-100)"
    )