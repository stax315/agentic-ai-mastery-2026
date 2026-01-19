# Core Patterns

Universal patterns that appear in 8+ agents. Use these ALWAYS.

---

## Universal Patterns (Use Always)

| Pattern | Occurrences | Why Universal |
|---------|-------------|---------------|
| `verify()` method | 11/12 | Instant confidence in correctness |
| `verify_print()` method | 10/12 | Human-readable validation output |
| `self.version` attribute | 11/12 | Track agent versions |
| `__init__()` with initialization | 12/12 | Standard Python class structure |
| `ValueError` for validation | 12/12 | Consistent, built-in, clear |
| Docstrings on all methods | 12/12 | Self-documenting code |

**Rule:** Every new agent MUST have `verify()`, `verify_print()`, and `self.version`.

---

## Pattern 1: Input Validation
```python
def _validate_inputs(self, a, b) -> None:
    # Use type() not isinstance() to exclude booleans
    if type(a) not in (int, float):
        raise ValueError(f"First argument must be a number, got {type(a).__name__}")
```

## Pattern 2: Consistent Return Types
```python
def add(self, a: float, b: float) -> float:
    self._validate_inputs(a, b)
    return float(a + b)  # Always return float for consistency
```

## Pattern 3: Self-Verifying Agents
```python
def verify(self) -> dict:
    """Run self-tests and report results."""
    tests = [
        ("add(2, 3) == 5.0", lambda: self.add(2, 3), 5.0, False),
        # ... more tests
    ]
    # Run all tests, return {"status": "PASS/FAIL", "details": [...]}
```

## Pattern 4: Error Messages with Context
```python
raise ValueError(f"First argument must be a number, got {type(a).__name__}")
# Good: "First argument must be a number, got str"
# Bad:  "Invalid input"
```

## Pattern 5: Reject Special Floats
```python
import math

def _validate_inputs(self, a, b):
    if math.isnan(a):
        raise ValueError("cannot be NaN")
    if math.isinf(a):
        raise ValueError("cannot be Infinity")
```

## Pattern 6: Check Results for Overflow
```python
def _check_result(self, result, operation):
    if math.isinf(result):
        raise ValueError(f"'{operation}' produced Infinity (overflow)")
    return result
```

## Pattern 7: Error Messages with Values
```python
# Bad
raise ValueError("Cannot divide by zero")

# Good
raise ValueError(f"Cannot divide {a} by zero")
```

## Pattern 8: Pretty Output Option
```python
def verify(self) -> dict:
    """Returns dict for programmatic use."""

def verify_print(self) -> bool:
    """Prints readable output for humans."""
```

## Pattern 9: Agent Class Structure
```python
class MyAgent:
    def __init__(self) -> None:
        """Initialize the agent."""
        self.version = "1.0"

    def _validate_inputs(self, ...):
        """Private: validate before operations."""

    def operation(self, ...):
        """Public: do the work."""
        self._validate_inputs(...)
        return result

    def verify(self) -> dict:
        """Public: test myself."""
```

---

## String Patterns (Day 2)

### Pattern 10: String Input Validation
```python
def _validate_input(self, text, param_name: str = "text") -> None:
    if text is None:
        raise ValueError(f"{param_name} cannot be None")
    if type(text) is bool:  # Booleans are NOT strings!
        raise ValueError(f"{param_name} must be a string, got bool")
    if not isinstance(text, str):
        raise ValueError(f"{param_name} must be a string, got {type(text).__name__}")
```

### Pattern 11: String Edge Case Handling
```python
# Empty strings are VALID - handle them, don't reject them
"".upper()      # Returns ""
"".split()      # Returns []
len("".split()) # Returns 0

# Whitespace-only needs explicit decisions per operation
"   ".split()       # Returns [] - no words
"   "[::-1]         # Returns "   " - preserved
"".join("   ".split())  # Returns "" - removed
```

### Pattern 12: Word Counting with split()
```python
def count_words(self, text: str) -> int:
    return len(text.split())  # split() with NO arguments!

# Why split() with no args is perfect:
# - Splits on ANY whitespace (space, tab, newline)
# - Removes empty strings from result
# - Handles multiple consecutive whitespace
# - Handles leading/trailing whitespace
# "  a  b  " -> ["a", "b"] -> 2 words
```

### Pattern 13: Whitespace Removal
```python
def remove_spaces(self, text: str) -> str:
    return "".join(text.split())  # Removes ALL whitespace types

# "a \t\n b" -> ["a", "b"] -> "ab"
```

---

## DateTime Patterns (Day 2)

### Pattern 14: Multi-Format Date Parsing
```python
def _parse_date(self, date_str: str) -> date:
    """Try multiple formats in priority order."""
    formats = [
        "%Y-%m-%d",      # ISO: 2024-01-15 (PRIORITY 1 - unambiguous)
        "%m/%d/%Y",      # US: 01/15/2024 (PRIORITY 2 - US assumption)
        "%B %d, %Y",     # Full: January 15, 2024
        "%b %d, %Y",     # Short: Jan 15, 2024
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: '{date_str}'")
```

### Pattern 15: Date String Validation
```python
def _validate_date_string(self, date_str, param_name: str = "date") -> None:
    """Validate date input is non-empty string."""
    if date_str is None:
        raise ValueError(f"{param_name} cannot be None")
    if type(date_str) is bool:
        raise ValueError(f"{param_name} must be a string, got bool")
    if not isinstance(date_str, str):
        raise ValueError(f"{param_name} must be a string, got {type(date_str).__name__}")
    if date_str.strip() == "":
        raise ValueError(f"{param_name} cannot be empty")

# Key difference from string validation: REJECT empty/whitespace
# Dates cannot be empty - there's no "empty date" concept
```

### Pattern 16: Integer Parameter Validation
```python
def _validate_days(self, days) -> None:
    """Validate days is an integer (not float, not bool)."""
    if days is None:
        raise ValueError("days cannot be None")
    if type(days) is bool:
        raise ValueError("days must be an integer, got bool")
    if not isinstance(days, int):
        raise ValueError(f"days must be an integer, got {type(days).__name__}")

# Why reject floats: 5.5 days is ambiguous
```

### Pattern 17: Standardized Output Format
```python
# All date outputs use ISO 8601 regardless of input format
def add_days(self, date_str: str, days: int) -> str:
    parsed_date = self._parse_date(date_str)  # Any format in
    result_date = parsed_date + timedelta(days=days)
    return result_date.isoformat()  # ISO format out

# Input: "01/15/2024" (US format)
# Output: "2024-01-20" (ISO format)
# Consistent, sortable, unambiguous
```

---

## Simple Agent Patterns (Day 4)

### Pattern 34: Inline Validation for Simple Agents
```python
# For agents with 2-4 methods, inline validation is cleaner than _validate_*

def get(self, url: str) -> dict:
    """Mock GET request."""
    if url is None:
        raise ValueError("url cannot be None")
    if not isinstance(url, str):
        raise ValueError(f"url must be string, got {type(url).__name__}")
    # ... operation logic follows directly

# When to inline:
# - Validation is 2-5 lines
# - Same validation not repeated across methods
# - Agent has few methods (≤4)
# - No complex type coercion needed

# When to extract _validate_*:
# - Same validation in 3+ methods
# - Complex validation logic (10+ lines)
# - Need to test validation separately
```

---

Last updated: January 19, 2026
