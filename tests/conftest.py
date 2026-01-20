"""
Test configuration and fixtures for pytest
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    dates = [datetime.now() - timedelta(days=x) for x in range(10, 0, -1)]
    return pd.DataFrame({
        'Date': dates,
        'Revenue': [1000 + i * 100 for i in range(10)],
        'Sales': [50 + i * 5 for i in range(10)],
        'Customer_Count': [100 + i * 10 for i in range(10)]
    })


@pytest.fixture
def sample_kpis():
    """Sample KPIs dictionary for testing."""
    return {
        'total_revenue': 14500.0,
        'avg_daily_revenue': 1450.0,
        'revenue_growth': 10.0,
        'total_sales': 725.0,
        'avg_daily_sales': 72.5,
        'sales_growth': 5.56,
        'total_customers': 1450.0,
        'avg_daily_customers': 145.0,
        'customer_growth': 11.11,
        'avg_revenue_per_customer': 10.0
    }


@pytest.fixture
def valid_emails():
    """List of valid email addresses."""
    return [
        'test@example.com',
        'user.name@company.org',
        'admin@subdomain.domain.com'
    ]


@pytest.fixture
def invalid_emails():
    """List of invalid email addresses."""
    return [
        'not-an-email',
        '@missing-local.com',
        'missing-domain@',
        'spaces in@email.com'
    ]
