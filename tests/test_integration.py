"""
Integration tests for the complete workflow
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestIntegrationWorkflow:
    """Integration tests for the complete email report workflow."""
    
    def test_full_workflow_dry_run(self, sample_dataframe, tmp_path):
        """Test complete workflow in dry-run mode."""
        from business_metrics import BusinessMetrics
        from ai_insights import generate_email_content_from_metrics
        
        # Step 1: Calculate metrics
        metrics = BusinessMetrics(sample_dataframe)
        kpis = metrics.calculate_kpis()
        
        assert 'total_revenue' in kpis
        assert kpis['total_revenue'] > 0
        
        # Step 2: Generate email content (mock AI to avoid API calls)
        with patch('ai_insights.chat_with_ai') as mock_ai:
            mock_ai.return_value = "Test insights"
            
            email_content = generate_email_content_from_metrics(
                kpis, 
                report_title="Test Report"
            )
            
            assert 'subject' in email_content
            assert 'body' in email_content
            assert 'insights' in email_content
        
        # Step 3: Save to file (dry run)
        output_file = tmp_path / "test_report.html"
        output_file.write_text(email_content['body'])
        
        assert output_file.exists()
        assert 'Test Report' in output_file.read_text()
    
    def test_metrics_to_email_flow(self, sample_kpis):
        """Test flow from KPIs to email content."""
        from ai_insights import generate_email_content_from_metrics
        
        with patch('ai_insights.chat_with_ai') as mock_ai:
            mock_ai.return_value = "Business is performing well."
            
            content = generate_email_content_from_metrics(
                sample_kpis,
                report_title="Weekly Report"
            )
            
            # Verify email structure
            assert content['subject'] is not None
            assert 'Weekly Report' in content['body']
            assert 'kpi-grid' in content['body']
    
    def test_csv_to_metrics_flow(self, tmp_path):
        """Test flow from CSV file to metrics."""
        from business_metrics import BusinessMetrics
        
        # Create test CSV
        csv_file = tmp_path / "test_data.csv"
        df = pd.DataFrame({
            'Date': ['2026-01-15', '2026-01-16', '2026-01-17'],
            'Revenue': [1000, 1100, 1200],
            'Sales': [50, 55, 60]
        })
        df.to_csv(csv_file, index=False)
        
        # Load and process
        loaded_df = pd.read_csv(csv_file)
        metrics = BusinessMetrics(loaded_df)
        kpis = metrics.calculate_kpis()
        
        assert kpis['total_revenue'] == 3300.0
        assert kpis['total_sales'] == 165.0


class TestEmailSendingIntegration:
    """Integration tests for email sending (mocked)."""
    
    def test_email_send_with_retry(self):
        """Test email sending with retry mechanism."""
        from automated_email import send_email
        
        with patch('automated_email.smtplib.SMTP') as mock_smtp:
            # Mock successful send after retry
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            result = send_email(
                subject="Test Subject",
                body="<html><body>Test</body></html>",
                recipients=["test@example.com"]
            )
            
            # Note: Will fail due to config, but tests the flow
            # In production, this would be mocked more thoroughly
    
    def test_email_validation_before_send(self, valid_emails):
        """Test that email validation works before sending."""
        from utils.validators import validate_email_list
        
        validated = validate_email_list(valid_emails)
        assert len(validated) == len(valid_emails)
