"""
Tests for APIAgent.

Day 4 Session 2 - Simple tests, ~20 total.
Mock time.sleep() for fast tests.
"""

import pytest
from unittest.mock import patch
from api_agent import APIAgent


@pytest.fixture
def agent():
    """Create agent instance."""
    return APIAgent()


# =============================================================================
# HAPPY PATH TESTS (6)
# =============================================================================

class TestHappyPath:
    """Tests for normal operation."""

    def test_get_users(self, agent):
        """GET users returns user list."""
        result = agent.get("https://api.example.com/users")
        assert result["status"] == 200
        assert result["users"] == ["alice", "bob"]

    def test_get_posts(self, agent):
        """GET posts returns empty list."""
        result = agent.get("https://api.example.com/posts")
        assert result["status"] == 200
        assert result["posts"] == []

    def test_get_unknown_url(self, agent):
        """GET unknown URL returns 404."""
        result = agent.get("https://api.example.com/unknown")
        assert result["status"] == 404
        assert "error" in result

    def test_post_creates_user(self, agent):
        """POST echoes data with 201."""
        data = {"name": "charlie"}
        result = agent.post("https://api.example.com/users", data)
        assert result["status"] == 201
        assert result["created"] == data

    def test_post_unknown_url(self, agent):
        """POST unknown URL returns 404."""
        result = agent.post("https://api.example.com/unknown", {"data": "test"})
        assert result["status"] == 404

    def test_verify_passes(self, agent):
        """Self-test succeeds."""
        result = agent.verify()
        assert result["status"] == "PASS"
        assert result["tests_passed"] == result["tests_run"]


# =============================================================================
# RETRY LOGIC TESTS (6)
# =============================================================================

class TestRetryLogic:
    """Tests for retry with exponential backoff."""

    @patch('api_agent.time.sleep')
    def test_retry_get_success(self, mock_sleep, agent):
        """Retry succeeds on working endpoint."""
        result = agent.retry_request("GET", "https://api.example.com/users")
        assert result["status"] == 200
        mock_sleep.assert_not_called()  # No retries needed

    @patch('api_agent.time.sleep')
    def test_retry_flaky_succeeds(self, mock_sleep, agent):
        """Retry succeeds after 2 failures on flaky endpoint."""
        agent.reset_flaky()
        result = agent.retry_request("GET", "https://api.example.com/flaky", max_retries=3)
        assert result["status"] == 200
        assert mock_sleep.call_count == 2  # Slept twice before success

    @patch('api_agent.time.sleep')
    def test_retry_exhausted(self, mock_sleep, agent):
        """All retries fail raises error."""
        with pytest.raises(ConnectionError):
            agent.retry_request("GET", "https://api.example.com/error", max_retries=3)
        assert mock_sleep.call_count == 2  # Slept between attempts

    @patch('api_agent.time.sleep')
    def test_retry_post_success(self, mock_sleep, agent):
        """Retry works with POST."""
        result = agent.retry_request("POST", "https://api.example.com/users", data={"name": "test"})
        assert result["status"] == 201
        mock_sleep.assert_not_called()

    @patch('api_agent.time.sleep')
    def test_retry_respects_max(self, mock_sleep, agent):
        """Honors max_retries parameter."""
        with pytest.raises(ConnectionError):
            agent.retry_request("GET", "https://api.example.com/error", max_retries=5)
        assert mock_sleep.call_count == 4  # 5 attempts = 4 sleeps

    def test_retry_unknown_method(self, agent):
        """Raises ValueError for unknown method."""
        with pytest.raises(ValueError, match="Unknown method"):
            agent.retry_request("DELETE", "https://api.example.com/users")


# =============================================================================
# ERROR HANDLING TESTS (5)
# =============================================================================

class TestErrorHandling:
    """Tests for error handling."""

    def test_get_none_url(self, agent):
        """ValueError for None url."""
        with pytest.raises(ValueError, match="url cannot be None"):
            agent.get(None)

    def test_get_non_string_url(self, agent):
        """ValueError for int url."""
        with pytest.raises(ValueError, match="url must be string"):
            agent.get(123)

    def test_post_none_url(self, agent):
        """ValueError for None url on POST."""
        with pytest.raises(ValueError, match="url cannot be None"):
            agent.post(None, {})

    def test_post_none_data(self, agent):
        """ValueError for None data."""
        with pytest.raises(ValueError, match="data cannot be None"):
            agent.post("https://api.example.com/users", None)

    def test_get_error_endpoint(self, agent):
        """ConnectionError raised for error endpoint."""
        with pytest.raises(ConnectionError, match="Server error"):
            agent.get("https://api.example.com/error")


# =============================================================================
# EDGE CASES (4)
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases."""

    def test_post_empty_data(self, agent):
        """POST with empty dict works."""
        result = agent.post("https://api.example.com/users", {})
        assert result["status"] == 201
        assert result["created"] == {}

    @patch('api_agent.time.sleep')
    def test_retry_zero_retries(self, mock_sleep, agent):
        """max_retries=0 fails immediately."""
        with pytest.raises(ConnectionError):
            agent.retry_request("GET", "https://api.example.com/error", max_retries=0)
        mock_sleep.assert_not_called()  # No retries

    def test_flaky_resets(self, agent):
        """Flaky endpoint resets after success."""
        agent.reset_flaky()
        # First 2 calls fail
        with pytest.raises(ConnectionError):
            agent.get("https://api.example.com/flaky")
        with pytest.raises(ConnectionError):
            agent.get("https://api.example.com/flaky")
        # Third succeeds
        result = agent.get("https://api.example.com/flaky")
        assert result["status"] == 200
        # After reset, fails again
        with pytest.raises(ConnectionError):
            agent.get("https://api.example.com/flaky")

    def test_retry_none_method(self, agent):
        """ValueError for None method."""
        with pytest.raises(ValueError, match="method cannot be None"):
            agent.retry_request(None, "https://api.example.com/users")
