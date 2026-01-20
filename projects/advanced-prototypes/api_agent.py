"""
APIAgent - Simple mock HTTP with retry pattern.

Day 4 Session 2 - Learning API retry patterns, not production HTTP.
All responses are mocked. No external dependencies.

Methods:
- get(url) -> dict
- post(url, data) -> dict
- retry_request(method, url, max_retries=3, **kwargs) -> dict
- verify() -> dict
"""

import time


class APIAgent:
    """Simple API agent with mocked responses. Learning pattern, not production."""

    def __init__(self) -> None:
        """Initialize the agent."""
        self.version = "1.0"
        self._fail_count = {}  # Track failures for flaky simulation

    def get(self, url: str) -> dict:
        """
        Mock GET request.

        Args:
            url: URL to fetch

        Returns:
            Dict with status and data

        Raises:
            ValueError: If url is None or not a string
            ConnectionError: If url is error endpoint
        """
        if url is None:
            raise ValueError("url cannot be None")
        if not isinstance(url, str):
            raise ValueError(f"url must be string, got {type(url).__name__}")

        # Hardcoded mock responses
        if url == "https://api.example.com/users":
            return {"users": ["alice", "bob"], "status": 200}
        if url == "https://api.example.com/posts":
            return {"posts": [], "status": 200}
        if url == "https://api.example.com/error":
            raise ConnectionError("Server error")
        if url == "https://api.example.com/flaky":
            return self._handle_flaky("GET", url)

        return {"error": "Not found", "status": 404}

    def post(self, url: str, data: dict) -> dict:
        """
        Mock POST request.

        Args:
            url: URL to post to
            data: Data to send

        Returns:
            Dict with status and data

        Raises:
            ValueError: If url or data is None
            ConnectionError: If url is error endpoint
        """
        if url is None:
            raise ValueError("url cannot be None")
        if not isinstance(url, str):
            raise ValueError(f"url must be string, got {type(url).__name__}")
        if data is None:
            raise ValueError("data cannot be None")

        # Mock: echo back data with 201
        if url == "https://api.example.com/users":
            return {"created": data, "status": 201}
        if url == "https://api.example.com/error":
            raise ConnectionError("Server error")
        if url == "https://api.example.com/flaky":
            return self._handle_flaky("POST", url)

        return {"error": "Not found", "status": 404}

    def retry_request(self, method: str, url: str, max_retries: int = 3, **kwargs) -> dict:
        """
        Retry request with exponential backoff (Day 3 pattern).

        Args:
            method: HTTP method (GET or POST)
            url: URL to request
            max_retries: Maximum retry attempts (default 3)
            **kwargs: Additional args (data for POST)

        Returns:
            Response dict from successful request

        Raises:
            ValueError: If method is unknown
            ConnectionError: If all retries fail
        """
        if method is None:
            raise ValueError("method cannot be None")

        last_error = None
        for attempt in range(max_retries):
            try:
                if method.upper() == "GET":
                    return self.get(url)
                elif method.upper() == "POST":
                    return self.post(url, kwargs.get("data", {}))
                else:
                    raise ValueError(f"Unknown method: {method}")
            except ConnectionError as e:
                last_error = e
                if attempt < max_retries - 1:
                    delay = 2 ** attempt  # 1s, 2s, 4s
                    time.sleep(delay)

        raise last_error or ConnectionError("All retries failed")

    def _handle_flaky(self, method: str, url: str) -> dict:
        """
        Simulate transient failures - fail first 2 calls, succeed on 3rd.

        Args:
            method: HTTP method
            url: URL being accessed

        Returns:
            Success dict on 3rd+ call

        Raises:
            ConnectionError: On first 2 calls
        """
        key = f"{method}:{url}"
        self._fail_count[key] = self._fail_count.get(key, 0) + 1

        if self._fail_count[key] <= 2:
            raise ConnectionError("Temporary failure")

        self._fail_count[key] = 0  # Reset for next test
        return {"data": "success", "status": 200}

    def reset_flaky(self) -> None:
        """Reset flaky endpoint state for testing."""
        self._fail_count = {}

    def verify(self) -> dict:
        """
        Run self-tests.

        Returns:
            Dict with status, tests_passed, tests_run, details
        """
        tests = []

        # Test 1: GET users
        try:
            result = self.get("https://api.example.com/users")
            passed = result["status"] == 200 and "users" in result
            tests.append({"test": "GET users returns 200", "result": "PASS" if passed else "FAIL"})
        except Exception as e:
            tests.append({"test": "GET users returns 200", "result": "FAIL", "error": str(e)})

        # Test 2: GET unknown returns 404
        try:
            result = self.get("https://api.example.com/unknown")
            passed = result["status"] == 404
            tests.append({"test": "GET unknown returns 404", "result": "PASS" if passed else "FAIL"})
        except Exception as e:
            tests.append({"test": "GET unknown returns 404", "result": "FAIL", "error": str(e)})

        # Test 3: POST creates
        try:
            result = self.post("https://api.example.com/users", {"name": "test"})
            passed = result["status"] == 201 and "created" in result
            tests.append({"test": "POST users returns 201", "result": "PASS" if passed else "FAIL"})
        except Exception as e:
            tests.append({"test": "POST users returns 201", "result": "FAIL", "error": str(e)})

        # Test 4: Retry succeeds on flaky
        try:
            self.reset_flaky()
            result = self.retry_request("GET", "https://api.example.com/flaky", max_retries=3)
            passed = result["status"] == 200
            tests.append({"test": "Retry succeeds on flaky", "result": "PASS" if passed else "FAIL"})
        except Exception as e:
            tests.append({"test": "Retry succeeds on flaky", "result": "FAIL", "error": str(e)})

        # Test 5: Error endpoint raises
        try:
            self.get("https://api.example.com/error")
            tests.append({"test": "Error endpoint raises", "result": "FAIL"})
        except ConnectionError:
            tests.append({"test": "Error endpoint raises", "result": "PASS"})
        except Exception as e:
            tests.append({"test": "Error endpoint raises", "result": "FAIL", "error": str(e)})

        passed_count = sum(1 for t in tests if t["result"] == "PASS")

        return {
            "status": "PASS" if passed_count == len(tests) else "FAIL",
            "tests_passed": passed_count,
            "tests_run": len(tests),
            "details": tests
        }

    def verify_print(self) -> bool:
        """Print verification results in readable format."""
        result = self.verify()
        print("=" * 50)
        print(f"APIAgent v{self.version} Self-Verification")
        print("=" * 50)
        for d in result["details"]:
            sym = "✓" if d["result"] == "PASS" else "✗"
            print(f"  {sym} {d['test']}")
        print("-" * 50)
        print(f"Status: {result['status']} ({result['tests_passed']}/{result['tests_run']})")
        print("=" * 50)
        return result["status"] == "PASS"


if __name__ == "__main__":
    agent = APIAgent()
    agent.verify_print()
