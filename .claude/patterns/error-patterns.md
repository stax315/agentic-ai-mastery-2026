# Error & Resilience Patterns

Patterns for error handling, recovery, and building resilient systems.

---

## Resilience Patterns (Day 3)

### Pattern 28: Resilient Wrapper
```python
def _execute_with_resilience(self, operation, args, kwargs):
    """Stack: circuit_breaker → retry → fallback"""
    def raw_operation():
        return self._execute_raw(operation, *args, **kwargs)

    def with_circuit_breaker():
        return self._recovery.circuit_breaker(
            operation=raw_operation,
            operation_id=agent_id,
            failure_threshold=5,
            reset_timeout=30.0
        )

    try:
        result = self._recovery.retry_with_backoff(
            operation=with_circuit_breaker,
            max_retries=3
        )
        return result
    except CircuitOpenError:
        return self._get_fallback_value(operation, args, kwargs)
    except Exception:
        return self._get_fallback_value(operation, args, kwargs)
```
**Why:** Composing resilience patterns creates production-grade reliability.

### Pattern 29: Per-Agent Circuit Breaker
```python
# Each agent has its own circuit breaker - one failing agent doesn't take down others
agent_id = self._agent_for_operation[operation]  # "string_agent", "datetime_agent", etc.

circuit_breaker(op, operation_id="string_agent")    # Separate circuit
circuit_breaker(op, operation_id="datetime_agent")  # Separate circuit
circuit_breaker(op, operation_id="calculator_agent") # Separate circuit

# If calculator agent fails repeatedly, string and datetime still work
```
**Why:** Isolation prevents cascade failures. One agent down shouldn't break everything.

### Pattern 30: Failure Injection for Testing
```python
def _inject_failure(self, operation: str, failure_type: str, fail_count: int):
    """Inject controlled failures for resilience testing."""
    self._injected_failures[operation] = {
        "type": failure_type,  # "transient" or "permanent"
        "remaining": fail_count
    }

def _execute_raw(self, operation, *args, **kwargs):
    # Check for injected failure before normal execution
    if operation in self._injected_failures:
        failure = self._injected_failures[operation]
        if failure["remaining"] > 0:
            failure["remaining"] -= 1
            if failure["type"] == "transient":
                raise TransientError(f"Injected transient failure")
            else:
                raise PermanentError(f"Injected permanent failure")
    # Normal execution...
```
**Why:** Can't test retry/circuit breaker without failures; injection provides controlled testing.

### Pattern 31: Operation-Specific Fallbacks
```python
fallbacks = {
    # String ops: Return input unchanged (user sees their input)
    "uppercase": lambda args, kwargs: args[0] if args else "",
    "reverse": lambda args, kwargs: args[0] if args else "",

    # Counts: Return -1 (not 0, since 0 is valid for empty string)
    "count_words": lambda args, kwargs: -1,
    "days_between": lambda args, kwargs: -1,

    # Calculator ops: Return NaN (math convention for undefined)
    "add": lambda args, kwargs: float('nan'),
    "divide": lambda args, kwargs: float('nan'),

    # DateTime ops: Return epoch/midnight (recognizable defaults)
    "current_date": lambda args, kwargs: "1970-01-01",
    "current_time": lambda args, kwargs: "00:00:00",
}
```
**Why:** Fallbacks should be recognizable as "error" values, not silent valid-looking results.

### Pattern 32: Circuit-First (Fail Fast) Pattern
```
User Request
    ↓
[Circuit Breaker Check] ──→ If OPEN: Return fallback immediately (fail fast)
    ↓ (if CLOSED/HALF_OPEN)
[Retry with Backoff] ──→ Try operation up to N times
    ↓ (if all fail)
[Fallback] ──→ Return safe default value
```
**Why:** Don't waste retries on a service known to be down. Fail fast protects both caller and failing service.

---

## Mistakes to Never Repeat

### Mistake 1: isinstance() with Booleans
```python
# WRONG - booleans pass through!
isinstance(True, int)  # Returns True!

# CORRECT - excludes booleans
type(True) in (int, float)  # Returns False
```

### Mistake 2: Building Without a Plan
- Always create a plan with edge cases BEFORE coding
- Review the plan for missing cases
- **Proof: Day 1 had ZERO bugs because I planned first**

### Mistake 3: Testing at the End
- Don't build 5 methods then write tests
- Build 1 method → Test it → Move on
- If something breaks, you know exactly where

### Mistake 4: Silent Failures
- NaN passing through calculations unnoticed
- Infinity from overflow going undetected
- **Fix: Explicitly reject problematic inputs**

### Mistake 5: Vague Error Messages
- "Invalid input" tells me nothing
- **Fix: Include the actual value and expected type**

---

## Error Prevention Strategies

### Strategy 1: Edge Case Checklist
Before implementing any function, ask:
- [ ] What if the input is empty?
- [ ] What if the input is zero?
- [ ] What if the input is negative?
- [ ] What if the input is the wrong type?
- [ ] What if the input is None?
- [ ] What if the input is a boolean?
- [ ] What if the input is NaN?
- [ ] What if the input is Infinity?
- [ ] What if the result overflows?

### Strategy 2: Plan Review Questions
Before executing a plan, ask:
1. "Is the implementation order logical?"
2. "Does the error anticipation cover likely issues?"
3. "Is the verification thorough enough?"
4. "What's missing from this plan?"

### Strategy 3: Test Categories
Every function should have tests for:
- Basic/happy path
- Edge cases (empty, zero, negative)
- Error cases (invalid input, division by zero)
- Type checking (strings, None, booleans, NaN, Infinity)

### Strategy 4: Planning Prevents Errors
- Planning identifies 80%+ of potential errors before coding
- Create comprehensive test plans that cover edge cases
- Implement verify() methods that test agent's own functionality
- **Day 1 achieved zero errors through planning alone**
- **Day 2 achieved zero errors through planning alone**

### Strategy 5: String-Specific Edge Case Checklist
Before implementing any string function, ask:
- [ ] What if the string is empty `""`?
- [ ] What if the string is whitespace only `"   "`?
- [ ] What if the input is None?
- [ ] What if the input is a boolean (not a string)?
- [ ] What if the input is an integer (not a string)?
- [ ] What if the string contains unicode/emoji?
- [ ] What if the string has tabs `\t` or newlines `\n`?
- [ ] What if there are multiple consecutive spaces?
- [ ] What if there are leading/trailing spaces?

### Strategy 6: Define Ambiguous Terms Before Coding
When a concept has multiple interpretations, DEFINE IT FIRST:
```
Example: "What is a word?"
- Defined as: "Maximal contiguous non-whitespace sequence"
- "don't" = 1 word (apostrophe is not whitespace)
- "well-known" = 1 word (hyphen is not whitespace)
- "Hello, World!" = 2 words (punctuation attached)
```

### Strategy 7: DateTime-Specific Edge Case Checklist
Before implementing any date function, ask:
- [ ] What if the date is Feb 29 in a leap year? (valid)
- [ ] What if the date is Feb 29 in a non-leap year? (invalid)
- [ ] What if the operation crosses a month boundary?
- [ ] What if the operation crosses a year boundary?
- [ ] What if days is negative? (subtraction)
- [ ] What if days is zero? (no change)
- [ ] What if the input format is ambiguous (01/02/2024)?
- [ ] What if the date string is empty or whitespace?
- [ ] What if days is a float (5.5)?

### Strategy 8: Trust Libraries for Date Arithmetic
```python
# DON'T: Manual date arithmetic
days_in_month = [31, 28, 31, 30, ...]  # What about leap years?

# DO: Use timedelta - it handles EVERYTHING
result = parsed_date + timedelta(days=days)

# timedelta automatically handles:
# - Leap years (Feb 29)
# - Month boundaries (Jan 31 + 1 = Feb 1)
# - Year boundaries (Dec 31 + 1 = Jan 1 next year)
# - Negative days (subtraction)
```

### Strategy 9: Standardize Output Even When Input Varies
```
Problem: Multiple valid input formats
- "2024-01-15" (ISO)
- "01/15/2024" (US)
- "January 15, 2024" (Written)

Solution: Accept many, output one
- Parse any valid format
- Always output ISO 8601
- Predictable, consistent, sortable
```

---

Last updated: January 19, 2026
