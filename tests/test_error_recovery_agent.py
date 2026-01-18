"""
Tests for ErrorRecoveryAgent - Day 3 Error Recovery & Resilience Patterns.

Test Categories:
- Failure Simulators (10 tests)
- Retry Logic (6 tests)
- Circuit Breaker (7 tests)
- Fallback Strategy (4 tests)
- Graceful Degradation (3 tests)
- Validation (5 tests)
- Integration (3 tests)
- verify() (2 tests)

Total: 40 tests
"""

import pytest
import random
import time
from unittest.mock import patch

from error_recovery_agent import (
    ErrorRecoveryAgent,
    TransientError,
    PermanentError,
    RateLimitError,
    CircuitOpenError,
    CircuitState,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def agent():
    """Create a fresh ErrorRecoveryAgent for each test."""
    return ErrorRecoveryAgent()


# =============================================================================
# FAILURE SIMULATOR TESTS (10 tests)
# =============================================================================

class TestFailureSimulators:
    """Tests for failure simulation methods."""

    def test_simulate_timeout_raises_timeout_error(self, agent):
        """simulate_timeout() raises TimeoutError."""
        with pytest.raises(TimeoutError) as exc_info:
            agent.simulate_timeout(0.001)
        assert "timed out" in str(exc_info.value).lower()

    def test_simulate_timeout_respects_delay(self, agent):
        """simulate_timeout() waits before raising."""
        start = time.time()
        with pytest.raises(TimeoutError):
            agent.simulate_timeout(0.05)
        elapsed = time.time() - start
        assert elapsed >= 0.05

    def test_simulate_rate_limit_raises_rate_limit_error(self, agent):
        """simulate_rate_limit() raises RateLimitError."""
        with pytest.raises(RateLimitError) as exc_info:
            agent.simulate_rate_limit(30)
        assert exc_info.value.retry_after == 30

    def test_simulate_rate_limit_includes_retry_after(self, agent):
        """RateLimitError includes retry_after attribute."""
        with pytest.raises(RateLimitError) as exc_info:
            agent.simulate_rate_limit(120)
        assert exc_info.value.retry_after == 120
        assert "120" in str(exc_info.value)

    def test_simulate_intermittent_failure_zero_rate_always_succeeds(self, agent):
        """With 0.0 failure rate, always succeeds."""
        for _ in range(10):
            result = agent.simulate_intermittent_failure(0.0, "ok")
            assert result == "ok"

    def test_simulate_intermittent_failure_full_rate_always_fails(self, agent):
        """With 1.0 failure rate, always fails."""
        for _ in range(10):
            with pytest.raises(TransientError):
                agent.simulate_intermittent_failure(1.0)

    def test_simulate_bad_response_malformed(self, agent):
        """simulate_bad_response('malformed') returns dict with None data."""
        result = agent.simulate_bad_response("malformed")
        assert isinstance(result, dict)
        assert result["data"] is None

    def test_simulate_bad_response_wrong_type(self, agent):
        """simulate_bad_response('wrong_type') returns dict with wrong types."""
        result = agent.simulate_bad_response("wrong_type")
        assert result["count"] == "not_a_number"

    def test_simulate_bad_response_unknown_type_raises(self, agent):
        """Unknown response type raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            agent.simulate_bad_response("invalid_type")
        assert "invalid_type" in str(exc_info.value)
        assert "Available" in str(exc_info.value)

    def test_simulate_resource_exhaustion_memory(self, agent):
        """simulate_resource_exhaustion('memory') raises MemoryError."""
        with pytest.raises(MemoryError):
            agent.simulate_resource_exhaustion("memory")


# =============================================================================
# RETRY LOGIC TESTS (6 tests)
# =============================================================================

class TestRetryWithBackoff:
    """Tests for retry_with_backoff() method."""

    def test_retry_succeeds_first_try(self, agent):
        """Returns immediately if operation succeeds."""
        result = agent.retry_with_backoff(
            lambda: "success",
            max_retries=3,
            base_delay=0.001
        )
        assert result == "success"
        assert agent._retry_metrics["attempts"] >= 1

    def test_retry_succeeds_after_failures(self, agent):
        """Retries and eventually succeeds."""
        counter = [0]

        def fail_twice():
            counter[0] += 1
            if counter[0] < 3:
                raise TransientError("temporary")
            return "success"

        result = agent.retry_with_backoff(
            fail_twice,
            max_retries=5,
            base_delay=0.001
        )
        assert result == "success"
        assert counter[0] == 3

    def test_retry_exhausts_retries(self, agent):
        """Raises after max_retries exhausted."""
        counter = [0]

        def always_fail():
            counter[0] += 1
            raise TransientError("always fails")

        with pytest.raises(TransientError):
            agent.retry_with_backoff(
                always_fail,
                max_retries=3,
                base_delay=0.001
            )

        # Should have attempted 4 times (initial + 3 retries)
        assert counter[0] == 4

    def test_retry_skips_permanent_errors(self, agent):
        """PermanentError raises immediately without retry."""
        counter = [0]

        def permanent_failure():
            counter[0] += 1
            raise PermanentError("don't retry this")

        with pytest.raises(PermanentError):
            agent.retry_with_backoff(
                permanent_failure,
                max_retries=5,
                base_delay=0.001
            )

        # Should have only attempted once
        assert counter[0] == 1

    def test_retry_backoff_increases(self, agent):
        """Each retry waits longer (exponential backoff)."""
        delays = []
        counter = [0]

        def track_and_fail():
            counter[0] += 1
            if counter[0] > 1:
                delays.append(agent._last_backoff_delay)
            if counter[0] < 4:
                raise TransientError("fail")
            return "ok"

        # Disable jitter for deterministic test
        agent.retry_with_backoff(
            track_and_fail,
            max_retries=5,
            base_delay=0.01,
            jitter=False
        )

        # Delays should be: 0.01, 0.02, 0.04 (exponential)
        assert len(delays) == 3
        assert delays[0] == pytest.approx(0.01)
        assert delays[1] == pytest.approx(0.02)
        assert delays[2] == pytest.approx(0.04)

    def test_retry_respects_max_delay(self, agent):
        """Delay never exceeds max_delay."""
        counter = [0]
        max_observed_delay = [0]

        def track_delay():
            counter[0] += 1
            if counter[0] > 1:
                max_observed_delay[0] = max(max_observed_delay[0], agent._last_backoff_delay)
            if counter[0] < 6:
                raise TransientError("fail")
            return "ok"

        agent.retry_with_backoff(
            track_delay,
            max_retries=10,
            base_delay=0.01,
            max_delay=0.05,
            jitter=False
        )

        # Should never exceed max_delay
        assert max_observed_delay[0] <= 0.05


# =============================================================================
# CIRCUIT BREAKER TESTS (7 tests)
# =============================================================================

class TestCircuitBreaker:
    """Tests for circuit_breaker() method."""

    def test_circuit_starts_closed(self, agent):
        """New circuit starts in CLOSED state."""
        agent.circuit_breaker(lambda: "ok", "test_closed")
        assert agent.get_circuit_state("test_closed") == "closed"

    def test_circuit_opens_after_threshold(self, agent):
        """After N failures, circuit opens."""
        def always_fail():
            raise TransientError("fail")

        # Trigger 5 failures (default threshold)
        for _ in range(5):
            with pytest.raises(TransientError):
                agent.circuit_breaker(always_fail, "test_open", failure_threshold=5)

        # Circuit should now be OPEN
        assert agent.get_circuit_state("test_open") == "open"

    def test_circuit_open_rejects_immediately(self, agent):
        """OPEN circuit raises CircuitOpenError immediately."""
        def always_fail():
            raise TransientError("fail")

        # Open the circuit
        for _ in range(5):
            with pytest.raises(TransientError):
                agent.circuit_breaker(always_fail, "test_reject", failure_threshold=5)

        # Now should reject immediately with CircuitOpenError
        with pytest.raises(CircuitOpenError) as exc_info:
            agent.circuit_breaker(lambda: "ok", "test_reject")

        assert "OPEN" in str(exc_info.value)

    @patch('error_recovery_agent.time.time')
    def test_circuit_half_opens_after_timeout(self, mock_time, agent):
        """After reset_timeout, circuit becomes HALF_OPEN."""
        mock_time.return_value = 1000.0

        def always_fail():
            raise TransientError("fail")

        # Open the circuit
        for _ in range(5):
            with pytest.raises(TransientError):
                agent.circuit_breaker(
                    always_fail,
                    "test_half_open",
                    failure_threshold=5,
                    reset_timeout=30.0
                )

        assert agent.get_circuit_state("test_half_open") == "open"

        # Advance time past reset_timeout
        mock_time.return_value = 1031.0  # 31 seconds later

        # Next call should attempt (HALF_OPEN state)
        # It will fail, but it should try
        with pytest.raises(TransientError):
            agent.circuit_breaker(always_fail, "test_half_open")

        # State should be OPEN again (failed in HALF_OPEN)
        assert agent.get_circuit_state("test_half_open") == "open"

    @patch('error_recovery_agent.time.time')
    def test_circuit_closes_on_success(self, mock_time, agent):
        """HALF_OPEN -> success -> CLOSED."""
        mock_time.return_value = 1000.0
        counter = [0]

        def fail_then_succeed():
            counter[0] += 1
            if counter[0] <= 5:
                raise TransientError("fail")
            return "success"

        # Open the circuit with 5 failures
        for _ in range(5):
            with pytest.raises(TransientError):
                agent.circuit_breaker(
                    fail_then_succeed,
                    "test_close",
                    failure_threshold=5,
                    reset_timeout=30.0
                )

        assert agent.get_circuit_state("test_close") == "open"

        # Advance time past reset_timeout
        mock_time.return_value = 1031.0

        # Now succeed (HALF_OPEN -> CLOSED)
        result = agent.circuit_breaker(fail_then_succeed, "test_close")
        assert result == "success"
        assert agent.get_circuit_state("test_close") == "closed"

    def test_circuit_separate_ids_independent(self, agent):
        """Different operation_ids have independent circuits."""
        def always_fail():
            raise TransientError("fail")

        # Open circuit A
        for _ in range(5):
            with pytest.raises(TransientError):
                agent.circuit_breaker(always_fail, "circuit_a", failure_threshold=5)

        # Circuit A should be open
        assert agent.get_circuit_state("circuit_a") == "open"

        # Circuit B should still work (independent)
        result = agent.circuit_breaker(lambda: "ok", "circuit_b")
        assert result == "ok"
        assert agent.get_circuit_state("circuit_b") == "closed"

    def test_circuit_metrics_tracked(self, agent):
        """Circuit breaker tracks opened/closed metrics."""
        def always_fail():
            raise TransientError("fail")

        initial_opened = agent._circuit_metrics["opened"]

        # Open the circuit
        for _ in range(5):
            with pytest.raises(TransientError):
                agent.circuit_breaker(always_fail, "metrics_test", failure_threshold=5)

        # Should have incremented opened count
        assert agent._circuit_metrics["opened"] > initial_opened


# =============================================================================
# FALLBACK STRATEGY TESTS (4 tests)
# =============================================================================

class TestFallbackStrategy:
    """Tests for fallback_strategy() method."""

    def test_fallback_uses_primary_on_success(self, agent):
        """Returns (result, 'primary') when primary works."""
        result, source = agent.fallback_strategy(
            primary=lambda: "primary_value",
            fallback=lambda: "fallback_value",
            default="default_value"
        )
        assert result == "primary_value"
        assert source == "primary"

    def test_fallback_uses_fallback_on_primary_failure(self, agent):
        """Returns (result, 'fallback') when primary fails."""
        def fail():
            raise TransientError("primary failed")

        result, source = agent.fallback_strategy(
            primary=fail,
            fallback=lambda: "fallback_value",
            default="default_value"
        )
        assert result == "fallback_value"
        assert source == "fallback"

    def test_fallback_uses_default_on_all_failures(self, agent):
        """Returns (default, 'default') when all fail."""
        def fail():
            raise TransientError("failed")

        result, source = agent.fallback_strategy(
            primary=fail,
            fallback=fail,
            default="default_value"
        )
        assert result == "default_value"
        assert source == "default"

    def test_fallback_raises_when_no_default(self, agent):
        """Raises original error if all fail and no default."""
        def fail():
            raise TransientError("original error")

        with pytest.raises(TransientError) as exc_info:
            agent.fallback_strategy(
                primary=fail,
                fallback=fail,
                default=None
            )
        assert "original error" in str(exc_info.value)


# =============================================================================
# GRACEFUL DEGRADATION TESTS (3 tests)
# =============================================================================

class TestGracefulDegradation:
    """Tests for graceful_degradation() method."""

    def test_graceful_returns_partial_results(self, agent):
        """Returns what succeeded, reports what failed."""
        def succeed():
            return "ok"

        def fail():
            raise TransientError("failed")

        result = agent.graceful_degradation({
            "op1": succeed,
            "op2": fail,
            "op3": succeed
        })

        assert "op1" in result["results"]
        assert "op3" in result["results"]
        assert "op2" in result["errors"]
        assert result["results"]["op1"] == "ok"
        assert "failed" in result["errors"]["op2"]

    def test_graceful_success_rate_correct(self, agent):
        """success_rate calculation is accurate."""
        def succeed():
            return "ok"

        def fail():
            raise TransientError("failed")

        result = agent.graceful_degradation({
            "op1": succeed,
            "op2": fail,
            "op3": succeed,
            "op4": fail
        })

        assert result["success_rate"] == pytest.approx(0.5)  # 2/4 = 0.5

    def test_graceful_empty_operations(self, agent):
        """Empty dict returns empty results, 0.0 rate."""
        result = agent.graceful_degradation({})

        assert result["results"] == {}
        assert result["errors"] == {}
        assert result["success_rate"] == 0.0


# =============================================================================
# VALIDATION TESTS (5 tests)
# =============================================================================

class TestValidation:
    """Tests for input validation."""

    def test_validate_positive_number_rejects_none(self, agent):
        """None is rejected for positive number validation."""
        with pytest.raises(ValueError) as exc_info:
            agent.simulate_timeout(None)
        assert "None" in str(exc_info.value)

    def test_validate_positive_number_rejects_bool(self, agent):
        """Booleans are rejected for positive number validation."""
        with pytest.raises(ValueError) as exc_info:
            agent.simulate_timeout(True)
        assert "bool" in str(exc_info.value)

    def test_validate_positive_number_rejects_string(self, agent):
        """Strings are rejected for positive number validation."""
        with pytest.raises(ValueError) as exc_info:
            agent.simulate_timeout("5")
        assert "str" in str(exc_info.value)

    def test_validate_positive_integer_rejects_float(self, agent):
        """Floats are rejected for positive integer validation."""
        with pytest.raises(ValueError) as exc_info:
            agent.simulate_rate_limit(30.5)
        assert "integer" in str(exc_info.value)

    def test_validate_probability_rejects_over_one(self, agent):
        """Values > 1.0 rejected for probability validation."""
        with pytest.raises(ValueError) as exc_info:
            agent.simulate_intermittent_failure(1.5)
        assert "0.0 and 1.0" in str(exc_info.value)


# =============================================================================
# INTEGRATION TESTS (3 tests)
# =============================================================================

class TestIntegration:
    """Tests for combined patterns."""

    def test_retry_with_intermittent_failure(self, agent):
        """Retry handles intermittent failures."""
        random.seed(42)  # Reproducible randomness

        counter = [0]

        def sometimes_fail():
            counter[0] += 1
            return agent.simulate_intermittent_failure(0.3, "success")

        # With retry, should eventually succeed
        result = agent.retry_with_backoff(
            sometimes_fail,
            max_retries=10,
            base_delay=0.001
        )
        assert result == "success"

    def test_fallback_with_timeout(self, agent):
        """Fallback handles timeout from primary."""
        def slow_primary():
            time.sleep(0.5)
            return "slow"

        def fast_fallback():
            return "fast"

        # Primary will timeout, fallback should be used
        result, source = agent.fallback_strategy(
            primary=lambda: agent.timeout_wrapper(slow_primary, timeout_seconds=0.1),
            fallback=fast_fallback,
            default="default"
        )

        assert result == "fast"
        assert source == "fallback"

    def test_metrics_tracking(self, agent):
        """Verify retry_metrics update correctly."""
        agent.reset_metrics()

        # Run some operations
        agent.retry_with_backoff(lambda: "ok", max_retries=1, base_delay=0.001)

        counter = [0]

        def fail_once():
            counter[0] += 1
            if counter[0] == 1:
                raise TransientError("fail")
            return "ok"

        agent.retry_with_backoff(fail_once, max_retries=3, base_delay=0.001)

        metrics = agent.get_metrics()
        assert metrics["retry"]["attempts"] >= 3  # At least 3 attempts total
        assert metrics["retry"]["successes"] == 2  # Both eventually succeeded


# =============================================================================
# VERIFY TESTS (2 tests)
# =============================================================================

class TestVerify:
    """Tests for verify() method."""

    def test_verify_returns_dict(self, agent):
        """verify() returns proper structure."""
        result = agent.verify()

        assert isinstance(result, dict)
        assert "status" in result
        assert "tests_run" in result
        assert "tests_passed" in result
        assert "tests_failed" in result
        assert "details" in result

    def test_verify_print_returns_bool(self, agent, capsys):
        """verify_print() returns bool and prints output."""
        result = agent.verify_print()

        assert isinstance(result, bool)

        captured = capsys.readouterr()
        assert "ErrorRecoveryAgent" in captured.out
        assert "Self-Verification" in captured.out


# =============================================================================
# TIMEOUT WRAPPER TESTS (2 additional tests to complete)
# =============================================================================

class TestTimeoutWrapper:
    """Tests for timeout_wrapper() method."""

    def test_timeout_wrapper_succeeds_fast_operation(self, agent):
        """Fast operation completes within timeout."""
        result = agent.timeout_wrapper(
            lambda: "quick",
            timeout_seconds=1.0
        )
        assert result == "quick"

    def test_timeout_wrapper_raises_on_slow_operation(self, agent):
        """Slow operation raises TimeoutError."""
        def slow():
            time.sleep(0.5)
            return "slow"

        with pytest.raises(TimeoutError):
            agent.timeout_wrapper(slow, timeout_seconds=0.1)
