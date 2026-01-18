"""
ErrorRecoveryAgent - A teaching agent for resilience patterns.

Day 3 Theme: Learning from Intentional Failures

This agent intentionally simulates common failures and demonstrates
production-ready recovery strategies.

Public Methods:
    Failure Simulators:
    - simulate_timeout(delay_seconds) -> Raises TimeoutError
    - simulate_rate_limit() -> Raises RateLimitError
    - simulate_intermittent_failure(failure_rate) -> Fails randomly
    - simulate_bad_response() -> Returns malformed data
    - simulate_resource_exhaustion() -> Raises MemoryError

    Recovery Strategies:
    - retry_with_backoff(operation, max_retries, base_delay) -> Result or raises
    - circuit_breaker(operation, failure_threshold, reset_timeout) -> Result or raises
    - fallback_strategy(primary, fallback, default) -> Result from first success
    - graceful_degradation(operations) -> Partial results dict
    - timeout_wrapper(operation, timeout_seconds) -> Result or raises

    Verification:
    - verify() -> dict
    - verify_print() -> bool
"""

import time
import random
import threading
from enum import Enum
from typing import Callable, Any, Optional
from dataclasses import dataclass, field


# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================

class TransientError(Exception):
    """Error that might succeed on retry (network timeout, rate limit)."""
    pass


class PermanentError(Exception):
    """Error that will NOT succeed on retry (invalid input, auth failure)."""
    pass


class RateLimitError(TransientError):
    """Simulates HTTP 429 Too Many Requests."""
    def __init__(self, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(f"Rate limited. Retry after {retry_after} seconds")


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open (rejecting requests)."""
    pass


# =============================================================================
# CIRCUIT BREAKER STATE MACHINE
# =============================================================================

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing fast, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerState:
    """Tracks state for a single circuit breaker."""
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: float = 0.0
    failure_threshold: int = 5
    reset_timeout: float = 30.0


# =============================================================================
# ERROR RECOVERY AGENT
# =============================================================================

class ErrorRecoveryAgent:
    """
    An agent that simulates failures and demonstrates recovery patterns.

    Teaches resilience through controlled, intentional failures.
    """

    def __init__(self) -> None:
        """Initialize the ErrorRecoveryAgent."""
        self.version = "1.0"

        # Circuit breaker state tracking (one per operation_id)
        self._circuit_states: dict[str, CircuitBreakerState] = {}

        # Metrics for learning and monitoring
        self._retry_metrics = {"attempts": 0, "successes": 0, "failures": 0}
        self._circuit_metrics = {"opened": 0, "closed": 0, "half_opened": 0}

        # For testing: track last backoff delay
        self._last_backoff_delay: float = 0.0

    # =========================================================================
    # VALIDATION HELPERS (Following Day 1-2 patterns)
    # =========================================================================

    def _validate_positive_number(self, value, param_name: str) -> None:
        """Validate value is a positive number."""
        if value is None:
            raise ValueError(f"{param_name} cannot be None")
        if type(value) is bool:
            raise ValueError(f"{param_name} must be a number, got bool")
        if type(value) not in (int, float):
            raise ValueError(f"{param_name} must be a number, got {type(value).__name__}")
        if value <= 0:
            raise ValueError(f"{param_name} must be positive, got {value}")

    def _validate_positive_integer(self, value, param_name: str) -> None:
        """Validate value is a positive integer."""
        if value is None:
            raise ValueError(f"{param_name} cannot be None")
        if type(value) is bool:
            raise ValueError(f"{param_name} must be an integer, got bool")
        if not isinstance(value, int):
            raise ValueError(f"{param_name} must be an integer, got {type(value).__name__}")
        if value <= 0:
            raise ValueError(f"{param_name} must be positive, got {value}")

    def _validate_probability(self, value, param_name: str) -> None:
        """Validate value is a probability (0.0-1.0)."""
        if value is None:
            raise ValueError(f"{param_name} cannot be None")
        if type(value) is bool:
            raise ValueError(f"{param_name} must be a number, got bool")
        if type(value) not in (int, float):
            raise ValueError(f"{param_name} must be a number, got {type(value).__name__}")
        if value < 0 or value > 1:
            raise ValueError(f"{param_name} must be between 0.0 and 1.0, got {value}")

    # =========================================================================
    # FAILURE SIMULATORS
    # =========================================================================

    def simulate_timeout(self, delay_seconds: float = 0.1) -> None:
        """
        Simulate an operation that times out.

        Args:
            delay_seconds: How long to wait before raising (simulates slow service)

        Raises:
            TimeoutError: Always (simulating network timeout)

        Example:
            agent.simulate_timeout(2.0)  # Waits 2s, then raises TimeoutError

        Learning: Operations need time limits. Never wait forever.
        """
        self._validate_positive_number(delay_seconds, "delay_seconds")
        time.sleep(delay_seconds)
        raise TimeoutError(f"Operation timed out after {delay_seconds} seconds")

    def simulate_rate_limit(self, retry_after: int = 60) -> None:
        """
        Simulate HTTP 429 rate limiting.

        Args:
            retry_after: Seconds until rate limit resets

        Raises:
            RateLimitError: Always (simulating API rate limit)

        Example:
            agent.simulate_rate_limit(30)  # Raises with retry_after=30

        Learning: APIs have limits. Respect Retry-After headers.
        """
        self._validate_positive_integer(retry_after, "retry_after")
        raise RateLimitError(retry_after)

    def simulate_intermittent_failure(
        self,
        failure_rate: float = 0.5,
        success_value: Any = "success"
    ) -> Any:
        """
        Simulate a flaky service that fails randomly.

        Args:
            failure_rate: Probability of failure (0.0-1.0)
            success_value: What to return on success

        Returns:
            success_value if not failing this time

        Raises:
            TransientError: Randomly based on failure_rate

        Example:
            result = agent.simulate_intermittent_failure(0.5)  # 50% fail rate

        Learning: Real systems are flaky. Retries help with transient failures.
        """
        self._validate_probability(failure_rate, "failure_rate")

        if random.random() < failure_rate:
            raise TransientError("Intermittent failure (random)")
        return success_value

    def simulate_bad_response(self, response_type: str = "malformed") -> dict:
        """
        Simulate receiving malformed or unexpected data.

        Args:
            response_type: Type of bad response to simulate
                - "malformed": Missing required fields
                - "wrong_type": Wrong data types
                - "empty": Empty response
                - "null": Null/None values where unexpected

        Returns:
            A problematic response dict for testing defensive parsing

        Example:
            bad_data = agent.simulate_bad_response("malformed")

        Learning: Never trust external data. Always validate responses.
        """
        bad_responses = {
            "malformed": {"data": None, "error": "missing_field"},
            "wrong_type": {"count": "not_a_number", "items": "not_a_list"},
            "empty": {},
            "null": {"user": None, "settings": None}
        }

        if response_type not in bad_responses:
            available = ", ".join(sorted(bad_responses.keys()))
            raise ValueError(f"Unknown response_type: '{response_type}'. Available: {available}")

        return bad_responses[response_type]

    def simulate_resource_exhaustion(self, resource_type: str = "memory") -> None:
        """
        Simulate resource exhaustion scenarios.

        Args:
            resource_type: Type of resource exhausted
                - "memory": Simulates MemoryError
                - "connections": Simulates connection pool exhaustion
                - "disk": Simulates disk full

        Raises:
            Appropriate error based on resource_type

        Example:
            agent.simulate_resource_exhaustion("memory")

        Learning: Resources are finite. Plan for exhaustion.
        """
        errors = {
            "memory": MemoryError("Simulated memory exhaustion"),
            "connections": ConnectionError("Connection pool exhausted"),
            "disk": OSError("No space left on device")
        }

        if resource_type not in errors:
            available = ", ".join(sorted(errors.keys()))
            raise ValueError(f"Unknown resource_type: '{resource_type}'. Available: {available}")

        raise errors[resource_type]

    # =========================================================================
    # RECOVERY STRATEGIES
    # =========================================================================

    def retry_with_backoff(
        self,
        operation: Callable[[], Any],
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        jitter: bool = True
    ) -> Any:
        """
        Retry an operation with exponential backoff.

        Backoff formula: delay = min(base_delay * 2^attempt, max_delay)
        With jitter: delay = delay * random(0.5, 1.5)

        Args:
            operation: Callable to retry (no arguments)
            max_retries: Maximum retry attempts (default 3)
            base_delay: Initial delay in seconds (default 1.0)
            max_delay: Maximum delay cap (default 60.0)
            jitter: Add randomness to prevent thundering herd (default True)

        Returns:
            Result from operation if successful

        Raises:
            Last exception if all retries exhausted
            PermanentError: Immediately without retry

        Example:
            def flaky_api_call():
                return external_service.get_data()

            result = agent.retry_with_backoff(flaky_api_call, max_retries=5)

        Learning: Transient failures often resolve with time. Exponential backoff
        prevents overwhelming recovering services.
        """
        self._validate_positive_integer(max_retries, "max_retries")
        self._validate_positive_number(base_delay, "base_delay")
        self._validate_positive_number(max_delay, "max_delay")

        last_exception = None

        for attempt in range(max_retries + 1):  # +1 for initial attempt
            try:
                self._retry_metrics["attempts"] += 1
                result = operation()
                self._retry_metrics["successes"] += 1
                return result

            except PermanentError:
                # Don't retry permanent errors - fail immediately
                self._retry_metrics["failures"] += 1
                raise

            except Exception as e:
                last_exception = e

                if attempt == max_retries:
                    # No more retries
                    self._retry_metrics["failures"] += 1
                    raise

                # Calculate backoff delay: 2^attempt, capped at max_delay
                delay = min(base_delay * (2 ** attempt), max_delay)

                if jitter:
                    # Add randomness to prevent thundering herd
                    delay = delay * random.uniform(0.5, 1.5)

                # Store for testing verification
                self._last_backoff_delay = delay

                time.sleep(delay)

        # Should not reach here, but safety
        if last_exception:
            raise last_exception

    def circuit_breaker(
        self,
        operation: Callable[[], Any],
        operation_id: str = "default",
        failure_threshold: int = 5,
        reset_timeout: float = 30.0
    ) -> Any:
        """
        Execute operation with circuit breaker protection.

        State Machine:
        - CLOSED: Normal operation, track failures
        - OPEN: Reject immediately (fail fast)
        - HALF_OPEN: Allow one request to test recovery

        State Transitions:
        - CLOSED --[failures >= threshold]--> OPEN
        - OPEN --[timeout elapsed]--> HALF_OPEN
        - HALF_OPEN --[success]--> CLOSED
        - HALF_OPEN --[failure]--> OPEN

        Args:
            operation: Callable to execute
            operation_id: Identifier for separate circuit tracking
            failure_threshold: Failures before opening circuit (default 5)
            reset_timeout: Seconds before trying half-open (default 30.0)

        Returns:
            Result from operation if successful

        Raises:
            CircuitOpenError: If circuit is open
            Original exception: If operation fails

        Example:
            def external_api():
                return api.call()

            result = agent.circuit_breaker(external_api, "api_v1")

        Learning: Prevents cascade failures. Gives failing services time to recover.
        """
        # Get or create circuit state for this operation
        if operation_id not in self._circuit_states:
            self._circuit_states[operation_id] = CircuitBreakerState(
                failure_threshold=failure_threshold,
                reset_timeout=reset_timeout
            )

        circuit = self._circuit_states[operation_id]
        current_time = time.time()

        # State: OPEN - Check if should move to HALF_OPEN
        if circuit.state == CircuitState.OPEN:
            time_since_failure = current_time - circuit.last_failure_time

            if time_since_failure >= circuit.reset_timeout:
                # Transition to HALF_OPEN
                circuit.state = CircuitState.HALF_OPEN
                self._circuit_metrics["half_opened"] += 1
            else:
                # Still open - fail fast
                raise CircuitOpenError(
                    f"Circuit '{operation_id}' is OPEN. "
                    f"Retry after {circuit.reset_timeout - time_since_failure:.1f}s"
                )

        # State: CLOSED or HALF_OPEN - Execute operation
        try:
            result = operation()

            # Success handling
            if circuit.state == CircuitState.HALF_OPEN:
                # Recovery confirmed - close circuit
                circuit.state = CircuitState.CLOSED
                circuit.failure_count = 0
                self._circuit_metrics["closed"] += 1

            circuit.success_count += 1
            return result

        except Exception as e:
            # Failure handling
            circuit.failure_count += 1
            circuit.last_failure_time = current_time

            if circuit.state == CircuitState.HALF_OPEN:
                # Still failing - reopen circuit
                circuit.state = CircuitState.OPEN
                self._circuit_metrics["opened"] += 1

            elif circuit.failure_count >= circuit.failure_threshold:
                # Threshold reached - open circuit
                circuit.state = CircuitState.OPEN
                self._circuit_metrics["opened"] += 1

            raise

    def fallback_strategy(
        self,
        primary: Callable[[], Any],
        fallback: Optional[Callable[[], Any]] = None,
        default: Any = None
    ) -> tuple[Any, str]:
        """
        Execute with fallback chain on failure.

        Tries in order: primary -> fallback -> default

        Args:
            primary: First choice operation
            fallback: Second choice if primary fails (optional)
            default: Last resort value if all fail (optional)

        Returns:
            Tuple of (result, source) where source is "primary", "fallback", or "default"

        Raises:
            Exception: If all options fail and no default provided

        Example:
            result, source = agent.fallback_strategy(
                primary=lambda: api.fetch_user(),
                fallback=lambda: cache.get("user"),
                default={"name": "Guest"}
            )
            print(f"Got {result} from {source}")

        Learning: Graceful degradation is better than complete failure.
        """
        primary_error = None

        # Try primary
        try:
            result = primary()
            return (result, "primary")
        except Exception as e:
            primary_error = e

        # Try fallback if provided
        if fallback is not None:
            try:
                result = fallback()
                return (result, "fallback")
            except Exception:
                pass  # Fall through to default

        # Use default if provided
        if default is not None:
            return (default, "default")

        # All options exhausted - raise original error
        raise primary_error

    def graceful_degradation(
        self,
        operations: dict[str, Callable[[], Any]]
    ) -> dict[str, Any]:
        """
        Execute multiple operations, returning partial results on failures.

        Unlike normal execution where one failure fails everything,
        this collects what succeeds and reports what failed.

        Args:
            operations: Dict mapping operation names to callables

        Returns:
            Dict with keys:
            - "results": Dict of successful {name: result}
            - "errors": Dict of failed {name: error_message}
            - "success_rate": Float 0.0-1.0

        Example:
            result = agent.graceful_degradation({
                "user": lambda: api.get_user(),
                "settings": lambda: api.get_settings(),
                "notifications": lambda: api.get_notifications()
            })
            # If notifications fails:
            # {
            #     "results": {"user": {...}, "settings": {...}},
            #     "errors": {"notifications": "Connection timeout"},
            #     "success_rate": 0.67
            # }

        Learning: Partial success is often acceptable. Don't let one failure
        break everything.
        """
        results = {}
        errors = {}

        for name, operation in operations.items():
            try:
                results[name] = operation()
            except Exception as e:
                errors[name] = str(e)

        total = len(operations)
        success_rate = len(results) / total if total > 0 else 0.0

        return {
            "results": results,
            "errors": errors,
            "success_rate": success_rate
        }

    def timeout_wrapper(
        self,
        operation: Callable[[], Any],
        timeout_seconds: float = 5.0
    ) -> Any:
        """
        Execute operation with a timeout.

        Note: Uses threading for timeout. For production, consider
        using async/await or signal-based timeouts.

        Args:
            operation: Callable to execute
            timeout_seconds: Maximum time to wait

        Returns:
            Result from operation if completed in time

        Raises:
            TimeoutError: If operation exceeds timeout

        Example:
            def slow_api_call():
                return api.get_large_dataset()

            result = agent.timeout_wrapper(slow_api_call, timeout_seconds=10)

        Learning: Every external operation needs a timeout. Never wait forever.
        """
        self._validate_positive_number(timeout_seconds, "timeout_seconds")

        result = [None]
        exception = [None]
        completed = threading.Event()

        def wrapper():
            try:
                result[0] = operation()
            except Exception as e:
                exception[0] = e
            finally:
                completed.set()

        thread = threading.Thread(target=wrapper)
        thread.daemon = True
        thread.start()

        if not completed.wait(timeout_seconds):
            raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")

        if exception[0] is not None:
            raise exception[0]

        return result[0]

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def get_circuit_state(self, operation_id: str) -> str:
        """Get the current state of a circuit breaker."""
        if operation_id not in self._circuit_states:
            return "not_initialized"
        return self._circuit_states[operation_id].state.value

    def reset_circuit(self, operation_id: str) -> None:
        """Reset a circuit breaker to CLOSED state."""
        if operation_id in self._circuit_states:
            self._circuit_states[operation_id].state = CircuitState.CLOSED
            self._circuit_states[operation_id].failure_count = 0

    def get_metrics(self) -> dict:
        """Return current metrics for retry and circuit breaker operations."""
        return {
            "retry": dict(self._retry_metrics),
            "circuit_breaker": dict(self._circuit_metrics)
        }

    def reset_metrics(self) -> None:
        """Reset all metrics to zero."""
        self._retry_metrics = {"attempts": 0, "successes": 0, "failures": 0}
        self._circuit_metrics = {"opened": 0, "closed": 0, "half_opened": 0}

    # =========================================================================
    # VERIFICATION
    # =========================================================================

    def verify(self) -> dict:
        """
        Run self-tests for all failure/recovery scenarios.

        Returns:
            Dict with status, tests_run, tests_passed, tests_failed, details
        """
        # Helper to raise an exception
        def raise_error():
            raise TransientError("test error")

        tests = [
            # Failure simulators
            ("simulate_timeout raises TimeoutError",
             lambda: self.simulate_timeout(0.001), TimeoutError, True),

            ("simulate_rate_limit raises RateLimitError",
             lambda: self.simulate_rate_limit(60), RateLimitError, True),

            ("simulate_intermittent_failure with 0.0 rate succeeds",
             lambda: self.simulate_intermittent_failure(0.0, "ok"), "ok", False),

            ("simulate_intermittent_failure with 1.0 rate fails",
             lambda: self.simulate_intermittent_failure(1.0), TransientError, True),

            ("simulate_bad_response returns dict",
             lambda: isinstance(self.simulate_bad_response("malformed"), dict), True, False),

            ("simulate_bad_response unknown type raises ValueError",
             lambda: self.simulate_bad_response("invalid"), ValueError, True),

            ("simulate_resource_exhaustion memory raises MemoryError",
             lambda: self.simulate_resource_exhaustion("memory"), MemoryError, True),

            # Recovery: retry succeeds on good operation
            ("retry_with_backoff succeeds on good operation",
             lambda: self.retry_with_backoff(lambda: 42, max_retries=1, base_delay=0.001), 42, False),

            # Recovery: fallback returns primary on success
            ("fallback returns primary on success",
             lambda: self.fallback_strategy(lambda: "primary_result")[1], "primary", False),

            # Recovery: fallback returns fallback on primary failure
            ("fallback returns fallback on primary failure",
             lambda: self.fallback_strategy(
                 primary=raise_error,
                 fallback=lambda: "backup"
             )[1], "fallback", False),

            # Recovery: fallback returns default on all failures
            ("fallback returns default on all failures",
             lambda: self.fallback_strategy(
                 primary=raise_error,
                 fallback=raise_error,
                 default="default_value"
             )[1], "default", False),

            # Recovery: graceful degradation returns partial results
            ("graceful_degradation handles partial failure",
             lambda: self.graceful_degradation({
                 "good": lambda: "ok",
                 "bad": raise_error
             })["success_rate"], 0.5, False),

            # Circuit breaker succeeds normally
            ("circuit_breaker succeeds normally",
             lambda: self.circuit_breaker(lambda: "success", "verify_test"), "success", False),

            # Timeout wrapper succeeds on fast operation
            ("timeout_wrapper succeeds on fast operation",
             lambda: self.timeout_wrapper(lambda: "fast", timeout_seconds=1.0), "fast", False),
        ]

        details = []
        tests_passed = 0
        tests_failed = 0

        for description, operation, expected, expects_error in tests:
            try:
                result = operation()

                if expects_error:
                    details.append({
                        "test": description,
                        "result": "FAIL",
                        "reason": f"Expected {expected.__name__} error, got result: {result}"
                    })
                    tests_failed += 1
                elif result == expected:
                    details.append({"test": description, "result": "PASS"})
                    tests_passed += 1
                else:
                    details.append({
                        "test": description,
                        "result": "FAIL",
                        "reason": f"Expected {expected}, got {result}"
                    })
                    tests_failed += 1

            except Exception as e:
                if expects_error:
                    if isinstance(e, expected):
                        details.append({"test": description, "result": "PASS"})
                        tests_passed += 1
                    else:
                        details.append({
                            "test": description,
                            "result": "FAIL",
                            "reason": f"Expected {expected.__name__}, got {type(e).__name__}: {e}"
                        })
                        tests_failed += 1
                else:
                    details.append({
                        "test": description,
                        "result": "FAIL",
                        "reason": f"Unexpected error: {type(e).__name__}: {e}"
                    })
                    tests_failed += 1

        return {
            "status": "PASS" if tests_failed == 0 else "FAIL",
            "tests_run": len(tests),
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
            "details": details
        }

    def verify_print(self) -> bool:
        """
        Run self-tests and print readable output.

        Returns:
            True if all tests pass, False otherwise
        """
        result = self.verify()

        print("=" * 60)
        print(f"ErrorRecoveryAgent v{self.version} Self-Verification")
        print("=" * 60)
        print()

        for detail in result["details"]:
            symbol = "\u2713" if detail["result"] == "PASS" else "\u2717"
            print(f"  {symbol} {detail['test']}")
            if detail["result"] == "FAIL" and "reason" in detail:
                print(f"      Reason: {detail['reason']}")

        print()
        print("-" * 60)
        status_symbol = "\u2713" if result["status"] == "PASS" else "\u2717"
        print(f"{status_symbol} Status: {result['status']}")
        print(f"  Tests: {result['tests_passed']}/{result['tests_run']} passed")

        if result["tests_failed"] > 0:
            print(f"  Failed: {result['tests_failed']}")

        print("=" * 60)

        return result["status"] == "PASS"


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    agent = ErrorRecoveryAgent()
    agent.verify_print()
