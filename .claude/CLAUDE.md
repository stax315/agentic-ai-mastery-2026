# AI Development Standards

## CRITICAL WORKFLOW RULES

### Rule #1: ALWAYS ASK FOR A PLAN FIRST
- Before writing ANY code, ask AI to create a detailed plan
- Plan should include: steps, files to create, tests needed, verification approach
- Review the plan, refine it, THEN execute
- This prevents wasted effort and catches issues early
- **Day 1 Proof: Zero errors achieved through planning-first**

### Rule #2: DOCUMENT EVERY ERROR
- When something goes wrong, capture it in ERROR_LOG.md
- Include: what happened, why it happened, how to prevent next time
- Update CLAUDE.md with prevention patterns
- Errors are learning opportunities, not failures

### Rule #3: TEST-AS-YOU-GO
- Write tests immediately after each function/method
- Never build everything first and test at the end
- If a test fails, you know exactly which code caused it

---

## Code Patterns That Work

### Pattern 1: Input Validation
```python
def _validate_inputs(self, a, b) -> None:
    # Use type() not isinstance() to exclude booleans
    if type(a) not in (int, float):
        raise ValueError(f"First argument must be a number, got {type(a).__name__}")
```

### Pattern 2: Consistent Return Types
```python
def add(self, a: float, b: float) -> float:
    self._validate_inputs(a, b)
    return float(a + b)  # Always return float for consistency
```

### Pattern 3: Self-Verifying Agents
```python
def verify(self) -> dict:
    """Run self-tests and report results."""
    tests = [
        ("add(2, 3) == 5.0", lambda: self.add(2, 3), 5.0, False),
        # ... more tests
    ]
    # Run all tests, return {"status": "PASS/FAIL", "details": [...]}
```

### Pattern 4: Error Messages with Context
```python
raise ValueError(f"First argument must be a number, got {type(a).__name__}")
# Good: "First argument must be a number, got str"
# Bad:  "Invalid input"
```

### Pattern 5: Reject Special Floats (v2)
```python
import math

def _validate_inputs(self, a, b):
    if math.isnan(a):
        raise ValueError("cannot be NaN")
    if math.isinf(a):
        raise ValueError("cannot be Infinity")
```

### Pattern 6: Check Results for Overflow (v2)
```python
def _check_result(self, result, operation):
    if math.isinf(result):
        raise ValueError(f"'{operation}' produced Infinity (overflow)")
    return result
```

### Pattern 7: Error Messages with Values (v2)
```python
# Bad
raise ValueError("Cannot divide by zero")

# Good
raise ValueError(f"Cannot divide {a} by zero")
```

### Pattern 8: Pretty Output Option (v2)
```python
def verify(self) -> dict:
    """Returns dict for programmatic use."""

def verify_print(self) -> bool:
    """Prints readable output for humans."""
```

### Pattern 9: Agent Class Structure
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

### v1 → v2 Improvements I Made

| Aspect | v1 | v2 |
|--------|----|----|
| Operations | 4 | 7 (+power, modulo, sqrt) |
| NaN handling | Silent pass | Explicit rejection |
| Infinity handling | Silent pass | Explicit rejection |
| Error messages | Basic | Include values |
| verify() output | Dict only | Dict + pretty print |

---

## Testing Standards

- Every function must have tests
- Tests must run and pass before code is considered complete
- AI must verify its own work before showing me
- Tests should catch the errors I've documented
- Use pytest with `-v` flag for verbose output
- Run tests after EVERY method, not at the end

---

## Learning Approach

- ASK FOR A PLAN before building anything
- Ask for line-by-line explanations when learning new concepts
- Always include error handling
- Document WHY decisions were made, not just WHAT was coded
- When errors occur, capture them in ERROR_LOG.md immediately

---

## Day 1 Achievements

- Built `sum_even_numbers()` function (9 tests passing)
- Built `CalculatorAgent` v1 (29 tests passing)
- Built `CalculatorAgent` v2 (47 tests passing)
- Conducted code review and improved code
- **Zero bugs due to planning-first approach**
- Learned: Planning prevents debugging
- Learned: Code review catches hidden issues
- Total tests: 85 passing

---

## Pattern Count

| Section | Patterns |
|---------|----------|
| Code Patterns | 9 |
| Mistakes to Avoid | 5 |
| Error Prevention | 4 |
| Planning Patterns | 5 |
| Review Patterns | 4+ |
| **Total** | **27+** |

---

Last updated: January 15, 2026
Day 1 - Planning-first, verification-first, review-and-improve approach
**ZERO ERRORS achieved through planning**
