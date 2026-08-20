"""
FastAPI backend for the web front end.

Wraps the existing report-generation modules (business_metrics.py,
ai_insights.py, automated_email.py, config.py, utils/) unchanged and exposes
them over HTTP so a browser-based UI can drive the same pipeline the CLI
(run_report.py) uses.
"""

import io
import sys
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import pandas as pd
from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

import config
from ai_insights import ai_enabled
from automated_email import send_email
from business_metrics import BusinessMetrics
from report_builder import build_report
from run_report import load_data_from_csv
from utils.logger import setup_logger
from utils.validators import ValidationError, validate_csv_data

from backend.schemas import (
    ChartResponse,
    ConfigResponse,
    DataInfoResponse,
    ReportPreviewResponse,
    SendReportRequest,
    SendReportResponse,
)

logger = setup_logger(__name__)

app = FastAPI(title="Business Reports API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

CHART_COLUMNS = {"Revenue", "Sales", "Customer_Count"}
UPLOAD_PATH = REPO_ROOT / "data" / "uploaded.csv"


def require_api_key(x_api_key: Optional[str] = Header(default=None)) -> None:
    token = config.API_AUTH_TOKEN
    if token and x_api_key != token:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def _load_current_dataframe() -> pd.DataFrame:
    csv_path = config.DATA_SOURCE.get("path", "data/sample_data.csv")
    df = load_data_from_csv(csv_path)
    if df is None:
        raise HTTPException(
            status_code=400,
            detail=f"No valid data available at '{csv_path}'. Upload a CSV or check the configured data source.",
        )
    return df


def _data_info(df: pd.DataFrame) -> DataInfoResponse:
    return DataInfoResponse(
        rows=len(df),
        columns=[col for col in df.columns if col != "Date"],
        date_min=str(df["Date"].min().date()),
        date_max=str(df["Date"].max().date()),
    )


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/config", response_model=ConfigResponse)
def get_config(_: None = Depends(require_api_key)) -> ConfigResponse:
    return ConfigResponse(
        report_frequency=config.REPORT_FREQUENCY,
        report_time=config.REPORT_TIME,
        ai_enabled=ai_enabled(),
        email_configured=bool(config.EMAIL_SENDER and config.EMAIL_PASSWORD),
    )


@app.get("/api/data", response_model=DataInfoResponse)
def get_data(_: None = Depends(require_api_key)) -> DataInfoResponse:
    return _data_info(_load_current_dataframe())


@app.post("/api/data/upload", response_model=DataInfoResponse)
async def upload_data(
    file: UploadFile = File(...), _: None = Depends(require_api_key)
) -> DataInfoResponse:
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted")

    raw = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(raw))
        df = validate_csv_data(df, required_columns=["Date"])
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {e}") from e

    UPLOAD_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(UPLOAD_PATH, index=False)
    config.DATA_SOURCE["path"] = str(UPLOAD_PATH)
    logger.info("Uploaded new data source: %s (%d rows)", UPLOAD_PATH, len(df))

    return _data_info(df)


@app.get("/api/charts/{column}", response_model=ChartResponse)
def get_chart(column: str, _: None = Depends(require_api_key)) -> ChartResponse:
    if column not in CHART_COLUMNS:
        raise HTTPException(status_code=404, detail=f"Unknown chart column: {column}")

    df = _load_current_dataframe()
    metrics = BusinessMetrics(df)
    if column not in metrics.data.columns:
        raise HTTPException(status_code=404, detail=f"Column '{column}' is not present in the current data")

    moving_average = metrics.calculate_moving_average(column)
    return ChartResponse(
        column=column,
        dates=[d.strftime("%Y-%m-%d") for d in metrics.data["Date"]],
        values=[float(v) for v in metrics.data[column]],
        moving_average=[float(v) for v in moving_average],
    )


@app.get("/api/reports/preview", response_model=ReportPreviewResponse)
def preview_report(_: None = Depends(require_api_key)) -> ReportPreviewResponse:
    df = _load_current_dataframe()
    return ReportPreviewResponse(**build_report(df))


@app.post("/api/reports/send", response_model=SendReportResponse)
def send_report(
    payload: SendReportRequest = SendReportRequest(), _: None = Depends(require_api_key)
) -> SendReportResponse:
    df = _load_current_dataframe()
    report = build_report(df)

    success = send_email(
        subject=report["subject"],
        body=report["html"],
        recipients=payload.recipients or None,
    )

    if not success:
        raise HTTPException(
            status_code=502,
            detail="Failed to send email. Check backend logs and SMTP configuration.",
        )

    recipient_count = len(payload.recipients or config.EMAIL_RECIPIENTS)
    return SendReportResponse(success=True, message=f"Report sent to {recipient_count} recipient(s).")
