"""
Integration tests for the FastAPI web backend.

Mirrors the mocking conventions used in tests/test_integration.py (patch
automated_email.send_email rather than hitting real SMTP/AI services).
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import config
from backend.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _reset_data_source():
    """Ensure uploads in one test don't leak into others."""
    original_path = config.DATA_SOURCE.get("path")
    yield
    config.DATA_SOURCE["path"] = original_path


class TestHealthAndConfig:
    def test_health(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_config(self):
        response = client.get("/api/config")
        assert response.status_code == 200
        body = response.json()
        assert body["report_frequency"] == config.REPORT_FREQUENCY
        assert body["report_time"] == config.REPORT_TIME
        assert "ai_enabled" in body
        assert "email_configured" in body


class TestApiKeyAuth:
    def test_public_when_token_unset(self):
        assert config.API_AUTH_TOKEN == ""
        response = client.get("/api/config")
        assert response.status_code == 200

    def test_rejects_missing_key_when_token_set(self, monkeypatch):
        monkeypatch.setattr(config, "API_AUTH_TOKEN", "secret123")
        response = client.get("/api/config")
        assert response.status_code == 401

    def test_accepts_correct_key_when_token_set(self, monkeypatch):
        monkeypatch.setattr(config, "API_AUTH_TOKEN", "secret123")
        response = client.get("/api/config", headers={"X-API-Key": "secret123"})
        assert response.status_code == 200


class TestDataEndpoints:
    def test_get_data_uses_sample_csv(self):
        response = client.get("/api/data")
        assert response.status_code == 200
        body = response.json()
        assert body["rows"] > 0
        assert "Revenue" in body["columns"]

    def test_upload_rejects_non_csv(self):
        response = client.post(
            "/api/data/upload",
            files={"file": ("data.txt", b"not,a,csv", "text/plain")},
        )
        assert response.status_code == 400

    def test_upload_rejects_invalid_data(self):
        bad_csv = b"Date,Revenue\nnot-a-date,100\n"
        response = client.post(
            "/api/data/upload",
            files={"file": ("bad.csv", bad_csv, "text/csv")},
        )
        assert response.status_code == 422

    def test_upload_accepts_valid_csv(self):
        good_csv = b"Date,Revenue,Sales\n2026-01-01,1000,50\n2026-01-02,1100,55\n"
        response = client.post(
            "/api/data/upload",
            files={"file": ("good.csv", good_csv, "text/csv")},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["rows"] == 2
        assert set(body["columns"]) == {"Revenue", "Sales"}


class TestChartEndpoint:
    def test_unknown_column_rejected(self):
        response = client.get("/api/charts/NotAColumn")
        assert response.status_code == 404

    def test_valid_column(self):
        response = client.get("/api/charts/Revenue")
        assert response.status_code == 200
        body = response.json()
        assert len(body["dates"]) == len(body["values"]) == len(body["moving_average"])
        assert len(body["values"]) > 0


class TestReportEndpoints:
    def test_preview_report(self):
        response = client.get("/api/reports/preview")
        assert response.status_code == 200
        body = response.json()
        assert "total_revenue" in body["kpis"]
        assert body["subject"]
        assert "kpi-grid" in body["html"]

    def test_send_report_success(self):
        with patch("backend.main.send_email", return_value=True) as mock_send:
            response = client.post("/api/reports/send", json={})
            assert response.status_code == 200
            assert response.json()["success"] is True
            mock_send.assert_called_once()

    def test_send_report_failure_returns_502(self):
        with patch("backend.main.send_email", return_value=False):
            response = client.post("/api/reports/send", json={})
            assert response.status_code == 502

    def test_send_report_with_recipient_override(self):
        with patch("backend.main.send_email", return_value=True) as mock_send:
            response = client.post(
                "/api/reports/send", json={"recipients": ["custom@example.com"]}
            )
            assert response.status_code == 200
            _, kwargs = mock_send.call_args
            assert kwargs["recipients"] == ["custom@example.com"]
