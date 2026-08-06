"""Pydantic request/response models for the report web API."""

from typing import Dict, List, Optional

from pydantic import BaseModel


class ConfigResponse(BaseModel):
    report_frequency: str
    report_time: str
    ai_enabled: bool
    email_configured: bool


class DataInfoResponse(BaseModel):
    rows: int
    columns: List[str]
    date_min: str
    date_max: str


class ReportPreviewResponse(BaseModel):
    kpis: Dict[str, float]
    insights: str
    subject: str
    html: str


class SendReportRequest(BaseModel):
    recipients: Optional[List[str]] = None


class SendReportResponse(BaseModel):
    success: bool
    message: str


class ChartResponse(BaseModel):
    column: str
    dates: List[str]
    values: List[float]
    moving_average: List[float]
