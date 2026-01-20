"""
FileOperationsAgent - Simple file I/O operations.

Day 4 Session 1 - Keep it simple, no overengineering.

Methods:
- read_file(path) -> str
- write_file(path, content) -> bool
- append_file(path, content) -> bool
- file_exists(path) -> bool
- verify() -> dict
"""

import os
import tempfile


class FileOperationsAgent:
    """Simple file I/O agent. No abstractions."""

    def __init__(self) -> None:
        """Initialize the agent."""
        self.version = "1.0"

    def read_file(self, path: str) -> str:
        """
        Read file contents.

        Args:
            path: Path to file

        Returns:
            File contents as string

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If path is None or empty
        """
        if path is None:
            raise ValueError("path cannot be None")
        if not isinstance(path, str):
            raise ValueError(f"path must be string, got {type(path).__name__}")
        if path.strip() == "":
            raise ValueError("path cannot be empty")

        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def write_file(self, path: str, content: str) -> bool:
        """
        Write content to file. Creates or overwrites.

        Args:
            path: Path to file
            content: Content to write

        Returns:
            True on success

        Raises:
            ValueError: If path or content is None/invalid
        """
        if path is None:
            raise ValueError("path cannot be None")
        if not isinstance(path, str):
            raise ValueError(f"path must be string, got {type(path).__name__}")
        if path.strip() == "":
            raise ValueError("path cannot be empty")
        if content is None:
            raise ValueError("content cannot be None")
        if not isinstance(content, str):
            raise ValueError(f"content must be string, got {type(content).__name__}")

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True

    def append_file(self, path: str, content: str) -> bool:
        """
        Append content to file. Creates if missing.

        Args:
            path: Path to file
            content: Content to append

        Returns:
            True on success

        Raises:
            ValueError: If path or content is None/invalid
        """
        if path is None:
            raise ValueError("path cannot be None")
        if not isinstance(path, str):
            raise ValueError(f"path must be string, got {type(path).__name__}")
        if path.strip() == "":
            raise ValueError("path cannot be empty")
        if content is None:
            raise ValueError("content cannot be None")
        if not isinstance(content, str):
            raise ValueError(f"content must be string, got {type(content).__name__}")

        with open(path, 'a', encoding='utf-8') as f:
            f.write(content)
        return True

    def file_exists(self, path: str) -> bool:
        """
        Check if file exists.

        Args:
            path: Path to check

        Returns:
            True if file exists, False otherwise

        Raises:
            ValueError: If path is None or invalid
        """
        if path is None:
            raise ValueError("path cannot be None")
        if not isinstance(path, str):
            raise ValueError(f"path must be string, got {type(path).__name__}")
        if path.strip() == "":
            raise ValueError("path cannot be empty")

        return os.path.isfile(path)

    def verify(self) -> dict:
        """
        Run self-tests using temp files.

        Returns:
            Dict with status, tests_passed, tests_run, details
        """
        tests = []

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.txt")

            # Test 1: Write file
            try:
                result = self.write_file(test_file, "hello")
                passed = result is True
                tests.append({"test": "write_file returns True", "result": "PASS" if passed else "FAIL"})
            except Exception as e:
                tests.append({"test": "write_file returns True", "result": "FAIL", "error": str(e)})

            # Test 2: File exists after write
            try:
                result = self.file_exists(test_file)
                passed = result is True
                tests.append({"test": "file_exists after write", "result": "PASS" if passed else "FAIL"})
            except Exception as e:
                tests.append({"test": "file_exists after write", "result": "FAIL", "error": str(e)})

            # Test 3: Read file
            try:
                result = self.read_file(test_file)
                passed = result == "hello"
                tests.append({"test": "read_file returns content", "result": "PASS" if passed else "FAIL"})
            except Exception as e:
                tests.append({"test": "read_file returns content", "result": "FAIL", "error": str(e)})

            # Test 4: Append file
            try:
                self.append_file(test_file, " world")
                result = self.read_file(test_file)
                passed = result == "hello world"
                tests.append({"test": "append_file adds content", "result": "PASS" if passed else "FAIL"})
            except Exception as e:
                tests.append({"test": "append_file adds content", "result": "FAIL", "error": str(e)})

            # Test 5: File doesn't exist
            try:
                result = self.file_exists(os.path.join(tmpdir, "nonexistent.txt"))
                passed = result is False
                tests.append({"test": "file_exists returns False for missing", "result": "PASS" if passed else "FAIL"})
            except Exception as e:
                tests.append({"test": "file_exists returns False for missing", "result": "FAIL", "error": str(e)})

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
        print(f"FileOperationsAgent v{self.version} Self-Verification")
        print("=" * 50)
        for d in result["details"]:
            sym = "✓" if d["result"] == "PASS" else "✗"
            print(f"  {sym} {d['test']}")
        print("-" * 50)
        print(f"Status: {result['status']} ({result['tests_passed']}/{result['tests_run']})")
        print("=" * 50)
        return result["status"] == "PASS"


if __name__ == "__main__":
    agent = FileOperationsAgent()
    agent.verify_print()
