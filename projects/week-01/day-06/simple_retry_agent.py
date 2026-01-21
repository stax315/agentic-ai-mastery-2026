"""SimpleRetryAgent - Basic retry wrapper. V0.1: Fixed delay, no backoff."""
import time


class SimpleRetryAgent:
    """Simple retry wrapper for operations that might fail."""

    def __init__(self) -> None:
        self.version = "0.1"

    def retry(self, operation, max_retries: int = 3, delay: float = 1.0):
        """Retry operation with fixed delay. max_retries = total attempts."""
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
                if attempt < max_retries - 1:
                    time.sleep(delay)
        raise last_exception

    def verify(self) -> dict:
        """Run 5 self-tests, return results dict."""
        def fail_then_succeed():
            state = {"count": 0}
            def op():
                state["count"] += 1
                if state["count"] < 2:
                    raise RuntimeError("fail")
                return "ok"
            return self.retry(op, 3, 0.001)

        tests = [
            ("succeeds first try", lambda: self.retry(lambda: 42, 1, 0.001), 42, False),
            ("retry succeeds", fail_then_succeed, "ok", False),
            ("exhausts retries", lambda: self.retry(lambda: 1/0, 2, 0.001), ZeroDivisionError, True),
            ("rejects max_retries=0", lambda: self.retry(lambda: 1, 0), ValueError, True),
            ("rejects delay=-1", lambda: self.retry(lambda: 1, 3, -1), ValueError, True),
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
                    results.append({"test": desc, "status": "FAIL"})
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
        print(f"\nSimpleRetryAgent v{self.version} Verification")
        print("=" * 45)
        for d in r["details"]:
            print(f"[{d['status']}] {d['test']}")
        print("=" * 45)
        print(f"Result: {r['passed']}/{r['total']} passed - {r['status']}")
        return r["status"] == "PASS"


if __name__ == "__main__":
    SimpleRetryAgent().verify_print()
