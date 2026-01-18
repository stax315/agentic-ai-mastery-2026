"""Tests for UtilityAgent - Day 3 integration tests."""

import pytest
from utility_agent import UtilityAgent


@pytest.fixture
def agent():
    return UtilityAgent()


# =============================================================================
# CALCULATOR ROUTING
# =============================================================================

class TestCalculatorRouting:
    def test_add_routes(self, agent):
        assert agent.execute("add", 2, 3) == 5.0

    def test_subtract_routes(self, agent):
        assert agent.execute("subtract", 10, 4) == 6.0

    def test_multiply_routes(self, agent):
        assert agent.execute("multiply", 3, 4) == 12.0

    def test_divide_routes(self, agent):
        assert agent.execute("divide", 15, 3) == 5.0

    def test_power_routes(self, agent):
        assert agent.execute("power", 2, 3) == 8.0

    def test_modulo_routes(self, agent):
        assert agent.execute("modulo", 10, 3) == 1.0

    def test_sqrt_routes(self, agent):
        assert agent.execute("sqrt", 16) == 4.0


# =============================================================================
# ERROR RECOVERY ROUTING
# =============================================================================

class TestErrorRecoveryRouting:
    def test_simulate_bad_response_routes(self, agent):
        result = agent.execute("simulate_bad_response", "malformed")
        assert isinstance(result, dict)

    def test_simulate_intermittent_failure_routes(self, agent):
        # 0% failure rate = always succeeds
        result = agent.execute("simulate_intermittent_failure", 0.0, "ok")
        assert result == "ok"

    def test_graceful_degradation_routes(self, agent):
        result = agent.execute("graceful_degradation", {"test": lambda: "success"})
        assert result["success_rate"] == 1.0


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


# =============================================================================
# DISCOVERY
# =============================================================================

class TestDiscovery:
    def test_list_operations_count(self, agent):
        ops = agent.list_operations()
        assert len(ops) == 17  # 7 calc + 5 sim + 5 recovery

    def test_list_operations_sorted(self, agent):
        ops = agent.list_operations()
        assert ops == sorted(ops)

    def test_list_by_category(self, agent):
        cats = agent.list_operations_by_category()
        assert "calculator" in cats
        assert "error_simulation" in cats
        assert "error_recovery" in cats
        assert len(cats["calculator"]) == 7


# =============================================================================
# VERIFY
# =============================================================================

class TestVerify:
    def test_verify_returns_dict(self, agent):
        result = agent.verify()
        assert result["status"] == "PASS"

    def test_verify_print_returns_bool(self, agent, capsys):
        result = agent.verify_print()
        assert result is True
