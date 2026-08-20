"""
Shared report-building logic used by both the CLI (run_report.py) and the
web API (backend/main.py), so the KPI -> insights -> email pipeline has a
single implementation instead of being reimplemented at each call site.
"""

from datetime import datetime

import pandas as pd

from ai_insights import generate_email_content_from_metrics, generate_metric_insights
from business_metrics import BusinessMetrics


def build_report(df: pd.DataFrame, title: str | None = None) -> dict:
    """Calculate KPIs, generate insights, and build the email content for them.

    Returns a dict with keys: kpis, insights, subject, html.
    """
    metrics = BusinessMetrics(df)
    kpis = metrics.calculate_kpis()
    insights = generate_metric_insights(kpis)

    title = title or f"Business Performance Report - {datetime.now().strftime('%B %d, %Y')}"
    content = generate_email_content_from_metrics(kpis, title, insights=insights)

    return {
        "kpis": kpis,
        "insights": insights,
        "subject": content["subject"],
        "html": content["body"],
    }
