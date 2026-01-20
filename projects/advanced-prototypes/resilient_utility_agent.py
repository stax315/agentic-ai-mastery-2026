"""
ADVANCED PROTOTYPE - Built during Week 1 (early)

Revisit: Week 17-20 (Production Patterns phase)

Context: Built this before completing foundational patterns.
Contains production-grade concepts (resilience wrapper, per-agent circuit
isolation, failure injection) that should be studied after mastering basics.

Original build date: January 18, 2026
Roadmap position when built: Week 1 Day 3
Appropriate roadmap position: Week 17-20

Patterns to extract:
- Resilient wrapper (Circuit Breaker -> Retry -> Fallback layering)
- Per-agent circuit breaker isolation
- Recognizable fallback values (NaN for calc, epoch for dates)
- Failure injection for testing resilience
- Operation logging with source tracking
- Configurable retry/circuit settings

Why saved: Excellent implementation of full resilience stack, built out of sequence.
Preserving for pattern study after foundations complete.

================================================================================
ORIGINAL DOCSTRING:
================================================================================

ResilientUtilityAgent - Production-ready multi-agent coordinator.

Day 3 Session 3 - Combines ALL patterns into production-ready system.

Integrates:
- Day 2: StringAgent, DateTimeAgent
- Day 3: CalculatorAgent
- Day 3: ErrorRecoveryAgent patterns

Every operation is wrapped with:
1. Circuit breaker (fail fast if service is down)
2. Retry with exponential backoff (for transient errors)
3. Fallback strategy (safe defaults)
4. Logging of all recovery attempts
"""

import sys
import math
import time
from pathlib import Path
from typing import Any, Callable

# Import Day 3 agents (same directory)
from calculator_agent import CalculatorAgent
from error_recovery_agent import ErrorRecoveryAgent, TransientError, PermanentError, CircuitOpenError

# Import Day 2 agents (different directory - with safety fallback)
try:
    from string_agent import StringAgent
    from datetime_agent import DateTimeAgent
except ImportError:
    # Add day-02 to path if not already available
    day02_path = Path(__file__).parent.parent / "day-02"
    if str(day02_path) not in sys.path:
        sys.path.insert(0, str(day02_path))
    from string_agent import StringAgent
    from datetime_agent import DateTimeAgent


class ResilientUtilityAgent:
    """Production-ready multi-agent coordinator with full resilience."""

    def __init__(
        self,
        retry_config: dict = None,
        circuit_config: dict = None,
        enable_logging: bool = True
    ) -> None:
        """
        Initialize ResilientUtilityAgent.

        Args:
            retry_config: Override retry settings (max_retries, base_delay, etc.)
            circuit_config: Override circuit breaker settings (failure_threshold, reset_timeout)
            enable_logging: Whether to log operations (default True)
        """
        self.version = "1.0"

        # Sub-agents (actual workers)
        self.string_agent = StringAgent()
        self.datetime_agent = DateTimeAgent()
        self.calculator_agent = CalculatorAgent()

        # Resilience provider (NOT a sub-agent - a utility)
        self._recovery = ErrorRecoveryAgent()

        # Configuration
        self._retry_config = retry_config or {
            "max_retries": 3,
            "base_delay": 0.01,  # Fast for testing
            "max_delay": 1.0,
            "jitter": True
        }
        self._circuit_config = circuit_config or {
            "failure_threshold": 5,
            "reset_timeout": 30.0
        }

        # Build registries
        self._operations = self._build_operation_registry()
        self._agent_for_operation = self._build_agent_mapping()
        self._fallbacks = self._build_fallback_registry()

        # Failure injection for testing
        self._injected_failures = {}

        # Logging
        self._enable_logging = enable_logging
        self._operation_log = []

    # =========================================================================
    # OPERATION REGISTRY (Pattern 19)
    # =========================================================================

    def _build_operation_registry(self) -> dict:
        """Map operation names to (agent, method_name) tuples."""
        return {
            # String operations (5)
            "reverse": (self.string_agent, "reverse_string"),
            "uppercase": (self.string_agent, "to_uppercase"),
            "lowercase": (self.string_agent, "to_lowercase"),
            "count_words": (self.string_agent, "count_words"),
            "remove_spaces": (self.string_agent, "remove_spaces"),

            # DateTime operations (5)
            "current_time": (self.datetime_agent, "get_current_time"),
            "current_date": (self.datetime_agent, "get_current_date"),
            "add_days": (self.datetime_agent, "add_days"),
            "days_between": (self.datetime_agent, "days_between"),
            "format_date": (self.datetime_agent, "format_date"),

            # Calculator operations (7)
            "add": (self.calculator_agent, "add"),
            "subtract": (self.calculator_agent, "subtract"),
            "multiply": (self.calculator_agent, "multiply"),
            "divide": (self.calculator_agent, "divide"),
            "power": (self.calculator_agent, "power"),
            "modulo": (self.calculator_agent, "modulo"),
            "sqrt": (self.calculator_agent, "sqrt"),
        }

    def _build_agent_mapping(self) -> dict:
        """Map operation names to agent identifiers for circuit breaker isolation."""
        return {
            # String agent operations
            "reverse": "string_agent",
            "uppercase": "string_agent",
            "lowercase": "string_agent",
            "count_words": "string_agent",
            "remove_spaces": "string_agent",

            # DateTime agent operations
            "current_time": "datetime_agent",
            "current_date": "datetime_agent",
            "add_days": "datetime_agent",
            "days_between": "datetime_agent",
            "format_date": "datetime_agent",

            # Calculator agent operations
            "add": "calculator_agent",
            "subtract": "calculator_agent",
            "multiply": "calculator_agent",
            "divide": "calculator_agent",
            "power": "calculator_agent",
            "modulo": "calculator_agent",
            "sqrt": "calculator_agent",
        }

    def _build_fallback_registry(self) -> dict:
        """
        Define fallback behaviors per operation type.

        Fallback values are designed to be recognizable as "error" values:
        - String ops: Return input unchanged
        - count_words: Return -1 (0 is valid for empty string)
        - DateTime ops: Return epoch/midnight
        - Calculator ops: Return NaN (math convention for undefined)
        """
        return {
            # String operations: Return input unchanged (safe default)
            "reverse": lambda args, kwargs: args[0] if args else "",
            "uppercase": lambda args, kwargs: args[0] if args else "",
            "lowercase": lambda args, kwargs: args[0] if args else "",
            "count_words": lambda args, kwargs: -1,  # -1 = error (0 is valid)
            "remove_spaces": lambda args, kwargs: args[0] if args else "",

            # DateTime operations: Use epoch/midnight (recognizable error values)
            "current_time": lambda args, kwargs: "00:00:00",  # Midnight
            "current_date": lambda args, kwargs: "1970-01-01",  # Epoch
            "add_days": lambda args, kwargs: args[0] if args else "1970-01-01",
            "days_between": lambda args, kwargs: -1,  # -1 = error
            "format_date": lambda args, kwargs: args[0] if args else "",

            # Calculator operations: Return NaN (math convention for undefined)
            "add": lambda args, kwargs: float('nan'),
            "subtract": lambda args, kwargs: float('nan'),
            "multiply": lambda args, kwargs: float('nan'),
            "divide": lambda args, kwargs: float('nan'),
            "power": lambda args, kwargs: float('nan'),
            "modulo": lambda args, kwargs: float('nan'),
            "sqrt": lambda args, kwargs: float('nan'),
        }

    def _get_fallback_value(self, operation: str, args: tuple, kwargs: dict) -> Any:
        """Get fallback value for an operation."""
        return self._fallbacks[operation](args, kwargs)

    # =========================================================================
    # VALIDATION (Pattern 22)
    # =========================================================================

    def _validate_operation(self, operation) -> None:
        """Validate operation name, include available options in error."""
        if operation is None:
            raise ValueError("operation cannot be None")
        if operation not in self._operations:
            available = ", ".join(sorted(self._operations.keys()))
            raise ValueError(f"Unknown operation: '{operation}'. Available: {available}")

    # =========================================================================
    # RAW EXECUTION (No Resilience)
    # =========================================================================

    def _execute_raw(self, operation: str, *args, **kwargs) -> Any:
        """Execute operation directly without resilience wrapper."""
        # Check for injected failure (testing only)
        if operation in self._injected_failures:
            failure = self._injected_failures[operation]
            if failure["remaining"] > 0:
                failure["remaining"] -= 1
                if failure["type"] == "transient":
                    raise TransientError(f"Injected transient failure for {operation}")
                else:
                    raise PermanentError(f"Injected permanent failure for {operation}")

        # Normal execution
        agent, method_name = self._operations[operation]
        method = getattr(agent, method_name)
        return method(*args, **kwargs)

    # =========================================================================
    # RESILIENCE WRAPPER (Pattern 38: Resilient Wrapper)
    # =========================================================================

    def _execute_with_resilience(
        self,
        operation: str,
        args: tuple,
        kwargs: dict
    ) -> Any:
        """
        Execute with full resilience: circuit breaker → retry → fallback.

        Flow:
        1. Check circuit breaker (fail fast if open)
        2. Create callable for the operation
        3. Wrap with retry (for transient errors)
        4. If circuit open or all retries fail, use fallback
        """
        agent_id = self._agent_for_operation[operation]

        # Create the raw operation callable
        def raw_operation():
            return self._execute_raw(operation, *args, **kwargs)

        # Wrap with circuit breaker (per-agent isolation)
        def with_circuit_breaker():
            return self._recovery.circuit_breaker(
                operation=raw_operation,
                operation_id=agent_id,
                failure_threshold=self._circuit_config["failure_threshold"],
                reset_timeout=self._circuit_config["reset_timeout"]
            )

        # Try with circuit breaker + retry logic
        try:
            result = self._recovery.retry_with_backoff(
                operation=with_circuit_breaker,
                max_retries=self._retry_config["max_retries"],
                base_delay=self._retry_config["base_delay"],
                max_delay=self._retry_config["max_delay"],
                jitter=self._retry_config["jitter"]
            )
            self._log_operation(operation, args, kwargs, result, "primary")
            return result
        except CircuitOpenError:
            # Circuit is open - fail fast, use fallback immediately
            fallback_result = self._get_fallback_value(operation, args, kwargs)
            self._log_operation(operation, args, kwargs, fallback_result, "circuit_open")
            return fallback_result
        except Exception:
            # All retries failed - use fallback
            fallback_result = self._get_fallback_value(operation, args, kwargs)
            self._log_operation(operation, args, kwargs, fallback_result, "fallback")
            return fallback_result

    # =========================================================================
    # MAIN EXECUTE
    # =========================================================================

    def execute(
        self,
        operation: str,
        *args,
        use_resilience: bool = True,
        **kwargs
    ) -> Any:
        """
        Execute operation with optional resilience stack.

        Resilience stack (when enabled):
        1. Retry with exponential backoff (up to 3 times)
        2. If all retries fail, use fallback
        (Circuit breaker added in Step 3)

        Args:
            operation: Operation name (e.g., "add", "reverse")
            *args: Arguments for the operation
            use_resilience: Whether to apply resilience (default True)
            **kwargs: Keyword arguments for the operation

        Returns:
            Operation result or fallback value

        Raises:
            ValueError: If operation unknown
        """
        self._validate_operation(operation)

        if not use_resilience:
            return self._execute_raw(operation, *args, **kwargs)

        return self._execute_with_resilience(operation, args, kwargs)

    # =========================================================================
    # FAILURE INJECTION (For Testing)
    # =========================================================================

    def _inject_failure(
        self,
        operation: str,
        failure_type: str = "transient",
        fail_count: int = 2
    ) -> None:
        """
        Inject failure behavior for testing resilience.

        Args:
            operation: Which operation to affect
            failure_type: "transient" (retryable) or "permanent"
            fail_count: How many times to fail before succeeding
        """
        self._injected_failures[operation] = {
            "type": failure_type,
            "remaining": fail_count
        }

    def _clear_failures(self) -> None:
        """Clear all injected failures (for test cleanup)."""
        self._injected_failures = {}

    # =========================================================================
    # DISCOVERY (Pattern 23)
    # =========================================================================

    def list_operations(self) -> list:
        """Return sorted list of all available operations."""
        return sorted(self._operations.keys())

    def list_operations_by_category(self) -> dict:
        """Return operations grouped by sub-agent."""
        return {
            "string": sorted([op for op, agent_id in self._agent_for_operation.items()
                             if agent_id == "string_agent"]),
            "datetime": sorted([op for op, agent_id in self._agent_for_operation.items()
                               if agent_id == "datetime_agent"]),
            "calculator": sorted([op for op, agent_id in self._agent_for_operation.items()
                                 if agent_id == "calculator_agent"]),
        }

    # =========================================================================
    # CIRCUIT BREAKER INSPECTION
    # =========================================================================

    def get_circuit_states(self) -> dict:
        """Return current state of all circuit breakers."""
        return {
            "string_agent": self._recovery.get_circuit_state("string_agent"),
            "datetime_agent": self._recovery.get_circuit_state("datetime_agent"),
            "calculator_agent": self._recovery.get_circuit_state("calculator_agent"),
        }

    def reset_circuit(self, agent_id: str) -> None:
        """Reset a circuit breaker to closed state."""
        self._recovery.reset_circuit(agent_id)

    # =========================================================================
    # LOGGING
    # =========================================================================

    def _log_operation(
        self,
        operation: str,
        args: tuple,
        kwargs: dict,
        result: Any,
        source: str
    ) -> None:
        """Log operation execution for debugging and metrics."""
        if not self._enable_logging:
            return

        log_entry = {
            "operation": operation,
            "agent": self._agent_for_operation[operation],
            "args": str(args)[:100],  # Truncate for safety
            "result_type": type(result).__name__,
            "source": source,  # "primary", "fallback", or "circuit_open"
            "timestamp": time.time(),
        }

        self._operation_log.append(log_entry)

        # Keep only last 100 entries
        if len(self._operation_log) > 100:
            self._operation_log = self._operation_log[-100:]

    def get_operation_log(self) -> list:
        """Return recent operation log."""
        return list(self._operation_log)

    def get_resilience_metrics(self) -> dict:
        """Return metrics from ErrorRecoveryAgent."""
        return self._recovery.get_metrics()

    def clear_operation_log(self) -> None:
        """Clear the operation log."""
        self._operation_log = []

    # =========================================================================
    # VERIFICATION
    # =========================================================================

    def verify(self) -> dict:
        """Run self-tests for basic functionality."""
        tests = [
            # Basic routing
            ("reverse routes correctly",
             lambda: self.execute("reverse", "hello", use_resilience=False), "olleh", False),
            ("uppercase routes correctly",
             lambda: self.execute("uppercase", "hello", use_resilience=False), "HELLO", False),
            ("add routes correctly",
             lambda: self.execute("add", 2, 3, use_resilience=False), 5.0, False),
            ("current_date returns 10 chars",
             lambda: len(self.execute("current_date", use_resilience=False)), 10, False),

            # Discovery
            ("list_operations returns 17",
             lambda: len(self.list_operations()), 17, False),
            ("categories has 3 keys",
             lambda: len(self.list_operations_by_category()), 3, False),

            # Validation
            ("unknown operation raises",
             lambda: self.execute("unknown"), ValueError, True),
            ("None operation raises",
             lambda: self.execute(None), ValueError, True),
        ]

        details = []
        passed = 0

        for desc, op, expected, expects_error in tests:
            try:
                result = op()
                if expects_error:
                    details.append({"test": desc, "result": "FAIL", "reason": "Expected error"})
                elif result == expected:
                    details.append({"test": desc, "result": "PASS"})
                    passed += 1
                else:
                    details.append({"test": desc, "result": "FAIL", "got": str(result)})
            except Exception as e:
                if expects_error and isinstance(e, expected):
                    details.append({"test": desc, "result": "PASS"})
                    passed += 1
                else:
                    details.append({"test": desc, "result": "FAIL", "error": str(e)})

        return {
            "status": "PASS" if passed == len(tests) else "FAIL",
            "tests_passed": passed,
            "tests_run": len(tests),
            "details": details
        }

    def verify_print(self) -> bool:
        """Print verification results."""
        result = self.verify()
        print("=" * 60)
        print(f"ResilientUtilityAgent v{self.version} Self-Verification")
        print("=" * 60)
        for d in result["details"]:
            sym = "✓" if d["result"] == "PASS" else "✗"
            print(f"  {sym} {d['test']}")
        print("-" * 60)
        print(f"✓ Status: {result['status']} ({result['tests_passed']}/{result['tests_run']})")
        print(f"  Operations: {len(self.list_operations())} available")
        print(f"  Categories: {list(self.list_operations_by_category().keys())}")
        print("=" * 60)
        return result["status"] == "PASS"


if __name__ == "__main__":
    agent = ResilientUtilityAgent()
    agent.verify_print()
