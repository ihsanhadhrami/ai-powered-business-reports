"""
Unit tests for retry mechanism
"""

import pytest
import time
import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.retry import retry_with_backoff, RetryContext


class TestRetryWithBackoff:
    """Test suite for retry_with_backoff decorator."""
    
    def test_successful_first_attempt(self):
        """Test function that succeeds on first attempt."""
        mock_func = Mock(return_value="success")
        
        @retry_with_backoff(max_retries=3)
        def test_func():
            return mock_func()
        
        result = test_func()
        assert result == "success"
        assert mock_func.call_count == 1
    
    def test_retry_on_exception(self):
        """Test retry behavior on exception."""
        call_count = 0
        
        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Failed")
            return "success"
        
        result = test_func()
        assert result == "success"
        assert call_count == 3
    
    def test_max_retries_exceeded(self):
        """Test that exception is raised after max retries."""
        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def always_fails():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError, match="Always fails"):
            always_fails()
    
    def test_specific_exception_retry(self):
        """Test retry only for specific exceptions."""
        call_count = 0
        
        @retry_with_backoff(
            max_retries=3,
            base_delay=0.01,
            exceptions=(ConnectionError,)
        )
        def test_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("Connection failed")
            return "success"
        
        result = test_func()
        assert result == "success"
        assert call_count == 2
    
    def test_non_matching_exception_not_retried(self):
        """Test that non-matching exceptions are not retried."""
        @retry_with_backoff(
            max_retries=3,
            base_delay=0.01,
            exceptions=(ConnectionError,)
        )
        def raises_value_error():
            raise ValueError("Different error")
        
        with pytest.raises(ValueError):
            raises_value_error()
    
    def test_on_retry_callback(self):
        """Test that on_retry callback is called."""
        callback = Mock()
        call_count = 0
        
        @retry_with_backoff(
            max_retries=2,
            base_delay=0.01,
            on_retry=callback
        )
        def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Retry")
            return "success"
        
        test_func()
        assert callback.call_count == 2


class TestRetryContext:
    """Test suite for RetryContext manager."""
    
    def test_successful_first_attempt(self):
        """Test context manager with successful first attempt."""
        with RetryContext(max_retries=3) as retry:
            attempts = 0
            while retry.should_continue():
                attempts += 1
                break  # Success on first try
        
        assert attempts == 1
    
    def test_retry_until_success(self):
        """Test retry until success."""
        attempts = 0
        
        with RetryContext(max_retries=3, base_delay=0.01) as retry:
            while retry.should_continue():
                attempts += 1
                try:
                    if attempts < 3:
                        raise Exception("Fail")
                    break  # Success
                except Exception as e:
                    retry.handle_exception(e)
        
        assert attempts == 3
    
    def test_max_retries_exceeded_raises(self):
        """Test that max retries exceeded raises exception."""
        with pytest.raises(Exception, match="Always fails"):
            with RetryContext(max_retries=2, base_delay=0.01) as retry:
                while retry.should_continue():
                    try:
                        raise Exception("Always fails")
                    except Exception as e:
                        retry.handle_exception(e)
