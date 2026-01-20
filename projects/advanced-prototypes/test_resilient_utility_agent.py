"""Tests for ResilientUtilityAgent - Day 3 Session 3."""

import pytest
import math
import time
import sys
from pathlib import Path

# Add day-02 to path for imports
day02_path = Path(__file__).parent.parent / "day-02"
if str(day02_path) not in sys.path:
    sys.path.insert(0, str(day02_path))

from resilient_utility_agent import ResilientUtilityAgent


@pytest.fixture
def agent():
    return ResilientUtilityAgent()


# =============================================================================
# STEP 1: BASIC ROUTING (17 tests)
# =============================================================================

class TestStringRouting:
    def test_reverse_routes(self, agent):
        assert agent.execute("reverse", "hello", use_resilience=False) == "olleh"

    def test_uppercase_routes(self, agent):
        assert agent.execute("uppercase", "hello", use_resilience=False) == "HELLO"

    def test_lowercase_routes(self, agent):
        assert agent.execute("lowercase", "HELLO", use_resilience=False) == "hello"

    def test_count_words_routes(self, agent):
        assert agent.execute("count_words", "hello world", use_resilience=False) == 2

    def test_remove_spaces_routes(self, agent):
        assert agent.execute("remove_spaces", "a b c", use_resilience=False) == "abc"


class TestDateTimeRouting:
    def test_current_time_routes(self, agent):
        result = agent.execute("current_time", use_resilience=False)
        assert len(result) == 8  # HH:MM:SS format
        assert result.count(":") == 2

    def test_current_date_routes(self, agent):
        result = agent.execute("current_date", use_resilience=False)
        assert len(result) == 10  # YYYY-MM-DD format
        assert result.count("-") == 2

    def test_add_days_routes(self, agent):
        result = agent.execute("add_days", "2024-01-01", 10, use_resilience=False)
        assert result == "2024-01-11"

    def test_days_between_routes(self, agent):
        result = agent.execute("days_between", "2024-01-01", "2024-01-11", use_resilience=False)
        assert result == 10

    def test_format_date_routes(self, agent):
        result = agent.execute("format_date", "2024-01-15", "%B %d, %Y", use_resilience=False)
        assert result == "January 15, 2024"


class TestCalculatorRouting:
    def test_add_routes(self, agent):
        assert agent.execute("add", 2, 3, use_resilience=False) == 5.0

    def test_subtract_routes(self, agent):
        assert agent.execute("subtract", 10, 4, use_resilience=False) == 6.0

    def test_multiply_routes(self, agent):
        assert agent.execute("multiply", 3, 4, use_resilience=False) == 12.0

    def test_divide_routes(self, agent):
        assert agent.execute("divide", 15, 3, use_resilience=False) == 5.0

    def test_power_routes(self, agent):
        assert agent.execute("power", 2, 3, use_resilience=False) == 8.0

    def test_modulo_routes(self, agent):
        assert agent.execute("modulo", 10, 3, use_resilience=False) == 1.0

    def test_sqrt_routes(self, agent):
        assert agent.execute("sqrt", 16, use_resilience=False) == 4.0


# =============================================================================
# VALIDATION
# =============================================================================

class TestValidation:
    def test_unknown_operation_raises(self, agent):
        with pytest.raises(ValueError, match="Unknown operation"):
            agent.execute("unknown")

    def test_none_operation_raises(self, agent):
        with pytest.raises(ValueError, match="cannot be None"):
            agent.execute(None)

    def test_error_includes_available_operations(self, agent):
        try:
            agent.execute("typo")
        except ValueError as e:
            assert "Available:" in str(e)
            assert "add" in str(e)


# =============================================================================
# DISCOVERY
# =============================================================================

class TestDiscovery:
    def test_list_operations_count(self, agent):
        ops = agent.list_operations()
        assert len(ops) == 17

    def test_list_operations_sorted(self, agent):
        ops = agent.list_operations()
        assert ops == sorted(ops)

    def test_list_operations_includes_all_categories(self, agent):
        ops = agent.list_operations()
        # String ops
        assert "reverse" in ops
        assert "uppercase" in ops
        # DateTime ops
        assert "current_date" in ops
        assert "add_days" in ops
        # Calculator ops
        assert "add" in ops
        assert "sqrt" in ops

    def test_list_by_category(self, agent):
        cats = agent.list_operations_by_category()
        assert "string" in cats
        assert "datetime" in cats
        assert "calculator" in cats
        assert len(cats["string"]) == 5
        assert len(cats["datetime"]) == 5
        assert len(cats["calculator"]) == 7


# =============================================================================
# FAILURE INJECTION (Testing Infrastructure)
# =============================================================================

class TestFailureInjection:
    def test_transient_injection_fails(self, agent):
        """Injected transient failure raises TransientError."""
        from error_recovery_agent import TransientError
        agent._inject_failure("add", "transient", fail_count=1)
        with pytest.raises(TransientError):
            agent.execute("add", 2, 3, use_resilience=False)
        agent._clear_failures()

    def test_permanent_injection_fails(self, agent):
        """Injected permanent failure raises PermanentError."""
        from error_recovery_agent import PermanentError
        agent._inject_failure("add", "permanent", fail_count=1)
        with pytest.raises(PermanentError):
            agent.execute("add", 2, 3, use_resilience=False)
        agent._clear_failures()

    def test_injection_countdown(self, agent):
        """Injection fails N times then succeeds."""
        from error_recovery_agent import TransientError
        agent._inject_failure("add", "transient", fail_count=2)

        # First two calls fail
        with pytest.raises(TransientError):
            agent.execute("add", 2, 3, use_resilience=False)
        with pytest.raises(TransientError):
            agent.execute("add", 2, 3, use_resilience=False)

        # Third call succeeds
        result = agent.execute("add", 2, 3, use_resilience=False)
        assert result == 5.0

        agent._clear_failures()

    def test_clear_failures(self, agent):
        """_clear_failures removes all injections."""
        agent._inject_failure("add", "transient", fail_count=100)
        agent._clear_failures()
        # Should succeed now
        result = agent.execute("add", 2, 3, use_resilience=False)
        assert result == 5.0


# =============================================================================
# STEP 2: RETRY + FALLBACK
# =============================================================================

class TestRetryRecovery:
    """Test that retry recovers from transient failures."""

    def test_retry_succeeds_after_transient_failures(self, agent):
        """Operation succeeds after transient failures."""
        agent._inject_failure("add", "transient", fail_count=2)
        # With 3 retries, should succeed on 3rd attempt
        result = agent.execute("add", 5, 3)
        assert result == 8.0
        agent._clear_failures()

    def test_retry_works_for_string_ops(self, agent):
        """Retry works for string operations too."""
        agent._inject_failure("reverse", "transient", fail_count=2)
        result = agent.execute("reverse", "hello")
        assert result == "olleh"
        agent._clear_failures()

    def test_retry_works_for_datetime_ops(self, agent):
        """Retry works for datetime operations."""
        agent._inject_failure("add_days", "transient", fail_count=1)
        result = agent.execute("add_days", "2024-01-01", 5)
        assert result == "2024-01-06"
        agent._clear_failures()


class TestFallbackValues:
    """Test that fallbacks return correct values."""

    def test_calculator_fallback_is_nan(self, agent):
        """Calculator operations return NaN on failure."""
        agent._inject_failure("add", "permanent", fail_count=100)
        result = agent.execute("add", 2, 3)
        assert math.isnan(result)
        agent._clear_failures()

    def test_count_words_fallback_is_negative_one(self, agent):
        """count_words returns -1 on failure (not 0)."""
        agent._inject_failure("count_words", "permanent", fail_count=100)
        result = agent.execute("count_words", "hello world")
        assert result == -1
        agent._clear_failures()

    def test_string_fallback_returns_input(self, agent):
        """String ops return input unchanged on failure."""
        agent._inject_failure("uppercase", "permanent", fail_count=100)
        result = agent.execute("uppercase", "hello")
        assert result == "hello"  # Input returned unchanged
        agent._clear_failures()

    def test_datetime_fallback_returns_epoch(self, agent):
        """DateTime ops return epoch on failure."""
        agent._inject_failure("current_date", "permanent", fail_count=100)
        result = agent.execute("current_date")
        assert result == "1970-01-01"
        agent._clear_failures()

    def test_current_time_fallback_returns_midnight(self, agent):
        """current_time returns midnight on failure."""
        agent._inject_failure("current_time", "permanent", fail_count=100)
        result = agent.execute("current_time")
        assert result == "00:00:00"
        agent._clear_failures()

    def test_days_between_fallback_is_negative_one(self, agent):
        """days_between returns -1 on failure."""
        agent._inject_failure("days_between", "permanent", fail_count=100)
        result = agent.execute("days_between", "2024-01-01", "2024-01-10")
        assert result == -1
        agent._clear_failures()


class TestPermanentVsTransient:
    """Test different error types."""

    def test_permanent_errors_not_retried(self, agent):
        """Permanent errors go straight to fallback."""
        agent._inject_failure("add", "permanent", fail_count=1)
        result = agent.execute("add", 2, 3)
        # Should be NaN (fallback) because permanent errors aren't retried
        assert math.isnan(result)
        agent._clear_failures()

    def test_transient_exhaustion_uses_fallback(self, agent):
        """When all retries exhausted, fallback is used."""
        # More failures than retries
        agent._inject_failure("add", "transient", fail_count=10)
        result = agent.execute("add", 2, 3)
        # Should be NaN (fallback) after 4 attempts (1 + 3 retries)
        assert math.isnan(result)
        agent._clear_failures()


# =============================================================================
# STEP 3: CIRCUIT BREAKER
# =============================================================================

class TestCircuitBreakerBasics:
    """Test circuit breaker state inspection."""

    def test_get_circuit_states_returns_dict(self, agent):
        """Circuit states should return a dict with all agents."""
        states = agent.get_circuit_states()
        assert isinstance(states, dict)
        assert "string_agent" in states
        assert "datetime_agent" in states
        assert "calculator_agent" in states

    def test_circuits_start_not_initialized(self, agent):
        """Circuits are not initialized until first use."""
        states = agent.get_circuit_states()
        # Before any operations, circuits are not initialized
        assert states["calculator_agent"] == "not_initialized"

    def test_circuit_initializes_on_first_use(self, agent):
        """Circuit initializes to closed on first operation."""
        agent.execute("add", 2, 3)  # Trigger circuit initialization
        states = agent.get_circuit_states()
        assert states["calculator_agent"] == "closed"


class TestCircuitBreakerIsolation:
    """Test that circuits are isolated per-agent."""

    def test_string_circuit_failure_doesnt_affect_calculator(self, agent):
        """Failing string agent shouldn't affect calculator circuit."""
        # Open string circuit by causing many failures
        agent._inject_failure("reverse", "transient", fail_count=100)
        for _ in range(6):  # Exceed threshold
            agent.execute("reverse", "hello")  # Uses fallback
        agent._clear_failures()

        # String circuit should be open
        states = agent.get_circuit_states()
        assert states["string_agent"] == "open"

        # Calculator should still work normally
        result = agent.execute("add", 2, 3)
        assert result == 5.0

    def test_calculator_circuit_failure_doesnt_affect_datetime(self, agent):
        """Failing calculator agent shouldn't affect datetime circuit."""
        # Open calculator circuit
        agent._inject_failure("add", "transient", fail_count=100)
        for _ in range(6):
            agent.execute("add", 2, 3)  # Uses fallback
        agent._clear_failures()

        # Calculator circuit should be open
        states = agent.get_circuit_states()
        assert states["calculator_agent"] == "open"

        # DateTime should still work normally
        result = agent.execute("current_date")
        assert len(result) == 10  # YYYY-MM-DD


class TestCircuitBreakerFallback:
    """Test that open circuit triggers fallback."""

    def test_open_circuit_uses_fallback_immediately(self, agent):
        """When circuit is open, fallback is used without retrying."""
        # Open calculator circuit
        agent._inject_failure("multiply", "transient", fail_count=100)
        for _ in range(6):
            agent.execute("multiply", 2, 3)
        agent._clear_failures()

        # Circuit is open - next call should use fallback immediately
        result = agent.execute("multiply", 5, 5)
        assert math.isnan(result)  # Fallback is NaN for calculator

    def test_string_open_circuit_returns_input(self, agent):
        """String circuit open returns input as fallback."""
        agent._inject_failure("uppercase", "transient", fail_count=100)
        for _ in range(6):
            agent.execute("uppercase", "test")
        agent._clear_failures()

        result = agent.execute("uppercase", "hello")
        assert result == "hello"  # Input returned unchanged


class TestCircuitBreakerRecovery:
    """Test circuit breaker recovery (half-open state)."""

    def test_circuit_recovers_after_reset_timeout(self, agent):
        """Circuit should recover after reset_timeout."""
        # Use fast reset timeout for testing
        agent._circuit_config["reset_timeout"] = 0.1

        # Open circuit
        agent._inject_failure("add", "transient", fail_count=100)
        for _ in range(6):
            agent.execute("add", 2, 3)

        assert agent.get_circuit_states()["calculator_agent"] == "open"
        agent._clear_failures()

        # Wait for reset timeout
        time.sleep(0.15)

        # Circuit should be half-open, operation should succeed
        result = agent.execute("add", 2, 3)
        assert result == 5.0

        # Circuit should be closed after success
        assert agent.get_circuit_states()["calculator_agent"] == "closed"

    def test_reset_circuit_manually(self, agent):
        """Manual circuit reset should work."""
        # Open circuit
        agent._inject_failure("add", "transient", fail_count=100)
        for _ in range(6):
            agent.execute("add", 2, 3)
        agent._clear_failures()

        assert agent.get_circuit_states()["calculator_agent"] == "open"

        # Manual reset
        agent.reset_circuit("calculator_agent")
        assert agent.get_circuit_states()["calculator_agent"] == "closed"

        # Should work now
        result = agent.execute("add", 2, 3)
        assert result == 5.0


# =============================================================================
# STEP 5: LOGGING
# =============================================================================

class TestOperationLogging:
    """Test operation logging functionality."""

    def test_log_captures_successful_operation(self, agent):
        """Successful operations are logged with source='primary'."""
        agent.clear_operation_log()
        agent.execute("add", 2, 3)
        log = agent.get_operation_log()
        assert len(log) == 1
        assert log[0]["operation"] == "add"
        assert log[0]["source"] == "primary"
        assert log[0]["agent"] == "calculator_agent"

    def test_log_captures_fallback_operation(self, agent):
        """Fallback operations are logged with source='fallback'."""
        agent.clear_operation_log()
        agent._inject_failure("add", "permanent", fail_count=100)
        agent.execute("add", 2, 3)
        agent._clear_failures()
        log = agent.get_operation_log()
        assert len(log) == 1
        assert log[0]["source"] == "fallback"

    def test_log_captures_circuit_open(self, agent):
        """Circuit open is logged with source='circuit_open'."""
        agent.clear_operation_log()
        # Open circuit
        agent._inject_failure("add", "transient", fail_count=100)
        for _ in range(6):
            agent.execute("add", 2, 3)
        agent._clear_failures()
        agent.clear_operation_log()  # Clear logs from opening circuit

        # This should be circuit_open
        agent.execute("add", 2, 3)
        log = agent.get_operation_log()
        assert len(log) == 1
        assert log[0]["source"] == "circuit_open"

    def test_log_has_timestamp(self, agent):
        """Log entries have timestamp."""
        agent.clear_operation_log()
        agent.execute("add", 2, 3)
        log = agent.get_operation_log()
        assert "timestamp" in log[0]
        assert isinstance(log[0]["timestamp"], float)

    def test_clear_operation_log(self, agent):
        """clear_operation_log empties the log."""
        agent.execute("add", 2, 3)
        agent.clear_operation_log()
        assert len(agent.get_operation_log()) == 0


class TestResilienceMetrics:
    """Test resilience metrics accessibility."""

    def test_get_resilience_metrics_returns_dict(self, agent):
        """Resilience metrics should return a dict."""
        metrics = agent.get_resilience_metrics()
        assert isinstance(metrics, dict)
        assert "retry" in metrics
        assert "circuit_breaker" in metrics

    def test_metrics_track_retry_attempts(self, agent):
        """Metrics track retry attempts."""
        agent.execute("add", 2, 3)
        metrics = agent.get_resilience_metrics()
        assert metrics["retry"]["attempts"] >= 1


# =============================================================================
# VERIFY
# =============================================================================

class TestVerify:
    def test_verify_returns_dict(self, agent):
        result = agent.verify()
        assert isinstance(result, dict)
        assert "status" in result
        assert "tests_passed" in result
        assert "tests_run" in result

    def test_verify_passes(self, agent):
        result = agent.verify()
        assert result["status"] == "PASS"

    def test_verify_print_returns_bool(self, agent, capsys):
        result = agent.verify_print()
        assert result is True
        captured = capsys.readouterr()
        assert "ResilientUtilityAgent" in captured.out
