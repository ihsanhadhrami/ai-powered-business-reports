"""
Input Validation Utilities
Provides validation functions for data integrity and security.
"""

import re
import pandas as pd
from typing import List, Optional, Dict, Any
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_email(email: str) -> bool:
    """
    Validate an email address format.
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid, raises ValidationError if invalid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError(f"Invalid email format: {email}")
    return True


def validate_email_list(emails: List[str]) -> List[str]:
    """
    Validate a list of email addresses.
    
    Args:
        emails: List of email addresses
    
    Returns:
        List of valid emails
    
    Raises:
        ValidationError if any email is invalid
    """
    if not emails:
        raise ValidationError("Email list cannot be empty")
    
    valid_emails = []
    for email in emails:
        email = email.strip()
        if validate_email(email):
            valid_emails.append(email)
    
    return valid_emails


def validate_csv_data(df: pd.DataFrame, required_columns: List[str] = None) -> pd.DataFrame:
    """
    Validate CSV data for required columns and data integrity.
    
    Args:
        df: Pandas DataFrame to validate
        required_columns: List of required column names
    
    Returns:
        Validated DataFrame
    
    Raises:
        ValidationError if validation fails
    """
    required_columns = required_columns or ['Date']
    
    # Check for empty DataFrame
    if df.empty:
        raise ValidationError("DataFrame is empty")
    
    # Check required columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValidationError(f"Missing required columns: {missing_columns}")
    
    # Validate Date column format
    if 'Date' in df.columns:
        try:
            df['Date'] = pd.to_datetime(df['Date'])
        except Exception as e:
            raise ValidationError(f"Invalid date format in 'Date' column: {e}")
    
    # Check for numeric columns and validate
    numeric_columns = ['Revenue', 'Sales', 'Customer_Count', 'Orders', 'Returns']
    for col in numeric_columns:
        if col in df.columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except Exception:
                    logger.warning(f"Could not convert column '{col}' to numeric")
    
    logger.info(f"Validated DataFrame with {len(df)} rows and {len(df.columns)} columns")
    return df


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration settings.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        True if valid
    
    Raises:
        ValidationError if invalid
    """
    # Check for placeholder values
    placeholder_patterns = [
        'your-email',
        'your-password',
        'your-api-key',
        'example.com',
        'placeholder'
    ]
    
    def check_value(value: Any, key: str):
        if isinstance(value, str):
            value_lower = value.lower()
            for pattern in placeholder_patterns:
                if pattern in value_lower:
                    raise ValidationError(
                        f"Configuration '{key}' contains placeholder value. "
                        "Please update with actual credentials."
                    )
    
    def recursive_check(d: Dict, prefix: str = ''):
        for key, value in d.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                recursive_check(value, full_key)
            else:
                check_value(value, full_key)
    
    recursive_check(config)
    return True


def sanitize_html(text: str) -> str:
    """
    Sanitize text for safe HTML insertion.
    
    Args:
        text: Text to sanitize
    
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Escape HTML special characters
    replacements = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    return text
