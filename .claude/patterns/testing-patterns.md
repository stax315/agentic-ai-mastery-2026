# Testing Patterns

Patterns for effective testing. Use these to ensure quality without over-testing.

---

## Test Count Guidance

| Agent Complexity | Recommended Tests |
|------------------|-------------------|
| Simple (2-4 methods) | 15-25 tests |
| Medium (5-8 methods) | 30-50 tests |
| Complex (9+ methods) | 50+ tests |

**Rule:** Tests should match complexity. More tests ≠ better.

---

## Pattern 33: Mock Testing for Fast Tests
```python
from unittest.mock import patch

@patch('api_agent.time.sleep')  # Mock at module level, not 'time.sleep'
def test_retry_logic(self, mock_sleep, agent):
    """Test retry without actual delays."""
    result = agent.retry_request("GET", "https://api.example.com/flaky")
    assert result["status"] == 200
    assert mock_sleep.call_count == 2  # Verify sleep happened N times

# Why mock at module level:
# - @patch('time.sleep') patches global time module
# - @patch('api_agent.time.sleep') patches where it's USED
# - Always patch where imported, not where defined
```
**Why:** Retry tests would take minutes without mocking. Mock enables fast, deterministic tests.

---

## Testing Standards

- Every function must have tests
- Tests must run and pass before code is considered complete
- AI must verify its own work before showing me
- Tests should catch the errors I've documented
- Use pytest with `-v` flag for verbose output
- Run tests after EVERY method, not at the end

---

## Integration Testing for Multi-Agent

Multi-agent systems need different test categories:

| Category | What to Test |
|----------|--------------|
| Routing | Each operation routes to correct agent |
| Propagation | Sub-agent errors pass through unchanged |
| Validation | Invalid operations rejected with helpful message |
| Discovery | list_operations() returns complete list |
| Integration | Full flow works end-to-end |

---

## When to Test

| Test Always | Test Sometimes | Skip |
|-------------|----------------|------|
| Happy path | Unlikely edge cases | 1% scenarios |
| Obvious edge cases (empty, None, zero) | Performance | Infrastructure |
| Error conditions you handle | Concurrency | Premature optimization |
| Integration points | Configuration variants | Library internals |

**Day 4 proof:** 20 tests per agent is sufficient for simple agents. 40+ tests only for complex agents.

---

## Backwards Compatibility Testing

When upgrading v1 → v2:
```python
# All v1 tests must still pass unchanged
# v1 API calls must work identically
# Error messages may be enhanced but not changed incompatibly
# New features are additive, not replacing
```

| Check | v1 Behavior | v2 Behavior | Breaking? |
|-------|-------------|-------------|-----------|
| execute("reverse", "hello") | "olleh" | "olleh" | No |
| execute("unknown", "x") | ValueError | ValueError + suggestion | No (enhanced) |
| list_operations() | 10 items | 17 items | No (additive) |

---

## Planning Patterns That Work

### Planning Pattern 1: Edge Case First
- List ALL edge cases BEFORE writing implementation
- Each edge case becomes a test case
- Handle edge cases in the code, not as afterthoughts

### Planning Pattern 2: Test Plan = Implementation Plan
- Create test plan alongside implementation plan
- Know what tests you'll write before you write code
- Tests guide implementation, not the other way around

### Planning Pattern 3: Review for Gotchas
Review plans specifically for:
- Type issues (booleans, strings, None)
- Mathematical edge cases (zero, negative, overflow)
- Empty inputs (lists, strings, None)
- Special values (NaN, Infinity)

### Planning Pattern 4: Verification First
- Plan verification approach before building main functionality
- Know HOW you'll prove it works before you build it
- verify() method design is part of the plan

### Planning Pattern 5: Anticipate Failure
- Consider what could go wrong
- Then prevent it in the plan
- "What if..." questions save debugging time

---

## Code Review Patterns

### What to Check in Every Review

| Category | Questions to Ask |
|----------|------------------|
| **Correctness** | Does it do what it's supposed to? |
| **Robustness** | Does it handle unexpected inputs? |
| **Maintainability** | Can someone else understand it? |
| **Testability** | Are tests comprehensive? |

### Review Checklist

```
□ Error handling complete?
  - Division by zero
  - Invalid types (strings, None, booleans)
  - Special floats (NaN, Infinity)

□ Edge cases covered?
  - Empty/zero inputs
  - Negative numbers
  - Very large numbers
  - Boundary conditions

□ Error messages helpful?
  - Include what went wrong
  - Include the problematic value
  - Suggest how to fix

□ Tests thorough?
  - Happy path tests
  - Edge case tests
  - Error case tests
```

### "Just Working" vs "Production-Ready"

| Just Working | Production-Ready |
|--------------|------------------|
| Happy path works | ALL paths work |
| Basic errors | Descriptive errors with context |
| Some tests | Comprehensive tests |
| Silent edge cases | Explicit edge case handling |

---

Last updated: January 19, 2026
