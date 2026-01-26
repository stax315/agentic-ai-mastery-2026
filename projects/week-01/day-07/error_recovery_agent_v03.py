"""ErrorRecoveryAgent V0.3 - Circuit Breaker. Stops sustained failures early."""
import time
RETRYABLE_ERRORS = (TimeoutError, ConnectionError, OSError)
PERMANENT_ERRORS = (ValueError, TypeError, KeyError, AttributeError, ZeroDivisionError, PermissionError)

class CircuitOpenError(Exception): pass

class ErrorRecoveryAgent:
    def __init__(self, failure_threshold: int = 3) -> None:
        self.version, self._consecutive_failures, self._circuit_open = "0.3", 0, False
        self._failure_threshold = failure_threshold

    @property
    def circuit_open(self) -> bool: return self._circuit_open
    @property
    def consecutive_failures(self) -> int: return self._consecutive_failures

    def reset_circuit(self) -> None:
        self._consecutive_failures, self._circuit_open = 0, False

    def _is_retryable(self, error: Exception, custom_classifier=None) -> bool:
        if custom_classifier: return custom_classifier(error)
        if isinstance(error, PERMANENT_ERRORS): return False
        return isinstance(error, RETRYABLE_ERRORS)

    def retry(self, operation, max_retries: int = 3, delay: float = 1.0, is_retryable=None):
        if max_retries < 1: raise ValueError("max_retries must be >= 1")
        if delay <= 0: raise ValueError("delay must be > 0")
        if self._circuit_open: raise CircuitOpenError(f"Circuit open after {self._failure_threshold} failures")
        last_exception = None
        for attempt in range(max_retries):
            try:
                result = operation()
                self._consecutive_failures, self._circuit_open = 0, False
                return result
            except Exception as e:
                last_exception = e
                if not self._is_retryable(e, is_retryable): raise
                self._consecutive_failures += 1
                if self._consecutive_failures >= self._failure_threshold: self._circuit_open = True
                if attempt < max_retries - 1: time.sleep(delay)
        raise last_exception

    def verify(self) -> dict:
        def fail_then_succeed():
            state = {"count": 0}
            def op():
                state["count"] += 1
                if state["count"] < 2: raise TimeoutError("t")
                return "ok"
            return self.retry(op, 3, 0.001)
        def count_perm():
            state = {"count": 0}
            def op(): state["count"] += 1; raise ValueError("p")
            try: self.retry(op, 3, 0.001)
            except ValueError: pass
            return state["count"]
        def test_circuit_opens():
            a = ErrorRecoveryAgent(3)
            for _ in range(3):
                try: a.retry(lambda: (_ for _ in ()).throw(TimeoutError()), 1, 0.001)
                except TimeoutError: pass
            return a.circuit_open
        def test_circuit_blocks():
            a = ErrorRecoveryAgent(1)
            try: a.retry(lambda: (_ for _ in ()).throw(TimeoutError()), 1, 0.001)
            except TimeoutError: pass
            try: a.retry(lambda: "ok", 1, 0.001); return False
            except CircuitOpenError: return True
        def test_success_resets():
            a = ErrorRecoveryAgent(3); a._consecutive_failures = 2
            a.retry(lambda: "ok", 1, 0.001)
            return a.consecutive_failures == 0
        def test_perm_no_circuit():
            a = ErrorRecoveryAgent(3)
            for _ in range(5):
                try: a.retry(lambda: (_ for _ in ()).throw(ValueError()), 1, 0.001)
                except ValueError: pass
            return not a.circuit_open and a.consecutive_failures == 0
        def test_manual_reset():
            a = ErrorRecoveryAgent(1); a._circuit_open, a._consecutive_failures = True, 5
            a.reset_circuit()
            return not a.circuit_open and a.consecutive_failures == 0
        tests = [
            ("succeeds first try", lambda: self.retry(lambda: 42, 1, 0.001), 42, False),
            ("retry succeeds", fail_then_succeed, "ok", False),
            ("exhausts retries", lambda: self.retry(lambda: (_ for _ in ()).throw(TimeoutError()), 2, 0.001), TimeoutError, True),
            ("permanent no retry", count_perm, 1, False),
            ("custom classifier", lambda: self.retry(lambda: (_ for _ in ()).throw(ValueError()), 3, 0.001, is_retryable=lambda e: True), ValueError, True),
            ("rejects max_retries=0", lambda: self.retry(lambda: 1, 0), ValueError, True),
            ("rejects delay=-1", lambda: self.retry(lambda: 1, 3, -1), ValueError, True),
            ("unknown no retry", lambda: self._is_retryable(RuntimeError()), False, False),
            ("circuit opens", test_circuit_opens, True, False),
            ("circuit blocks", test_circuit_blocks, True, False),
            ("success resets", test_success_resets, True, False),
            ("permanent no circuit", test_perm_no_circuit, True, False),
            ("manual reset", test_manual_reset, True, False),
        ]
        results, passed, failed = [], 0, 0
        for desc, func, expected, should_raise in tests:
            try:
                result = func()
                if should_raise: results.append({"test": desc, "status": "FAIL"}); failed += 1
                elif result == expected: results.append({"test": desc, "status": "PASS"}); passed += 1
                else: results.append({"test": desc, "status": "FAIL", "got": result}); failed += 1
            except Exception as e:
                if should_raise and isinstance(e, expected): results.append({"test": desc, "status": "PASS"}); passed += 1
                else: results.append({"test": desc, "status": "FAIL", "error": str(e)}); failed += 1
        return {"status": "PASS" if failed == 0 else "FAIL", "passed": passed, "failed": failed, "total": len(tests), "details": results}

    def verify_print(self) -> bool:
        r = self.verify()
        print(f"\nErrorRecoveryAgent v{self.version} Verification\n" + "="*50)
        for d in r["details"]: print(f"[{d['status']}] {d['test']}")
        print("="*50 + f"\nResult: {r['passed']}/{r['total']} passed - {r['status']}")
        return r["status"] == "PASS"

if __name__ == "__main__": ErrorRecoveryAgent().verify_print()
