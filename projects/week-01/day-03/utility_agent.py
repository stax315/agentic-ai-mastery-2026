"""
UtilityAgent - Day 3 Multi-Agent Coordinator.

Integrates CalculatorAgent + ErrorRecoveryAgent using Operation Registry pattern.
Demonstrates: Adding a new agent takes ~10 lines of code.
"""

from calculator_agent import CalculatorAgent
from error_recovery_agent import ErrorRecoveryAgent


class UtilityAgent:
    """Coordinator agent using Operation Registry pattern (Day 2 Pattern 19)."""

    def __init__(self) -> None:
        """Initialize with sub-agents."""
        self.version = "1.0"

        # Sub-agents (Pattern 18: Agent Composition)
        self.calculator_agent = CalculatorAgent()
        self.error_recovery_agent = ErrorRecoveryAgent()

        # Operation Registry (Pattern 19)
        self._operations = self._build_operation_registry()

    def _build_operation_registry(self) -> dict:
        """Map operation names to (agent, method_name) tuples."""
        return {
            # Calculator operations (7)
            "add": (self.calculator_agent, "add"),
            "subtract": (self.calculator_agent, "subtract"),
            "multiply": (self.calculator_agent, "multiply"),
            "divide": (self.calculator_agent, "divide"),
            "power": (self.calculator_agent, "power"),
            "modulo": (self.calculator_agent, "modulo"),
            "sqrt": (self.calculator_agent, "sqrt"),

            # Error Recovery operations (5 simulators + 5 recovery)
            "simulate_timeout": (self.error_recovery_agent, "simulate_timeout"),
            "simulate_rate_limit": (self.error_recovery_agent, "simulate_rate_limit"),
            "simulate_intermittent_failure": (self.error_recovery_agent, "simulate_intermittent_failure"),
            "simulate_bad_response": (self.error_recovery_agent, "simulate_bad_response"),
            "simulate_resource_exhaustion": (self.error_recovery_agent, "simulate_resource_exhaustion"),
            "retry_with_backoff": (self.error_recovery_agent, "retry_with_backoff"),
            "circuit_breaker": (self.error_recovery_agent, "circuit_breaker"),
            "fallback_strategy": (self.error_recovery_agent, "fallback_strategy"),
            "graceful_degradation": (self.error_recovery_agent, "graceful_degradation"),
            "timeout_wrapper": (self.error_recovery_agent, "timeout_wrapper"),
        }

    def _validate_operation(self, operation) -> None:
        """Validate operation name (Pattern 22)."""
        if operation is None:
            raise ValueError("operation cannot be None")
        if operation not in self._operations:
            available = ", ".join(sorted(self._operations.keys()))
            raise ValueError(f"Unknown operation: '{operation}'. Available: {available}")

    def execute(self, operation: str, *args, **kwargs):
        """Route operation to appropriate sub-agent (Pattern 20)."""
        self._validate_operation(operation)
        agent, method_name = self._operations[operation]
        method = getattr(agent, method_name)
        return method(*args, **kwargs)  # Errors propagate (Pattern 21)

    def list_operations(self) -> list:
        """Return sorted list of available operations (Pattern 23)."""
        return sorted(self._operations.keys())

    def list_operations_by_category(self) -> dict:
        """Return operations grouped by category."""
        return {
            "calculator": ["add", "subtract", "multiply", "divide", "power", "modulo", "sqrt"],
            "error_simulation": ["simulate_timeout", "simulate_rate_limit",
                                "simulate_intermittent_failure", "simulate_bad_response",
                                "simulate_resource_exhaustion"],
            "error_recovery": ["retry_with_backoff", "circuit_breaker", "fallback_strategy",
                              "graceful_degradation", "timeout_wrapper"],
        }

    def verify(self) -> dict:
        """Run self-tests for routing."""
        tests = [
            ("add routes correctly", lambda: self.execute("add", 2, 3), 5.0, False),
            ("subtract routes correctly", lambda: self.execute("subtract", 10, 4), 6.0, False),
            ("multiply routes correctly", lambda: self.execute("multiply", 3, 4), 12.0, False),
            ("divide routes correctly", lambda: self.execute("divide", 15, 3), 5.0, False),
            ("sqrt routes correctly", lambda: self.execute("sqrt", 16), 4.0, False),
            ("unknown operation raises", lambda: self.execute("unknown"), ValueError, True),
            ("list_operations returns 17", lambda: len(self.list_operations()), 17, False),
        ]

        details = []
        passed = 0

        for desc, op, expected, expects_error in tests:
            try:
                result = op()
                if expects_error:
                    details.append({"test": desc, "result": "FAIL"})
                elif result == expected:
                    details.append({"test": desc, "result": "PASS"})
                    passed += 1
                else:
                    details.append({"test": desc, "result": "FAIL", "reason": f"Got {result}"})
            except Exception as e:
                if expects_error and isinstance(e, expected):
                    details.append({"test": desc, "result": "PASS"})
                    passed += 1
                else:
                    details.append({"test": desc, "result": "FAIL", "reason": str(e)})

        return {
            "status": "PASS" if passed == len(tests) else "FAIL",
            "tests_passed": passed,
            "tests_run": len(tests),
            "details": details
        }

    def verify_print(self) -> bool:
        """Print verification results."""
        result = self.verify()
        print("=" * 50)
        print(f"UtilityAgent v{self.version} Self-Verification")
        print("=" * 50)
        for d in result["details"]:
            sym = "✓" if d["result"] == "PASS" else "✗"
            print(f"  {sym} {d['test']}")
        print("-" * 50)
        print(f"✓ Status: {result['status']} ({result['tests_passed']}/{result['tests_run']})")
        print(f"  Operations: {len(self.list_operations())} available")
        print("=" * 50)
        return result["status"] == "PASS"


if __name__ == "__main__":
    agent = UtilityAgent()
    agent.verify_print()
