"""
Unit tests for business_metrics.py
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from business_metrics import BusinessMetrics


class TestBusinessMetrics:
    """Test suite for BusinessMetrics class."""
    
    def test_init_with_valid_data(self, sample_dataframe):
        """Test initialization with valid DataFrame."""
        metrics = BusinessMetrics(sample_dataframe)
        assert metrics.data is not None
        assert len(metrics.data) == 10
    
    def test_calculate_growth_rate_positive(self, sample_dataframe):
        """Test growth rate calculation with positive growth."""
        metrics = BusinessMetrics(sample_dataframe)
        growth = metrics.calculate_growth_rate('Revenue')
        assert isinstance(growth, float)
        assert growth > 0  # Data has increasing values
    
    def test_calculate_growth_rate_missing_column(self, sample_dataframe):
        """Test growth rate with non-existent column."""
        metrics = BusinessMetrics(sample_dataframe)
        growth = metrics.calculate_growth_rate('NonExistentColumn')
        assert growth == 0.0
    
    def test_calculate_moving_average(self, sample_dataframe):
        """Test moving average calculation."""
        metrics = BusinessMetrics(sample_dataframe)
        ma = metrics.calculate_moving_average('Revenue', window=3)
        assert ma is not None
        assert len(ma) == len(sample_dataframe)
    
    def test_calculate_moving_average_missing_column(self, sample_dataframe):
        """Test moving average with non-existent column."""
        metrics = BusinessMetrics(sample_dataframe)
        ma = metrics.calculate_moving_average('NonExistentColumn')
        assert ma is None
    
    def test_calculate_kpis_structure(self, sample_dataframe):
        """Test that calculate_kpis returns expected structure."""
        metrics = BusinessMetrics(sample_dataframe)
        kpis = metrics.calculate_kpis()
        
        assert isinstance(kpis, dict)
        assert 'total_revenue' in kpis
        assert 'avg_daily_revenue' in kpis
        assert 'revenue_growth' in kpis
    
    def test_calculate_kpis_values(self, sample_dataframe):
        """Test that KPI values are calculated correctly."""
        metrics = BusinessMetrics(sample_dataframe)
        kpis = metrics.calculate_kpis()
        
        # Verify total_revenue is sum of Revenue column
        expected_total = sample_dataframe['Revenue'].sum()
        assert kpis['total_revenue'] == pytest.approx(expected_total)
        
        # Verify average is correct
        expected_avg = sample_dataframe['Revenue'].mean()
        assert kpis['avg_daily_revenue'] == pytest.approx(expected_avg)
    
    def test_generate_summary_html(self, sample_dataframe):
        """Test HTML summary generation."""
        metrics = BusinessMetrics(sample_dataframe)
        html = metrics.generate_summary_html()
        
        assert isinstance(html, str)
        assert 'kpi-container' in html
        assert 'kpi-grid' in html
    
    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        empty_df = pd.DataFrame(columns=['Date', 'Revenue'])
        metrics = BusinessMetrics(empty_df)
        kpis = metrics.calculate_kpis()
        
        # Should return empty or zero values, not crash
        assert isinstance(kpis, dict)
    
    def test_single_row_dataframe(self):
        """Test with single row DataFrame."""
        single_row = pd.DataFrame({
            'Date': [datetime.now()],
            'Revenue': [1000.0],
            'Sales': [50]
        })
        metrics = BusinessMetrics(single_row)
        kpis = metrics.calculate_kpis()
        
        assert kpis['total_revenue'] == 1000.0


class TestGrowthRateEdgeCases:
    """Test edge cases for growth rate calculation."""
    
    def test_zero_previous_value(self):
        """Test growth rate when previous value is zero."""
        df = pd.DataFrame({
            'Date': [datetime.now() - timedelta(days=1), datetime.now()],
            'Revenue': [0, 100]
        })
        metrics = BusinessMetrics(df)
        growth = metrics.calculate_growth_rate('Revenue')
        assert growth == float('inf')
    
    def test_both_zero_values(self):
        """Test growth rate when both values are zero."""
        df = pd.DataFrame({
            'Date': [datetime.now() - timedelta(days=1), datetime.now()],
            'Revenue': [0, 0]
        })
        metrics = BusinessMetrics(df)
        growth = metrics.calculate_growth_rate('Revenue')
        assert growth == 0.0
    
    def test_negative_growth(self):
        """Test negative growth rate calculation."""
        df = pd.DataFrame({
            'Date': [datetime.now() - timedelta(days=1), datetime.now()],
            'Revenue': [200, 100]
        })
        metrics = BusinessMetrics(df)
        growth = metrics.calculate_growth_rate('Revenue')
        assert growth == -50.0
