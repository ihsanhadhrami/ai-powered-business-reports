"""
Unit tests for validators.py
"""

import pytest
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.validators import (
    ValidationError,
    validate_email,
    validate_email_list,
    validate_csv_data,
    validate_config,
    sanitize_html
)


class TestEmailValidation:
    """Test suite for email validation functions."""
    
    def test_valid_email(self, valid_emails):
        """Test validation of valid email addresses."""
        for email in valid_emails:
            assert validate_email(email) is True
    
    def test_invalid_email(self, invalid_emails):
        """Test validation of invalid email addresses."""
        for email in invalid_emails:
            with pytest.raises(ValidationError):
                validate_email(email)
    
    def test_validate_email_list_valid(self, valid_emails):
        """Test validation of valid email list."""
        result = validate_email_list(valid_emails)
        assert len(result) == len(valid_emails)
    
    def test_validate_email_list_empty(self):
        """Test validation of empty email list."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_email_list([])
    
    def test_validate_email_list_with_spaces(self):
        """Test email list with whitespace."""
        emails = ['  test@example.com  ', 'user@domain.com  ']
        result = validate_email_list(emails)
        assert result == ['test@example.com', 'user@domain.com']


class TestCSVDataValidation:
    """Test suite for CSV data validation."""
    
    def test_valid_dataframe(self, sample_dataframe):
        """Test validation of valid DataFrame."""
        result = validate_csv_data(sample_dataframe)
        assert len(result) == len(sample_dataframe)
    
    def test_empty_dataframe(self):
        """Test validation of empty DataFrame."""
        empty_df = pd.DataFrame()
        with pytest.raises(ValidationError, match="empty"):
            validate_csv_data(empty_df)
    
    def test_missing_required_column(self):
        """Test validation with missing required column."""
        df = pd.DataFrame({'Revenue': [100, 200]})
        with pytest.raises(ValidationError, match="Missing required columns"):
            validate_csv_data(df, required_columns=['Date', 'Revenue'])
    
    def test_invalid_date_format(self):
        """Test validation with invalid date format."""
        df = pd.DataFrame({
            'Date': ['not-a-date', 'also-not-date'],
            'Revenue': [100, 200]
        })
        with pytest.raises(ValidationError, match="Invalid date format"):
            validate_csv_data(df)
    
    def test_numeric_conversion(self):
        """Test automatic numeric conversion."""
        df = pd.DataFrame({
            'Date': [datetime.now()],
            'Revenue': ['1000']  # String that can be converted
        })
        result = validate_csv_data(df)
        assert pd.api.types.is_numeric_dtype(result['Revenue'])


class TestConfigValidation:
    """Test suite for configuration validation."""
    
    def test_valid_config(self):
        """Test validation of valid configuration."""
        config = {
            'email': 'actual@email.com',
            'api_key': 'sk-real-api-key-here',
            'server': 'smtp.gmail.com'
        }
        assert validate_config(config) is True
    
    def test_placeholder_email(self):
        """Test detection of placeholder email."""
        config = {
            'email': 'your-email@gmail.com'
        }
        with pytest.raises(ValidationError, match="placeholder"):
            validate_config(config)
    
    def test_nested_placeholder(self):
        """Test detection of nested placeholder values."""
        config = {
            'outer': {
                'inner': {
                    'key': 'your-password-here'
                }
            }
        }
        with pytest.raises(ValidationError, match="placeholder"):
            validate_config(config)


class TestHTMLSanitization:
    """Test suite for HTML sanitization."""
    
    def test_escape_html_tags(self):
        """Test escaping of HTML tags."""
        result = sanitize_html('<script>alert("xss")</script>')
        assert '<' not in result
        assert '>' not in result
        assert '&lt;' in result
        assert '&gt;' in result
    
    def test_escape_quotes(self):
        """Test escaping of quotes."""
        result = sanitize_html('He said "hello"')
        assert '"' not in result
        assert '&quot;' in result
    
    def test_escape_ampersand(self):
        """Test escaping of ampersand."""
        result = sanitize_html('Tom & Jerry')
        assert '&amp;' in result
    
    def test_non_string_input(self):
        """Test sanitization of non-string input."""
        result = sanitize_html(12345)
        assert result == '12345'
    
    def test_empty_string(self):
        """Test sanitization of empty string."""
        result = sanitize_html('')
        assert result == ''
