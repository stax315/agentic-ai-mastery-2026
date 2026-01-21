"""Tests for SimpleRetryAgent V0.1."""
import pytest
from simple_retry_agent import SimpleRetryAgent


class TestHappyPath:
    """Test successful operations."""

    def test_succeeds_first_try(self):
        """Operation that succeeds immediately returns result."""
        agent = SimpleRetryAgent()
        result = agent.retry(lambda: 42, max_retries=3, delay=0.001)
        assert result == 42

    def test_succeeds_on_retry(self):
        """Operation that fails once then succeeds returns result."""
        agent = SimpleRetryAgent()
        attempts = []

        def fail_once():
            attempts.append(1)
            if len(attempts) < 2:
                raise RuntimeError("First attempt fails")
            return "success"

        result = agent.retry(fail_once, max_retries=3, delay=0.001)
        assert result == "success"
        assert len(attempts) == 2


class TestValidation:
    """Test input validation."""

    def test_rejects_zero_retries(self):
        """max_retries=0 raises ValueError."""
        agent = SimpleRetryAgent()
        with pytest.raises(ValueError, match="max_retries must be >= 1"):
            agent.retry(lambda: 1, max_retries=0)

    def test_rejects_negative_retries(self):
        """Negative max_retries raises ValueError."""
        agent = SimpleRetryAgent()
        with pytest.raises(ValueError, match="max_retries must be >= 1"):
            agent.retry(lambda: 1, max_retries=-5)

    def test_rejects_negative_delay(self):
        """Negative delay raises ValueError."""
        agent = SimpleRetryAgent()
        with pytest.raises(ValueError, match="delay must be > 0"):
            agent.retry(lambda: 1, max_retries=3, delay=-1)


class TestRetryBehavior:
    """Test retry mechanics."""

    def test_counts_attempts_correctly(self):
        """Exactly max_retries attempts are made before giving up."""
        agent = SimpleRetryAgent()
        attempts = []

        def always_fail():
            attempts.append(1)
            raise RuntimeError("Always fails")

        with pytest.raises(RuntimeError):
            agent.retry(always_fail, max_retries=5, delay=0.001)

        assert len(attempts) == 5

    def test_stops_on_success(self):
        """Stops retrying immediately on success."""
        agent = SimpleRetryAgent()
        attempts = []

        def succeed_on_third():
            attempts.append(1)
            if len(attempts) < 3:
                raise ValueError("Not yet")
            return "done"

        result = agent.retry(succeed_on_third, max_retries=10, delay=0.001)
        assert result == "done"
        assert len(attempts) == 3  # Stopped at 3, didn't continue to 10

    def test_uses_fixed_delay(self):
        """Delay is applied between retries (basic check)."""
        import time
        agent = SimpleRetryAgent()
        attempts = []

        def fail_twice():
            attempts.append(time.time())
            if len(attempts) < 3:
                raise RuntimeError("fail")
            return "ok"

        agent.retry(fail_twice, max_retries=3, delay=0.05)
        # Check delays exist (not precise timing, just verifies delay happens)
        assert len(attempts) == 3
        assert attempts[1] - attempts[0] >= 0.04  # ~50ms delay


class TestErrorPropagation:
    """Test exception handling."""

    def test_raises_last_exception(self):
        """After exhausting retries, raises the last exception."""
        agent = SimpleRetryAgent()

        with pytest.raises(ZeroDivisionError):
            agent.retry(lambda: 1 / 0, max_retries=3, delay=0.001)

    def test_preserves_exception_type(self):
        """Original exception type is preserved."""
        agent = SimpleRetryAgent()

        class CustomError(Exception):
            pass

        with pytest.raises(CustomError):
            agent.retry(lambda: (_ for _ in ()).throw(CustomError("test")), max_retries=2, delay=0.001)


class TestVerify:
    """Test self-verification."""

    def test_verify_returns_dict(self):
        """verify() returns properly structured dict."""
        agent = SimpleRetryAgent()
        result = agent.verify()
        assert isinstance(result, dict)
        assert "status" in result
        assert "passed" in result
        assert "failed" in result
        assert "total" in result
        assert "details" in result

    def test_verify_all_pass(self):
        """All internal tests pass."""
        agent = SimpleRetryAgent()
        result = agent.verify()
        assert result["status"] == "PASS"
        assert result["failed"] == 0
        assert result["passed"] == result["total"]
