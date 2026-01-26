"""ErrorRecoveryAgent V0.2 - Error Classification. Permanent errors fail immediately."""
import time

RETRYABLE_ERRORS = (TimeoutError, ConnectionError, OSError)
PERMANENT_ERRORS = (ValueError, TypeError, KeyError, AttributeError, ZeroDivisionError, PermissionError)

class ErrorRecoveryAgent:
    """Retry wrapper with error classification."""

    def __init__(self) -> None:
        self.version = "0.2"

    def _is_retryable(self, error: Exception, custom_classifier=None) -> bool:
        """Classify error: True=retry, False=permanent."""
        if custom_classifier:
            return custom_classifier(error)
        if isinstance(error, PERMANENT_ERRORS):
            return False
        if isinstance(error, RETRYABLE_ERRORS):
            return True
        return False  # Unknown = don't retry (conservative)

    def retry(self, operation, max_retries: int = 3, delay: float = 1.0, is_retryable=None):
        """Retry operation with error classification."""
        if max_retries < 1:
            raise ValueError("max_retries must be >= 1")
        if delay <= 0:
            raise ValueError("delay must be > 0")
        last_exception = None
        for attempt in range(max_retries):
            try:
                return operation()
            except Exception as e:
                last_exception = e
                if not self._is_retryable(e, is_retryable):
                    raise  # Permanent - fail immediately
                if attempt < max_retries - 1:
                    time.sleep(delay)
        raise last_exception

    def verify(self) -> dict:
        """Run 8 self-tests, return results dict."""
        def fail_then_succeed():
            state = {"count": 0}
            def op():
                state["count"] += 1
                if state["count"] < 2: raise TimeoutError("transient")
                return "ok"
            return self.retry(op, 3, 0.001)
        def count_attempts_permanent():
            state = {"count": 0}
            def op():
                state["count"] += 1
                raise ValueError("permanent")
            try:
                self.retry(op, 3, 0.001)
            except ValueError:
                pass
            return state["count"]

        tests = [
            ("succeeds first try", lambda: self.retry(lambda: 42, 1, 0.001), 42, False),
            ("retry succeeds (retryable)", fail_then_succeed, "ok", False),
            ("exhausts retries", lambda: self.retry(lambda: (_ for _ in ()).throw(TimeoutError("t")), 2, 0.001), TimeoutError, True),
            ("permanent error no retry", count_attempts_permanent, 1, False),
            ("custom classifier", lambda: self.retry(lambda: (_ for _ in ()).throw(ValueError("v")), 3, 0.001, is_retryable=lambda e: True), ValueError, True),
            ("rejects max_retries=0", lambda: self.retry(lambda: 1, 0), ValueError, True),
            ("rejects delay=-1", lambda: self.retry(lambda: 1, 3, -1), ValueError, True),
            ("unknown error no retry", lambda: self._is_retryable(RuntimeError("unknown")), False, False),
        ]
        results, passed, failed = [], 0, 0
        for desc, func, expected, should_raise in tests:
            try:
                result = func()
                if should_raise:
                    results.append({"test": desc, "status": "FAIL"})
                    failed += 1
                elif result == expected:
                    results.append({"test": desc, "status": "PASS"})
                    passed += 1
                else:
                    results.append({"test": desc, "status": "FAIL", "got": result})
                    failed += 1
            except Exception as e:
                if should_raise and isinstance(e, expected):
                    results.append({"test": desc, "status": "PASS"})
                    passed += 1
                else:
                    results.append({"test": desc, "status": "FAIL", "error": str(e)})
                    failed += 1
        return {"status": "PASS" if failed == 0 else "FAIL", "passed": passed, "failed": failed, "total": len(tests), "details": results}

    def verify_print(self) -> bool:
        """Run self-tests with human-readable output."""
        r = self.verify()
        print(f"\nErrorRecoveryAgent v{self.version} Verification")
        print("=" * 50)
        for d in r["details"]:
            print(f"[{d['status']}] {d['test']}")
        print("=" * 50)
        print(f"Result: {r['passed']}/{r['total']} passed - {r['status']}")
        return r["status"] == "PASS"

if __name__ == "__main__":
    ErrorRecoveryAgent().verify_print()
