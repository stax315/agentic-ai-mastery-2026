"""
Tests for FileOperationsAgent.

Day 4 Session 1 - Simple tests, 15-20 total.
"""

import os
import tempfile
import pytest
from file_operations_agent import FileOperationsAgent


@pytest.fixture
def agent():
    """Create agent instance."""
    return FileOperationsAgent()


@pytest.fixture
def temp_dir():
    """Create temp directory for file tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


# =============================================================================
# HAPPY PATH TESTS (8)
# =============================================================================

class TestHappyPath:
    """Tests for normal operation."""

    def test_write_new_file(self, agent, temp_dir):
        """Write to new file succeeds."""
        path = os.path.join(temp_dir, "test.txt")
        result = agent.write_file(path, "hello")
        assert result is True

    def test_read_existing_file(self, agent, temp_dir):
        """Read written file returns content."""
        path = os.path.join(temp_dir, "test.txt")
        agent.write_file(path, "hello world")
        result = agent.read_file(path)
        assert result == "hello world"

    def test_append_to_file(self, agent, temp_dir):
        """Append adds to existing content."""
        path = os.path.join(temp_dir, "test.txt")
        agent.write_file(path, "hello")
        agent.append_file(path, " world")
        result = agent.read_file(path)
        assert result == "hello world"

    def test_append_creates_file(self, agent, temp_dir):
        """Append creates file if missing."""
        path = os.path.join(temp_dir, "new.txt")
        result = agent.append_file(path, "created")
        assert result is True
        assert agent.read_file(path) == "created"

    def test_file_exists_true(self, agent, temp_dir):
        """Existing file returns True."""
        path = os.path.join(temp_dir, "test.txt")
        agent.write_file(path, "content")
        assert agent.file_exists(path) is True

    def test_file_exists_false(self, agent, temp_dir):
        """Missing file returns False."""
        path = os.path.join(temp_dir, "missing.txt")
        assert agent.file_exists(path) is False

    def test_write_overwrites(self, agent, temp_dir):
        """Write replaces existing content."""
        path = os.path.join(temp_dir, "test.txt")
        agent.write_file(path, "first")
        agent.write_file(path, "second")
        assert agent.read_file(path) == "second"

    def test_verify_passes(self, agent):
        """Self-test succeeds."""
        result = agent.verify()
        assert result["status"] == "PASS"
        assert result["tests_passed"] == result["tests_run"]


# =============================================================================
# ERROR PATH TESTS (6)
# =============================================================================

class TestErrors:
    """Tests for error handling."""

    def test_read_missing_file(self, agent, temp_dir):
        """FileNotFoundError raised for missing file."""
        path = os.path.join(temp_dir, "missing.txt")
        with pytest.raises(FileNotFoundError):
            agent.read_file(path)

    def test_read_none_path(self, agent):
        """ValueError for None path."""
        with pytest.raises(ValueError, match="path cannot be None"):
            agent.read_file(None)

    def test_read_empty_path(self, agent):
        """ValueError for empty path."""
        with pytest.raises(ValueError, match="path cannot be empty"):
            agent.read_file("   ")

    def test_write_none_path(self, agent):
        """ValueError for None path on write."""
        with pytest.raises(ValueError, match="path cannot be None"):
            agent.write_file(None, "content")

    def test_write_none_content(self, agent, temp_dir):
        """ValueError for None content."""
        path = os.path.join(temp_dir, "test.txt")
        with pytest.raises(ValueError, match="content cannot be None"):
            agent.write_file(path, None)

    def test_read_non_string_path(self, agent):
        """ValueError for int path."""
        with pytest.raises(ValueError, match="path must be string"):
            agent.read_file(123)


# =============================================================================
# EDGE CASES (4)
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases."""

    def test_read_empty_file(self, agent, temp_dir):
        """Returns empty string, not error."""
        path = os.path.join(temp_dir, "empty.txt")
        agent.write_file(path, "")
        result = agent.read_file(path)
        assert result == ""

    def test_write_empty_content(self, agent, temp_dir):
        """Creates empty file."""
        path = os.path.join(temp_dir, "empty.txt")
        agent.write_file(path, "")
        assert agent.file_exists(path) is True
        assert agent.read_file(path) == ""

    def test_unicode_content(self, agent, temp_dir):
        """UTF-8 works correctly."""
        path = os.path.join(temp_dir, "unicode.txt")
        content = "Hello 世界 🌍"
        agent.write_file(path, content)
        assert agent.read_file(path) == content

    def test_multiline_content(self, agent, temp_dir):
        """Handles newlines correctly."""
        path = os.path.join(temp_dir, "multiline.txt")
        content = "line1\nline2\nline3"
        agent.write_file(path, content)
        assert agent.read_file(path) == content
