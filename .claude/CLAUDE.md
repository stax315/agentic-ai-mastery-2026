# AI Development Standards

## Style Guide
- Use existing patterns; examine codebase first
- Minimal changes only: surgical edits, no refactors unless breaking

## What NOT to Do (Anti-Overengineering)
- No abstractions until duplications exists
- No design patterns unless problem demands them
- No complex error handling for 1% edge cases
- No configurations for rarely-changing values
- No new utils/helpers for one-off logic
- Inline simple functions; reuse existing code first
- Minimal changes only: edit files surgically
- Assume happy path until proven otherwise

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

### Pattern 10: String Input Validation (Day 2)
```python
def _validate_input(self, text, param_name: str = "text") -> None:
    if text is None:
        raise ValueError(f"{param_name} cannot be None")
    if type(text) is bool:  # Booleans are NOT strings!
        raise ValueError(f"{param_name} must be a string, got bool")
    if not isinstance(text, str):
        raise ValueError(f"{param_name} must be a string, got {type(text).__name__}")
```

### Pattern 11: String Edge Case Handling (Day 2)
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

### Pattern 12: Word Counting with split() (Day 2)
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

### Pattern 13: Whitespace Removal (Day 2)
```python
def remove_spaces(self, text: str) -> str:
    return "".join(text.split())  # Removes ALL whitespace types

# "a \t\n b" -> ["a", "b"] -> "ab"
```

### Pattern 14: Multi-Format Date Parsing (Day 2)
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

# Why this order:
# - ISO is unambiguous, always try first
# - US format chosen over EU (must pick one for ambiguous dates)
# - Document the choice so users know what to expect
```

### Pattern 15: Date String Validation (Day 2)
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

### Pattern 16: Integer Parameter Validation (Day 2)
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
# Should it be 5 days? 6 days? 5 days + 12 hours?
# Require explicit integer for clarity
```

### Pattern 17: Standardized Output Format (Day 2)
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

### Pattern 18: Agent Composition (Day 2 - Multi-Agent)
```python
class CoordinatorAgent:
    def __init__(self) -> None:
        self.version = "1.0"
        # COMPOSITION: Create sub-agent instances
        self.string_agent = StringAgent()
        self.datetime_agent = DateTimeAgent()
        # Build routing registry
        self._operations = self._build_operation_registry()

# Coordinator OWNS sub-agents
# Sub-agents created in __init__ - always available
# Registry maps user-friendly names to internal methods
```

### Pattern 19: Operation Registry for Routing (Day 2 - Multi-Agent)
```python
def _build_operation_registry(self) -> dict:
    """Map operation names to (agent, method_name) tuples."""
    return {
        # User-friendly name → (agent instance, internal method name)
        "reverse": (self.string_agent, "reverse_string"),
        "uppercase": (self.string_agent, "to_uppercase"),
        "add_days": (self.datetime_agent, "add_days"),
        "current_time": (self.datetime_agent, "get_current_time"),
    }

# Why registry pattern:
# - Explicit routing - no magic, no ambiguity
# - Easy to extend - add one line per new operation
# - Testable - deterministic behavior
# - Discoverable - list_operations() for introspection
```

### Pattern 20: Execute with Registry Lookup (Day 2 - Multi-Agent)
```python
def execute(self, operation: str, *args, **kwargs):
    """Route operation to appropriate sub-agent."""
    self._validate_operation(operation)       # Validate first
    agent, method_name = self._operations[operation]  # Lookup
    method = getattr(agent, method_name)      # Get method
    return method(*args, **kwargs)            # Execute (errors propagate)

# Example flow:
# execute("reverse", "hello")
# → lookup: "reverse" → (string_agent, "reverse_string")
# → call: string_agent.reverse_string("hello")
# → return: "olleh"
```

### Pattern 21: Error Propagation in Multi-Agent (Day 2 - Multi-Agent)
```python
# Let sub-agent errors propagate AS-IS - don't wrap them
return method(*args, **kwargs)  # If sub-agent raises, it propagates

# Why propagate (not wrap):
# - Sub-agents already have context-rich error messages
# - Wrapping loses specificity ("Cannot parse date" vs "UtilityAgent error")
# - Simpler code = fewer bugs
# - Consistent with Python exception handling
```

### Pattern 22: Coordinator Validation with Discovery (Day 2 - Multi-Agent)
```python
def _validate_operation(self, operation) -> None:
    """Validate operation, include available options in error."""
    if operation is None:
        raise ValueError("operation cannot be None")
    if operation not in self._operations:
        available = ", ".join(sorted(self._operations.keys()))
        raise ValueError(f"Unknown operation: '{operation}'. Available: {available}")

# Include available operations in error message:
# - Helps users discover valid operations
# - Makes typos obvious
# - Self-documenting errors
```

### Pattern 23: Discovery Helper Method (Day 2 - Multi-Agent)
```python
def list_operations(self) -> list:
    """Return sorted list of available operation names."""
    return sorted(self._operations.keys())

# Why include this:
# - Discoverability - users can see what's available
# - Supports error messages ("Available: ...")
# - Enables introspection and documentation
# - Easy to test (assert len(ops) == 10)
```

### Pattern 24: Alias Resolution Layer (Day 2 v2)
```python
def _build_alias_registry(self) -> dict:
    """Map aliases to canonical operation names."""
    return {
        "rev": "reverse",
        "upper": "uppercase",
        "now": "current_time",
        "plus": "add",
    }

def _resolve_alias(self, operation: str) -> str:
    """Resolve alias to canonical name, or return as-is."""
    return self._aliases.get(operation, operation)

# Usage in execute():
operation = self._resolve_alias(operation)  # BEFORE validation!

# Why separate from operations registry:
# - Aliases are shortcuts, not new operations
# - One canonical name in error messages
# - Easy to add/remove aliases without touching core
# - Users can discover aliases separately
```

### Pattern 25: Self-Documenting API (Day 2 v2)
```python
def _build_descriptions(self) -> dict:
    """Human-readable descriptions for each operation."""
    return {
        "reverse": "Reverses a string. Args: (text)",
        "add_days": "Adds days to a date. Args: (date_str, days)",
        "add": "Adds two numbers. Args: (a, b)",
    }

def describe(self, operation: str) -> str:
    """Return description of what an operation does."""
    resolved = self._resolve_alias(operation)
    self._validate_operation(resolved)
    return self._descriptions[resolved]

# Why this pattern:
# - Users can discover functionality without reading source
# - Supports help/documentation systems
# - Aliases work transparently (describe("rev") works)
# - Error for unknown operations is consistent
```

### Pattern 26: Typo Suggestions in Errors (Day 2 v2)
```python
def _find_similar(self, typo: str) -> str | None:
    """Find operation name similar to typo using prefix matching."""
    if len(typo) < 2:
        return None

    typo_lower = typo.lower()
    best_match, best_score = None, 0

    all_names = list(self._operations.keys()) + list(self._aliases.keys())
    for name in all_names:
        common = 0
        for i in range(min(len(typo_lower), len(name))):
            if typo_lower[i] == name[i]:
                common += 1
            else:
                break
        if common >= 2 and common > best_score:
            best_score, best_match = common, name

    return best_match

# In validation:
suggestion = self._find_similar(operation)
msg = f"Unknown operation: '{operation}'."
if suggestion:
    msg += f" Did you mean '{suggestion}'?"
msg += f" Available: {available}"

# Why prefix matching (not edit distance):
# - Simple, fast, no dependencies
# - Good enough for common typos
# - "revrese" → "reverse" works
# - "uppercas" → "uppercase" works
# - Avoids over-suggesting for gibberish
```

### Pattern 27: Operation Categories for Discoverability (Day 2 v2)
```python
def list_operations_by_category(self) -> dict:
    """Return operations grouped by sub-agent category."""
    return {
        "string": sorted(["reverse", "uppercase", "lowercase", ...]),
        "datetime": sorted(["current_time", "add_days", ...]),
        "calculator": sorted(["add", "subtract", "multiply", ...]),
    }

# Why categories:
# - 17 operations is a lot to scan
# - Categories help users find what they need
# - Shows the multi-agent architecture
# - Supports organized help output
```

---

## Resilience Patterns (Day 3)

### Pattern 28: Resilient Wrapper (Day 3 Session 3)
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

### Pattern 29: Per-Agent Circuit Breaker (Day 3 Session 3)
```python
# Each agent has its own circuit breaker - one failing agent doesn't take down others
agent_id = self._agent_for_operation[operation]  # "string_agent", "datetime_agent", etc.

circuit_breaker(op, operation_id="string_agent")    # Separate circuit
circuit_breaker(op, operation_id="datetime_agent")  # Separate circuit
circuit_breaker(op, operation_id="calculator_agent") # Separate circuit

# If calculator agent fails repeatedly, string and datetime still work
```
**Why:** Isolation prevents cascade failures. One agent down shouldn't break everything.

### Pattern 30: Failure Injection for Testing (Day 3 Session 3)
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

### Pattern 31: Operation-Specific Fallbacks (Day 3 Session 3)
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

### Pattern 32: Circuit-First (Fail Fast) Pattern (Day 3 Session 3)
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

## Multi-Agent Patterns (Day 2)

### Architecture: Coordinator vs Implementer

| Aspect | Implementer Agent | Coordinator Agent |
|--------|-------------------|-------------------|
| **Role** | Does the work | Routes to workers |
| **Operations** | Implements logic | Delegates to sub-agents |
| **Has sub-agents** | No | Yes |
| **Primary job** | Execute operations | Route to correct agent |
| **Error source** | Self only | Self + sub-agents |
| **Validation** | Input values | Operation names |
| **Testing focus** | Edge cases | Integration |

### Routing Strategy: Why Registry Wins

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| Keyword matching | Natural language | Ambiguous, brittle | ❌ |
| Pattern detection | Automatic | Complex, still ambiguous | ❌ |
| Type parameter | Unambiguous | Verbose API | ⚠️ |
| **Operation Registry** | **Explicit, testable, extendable** | User must know names | ✅ |

### Error Handling in Multi-Agent Systems

| Error Type | Source | Handling |
|------------|--------|----------|
| Invalid operation | Coordinator | Raise with available list |
| Unknown operation | Coordinator | Raise with suggestions |
| Invalid arguments | Sub-agent | Propagate as-is |
| Internal error | Sub-agent | Propagate as-is |

### Integration Testing Strategy

Multi-agent testing requires different focus than single-agent:

| Single-Agent Tests | Multi-Agent Tests |
|-------------------|-------------------|
| Operation correctness | Routing correctness |
| Input validation | Operation validation |
| Edge cases | Error propagation |
| Return values | Integration flow |

### Extensibility Pattern

Adding a new sub-agent requires:
```python
# 1. Import
from new_agent import NewAgent

# 2. Initialize in __init__
self.new_agent = NewAgent()

# 3. Add to registry
"new_operation": (self.new_agent, "method_name"),

# 4. Write tests for new routes
# Effort: ~10 minutes per agent
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
- **Day 2 achieved zero errors through planning alone**

### Strategy 5: String-Specific Edge Case Checklist (Day 2)
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

### Strategy 6: Define Ambiguous Terms Before Coding (Day 2)
When a concept has multiple interpretations, DEFINE IT FIRST:
```
Example: "What is a word?"
- Defined as: "Maximal contiguous non-whitespace sequence"
- "don't" = 1 word (apostrophe is not whitespace)
- "well-known" = 1 word (hyphen is not whitespace)
- "Hello, World!" = 2 words (punctuation attached)
```
This prevents implementation confusion and ensures consistent tests.

### Strategy 7: DateTime-Specific Edge Case Checklist (Day 2)
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

### Strategy 8: Trust Libraries for Date Arithmetic (Day 2)
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
**Lesson: Don't manually calculate expected test values either!**

### Strategy 9: Standardize Output Even When Input Varies (Day 2)
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

### Strategy 10: Multi-Agent Routing Checklist (Day 2)
Before implementing a coordinator agent, ask:
- [ ] What operations will be routed?
- [ ] Which sub-agent handles each operation?
- [ ] What's the routing mechanism (registry recommended)?
- [ ] How are unknown operations handled?
- [ ] How do sub-agent errors propagate?
- [ ] How can users discover available operations?
- [ ] Is the operation naming intuitive?

### Strategy 11: Eliminate Ambiguity by Design (Day 2)
```
Problem: "reverse 2024-01-15" - string or date operation?

Bad solution: Try to parse and guess
- Complex logic
- Still ambiguous in edge cases
- Hard to test

Good solution: Registry pattern
- User explicitly names operation
- execute("reverse", "2024-01-15") → string operation
- No ambiguity possible by design
```

### Strategy 12: Integration Testing for Multi-Agent (Day 2)
Multi-agent systems need different test categories:

| Category | What to Test |
|----------|--------------|
| Routing | Each operation routes to correct agent |
| Propagation | Sub-agent errors pass through unchanged |
| Validation | Invalid operations rejected with helpful message |
| Discovery | list_operations() returns complete list |
| Integration | Full flow works end-to-end |

### Strategy 13: V2 Planning Checklist (Day 2 v2)
Before implementing v2 improvements, plan:
- [ ] What specific features will be added?
- [ ] Why is each feature valuable? (not just "nice to have")
- [ ] How will each feature be implemented?
- [ ] What edge cases does each feature introduce?
- [ ] How will backwards compatibility be maintained?
- [ ] What new tests are needed?
- [ ] What is the implementation order?
- [ ] What are the success criteria?

V2 planning prevents scope creep and ensures meaningful improvements.

### Strategy 14: Backwards Compatibility Testing (Day 2 v2)
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

## Day 2 Achievements

### StringAgent
- Built `StringAgent` with 5 operations + verify() (45 tests passing)
- Applied Day 1 patterns to new domain (strings)
- **Zero bugs due to planning-first approach**
- Learned: Define ambiguous terms (like "word") before coding
- Learned: Empty strings and whitespace need explicit handling decisions
- Learned: `split()` with no arguments is powerful for whitespace handling

### DateTimeAgent
- Built `DateTimeAgent` with 5 operations + verify() (51 tests passing)
- Applied multi-format date parsing with priority order
- **Zero code bugs** - only error was incorrect test expected value
- Learned: Trust datetime library for leap years and boundaries
- Learned: Don't manually calculate expected date values
- Learned: Standardize output format (ISO 8601) regardless of input
- Learned: DateTimeAgent more complex than StringAgent (parsing + semantic validity)

### UtilityAgent v1 (First Multi-Agent System!)
- Built `UtilityAgent` coordinating StringAgent + DateTimeAgent (32 tests passing)
- Implemented Operation Registry pattern for routing
- **Zero bugs due to planning-first approach**
- Learned: Registry pattern eliminates routing ambiguity
- Learned: Let sub-agent errors propagate (don't wrap them)
- Learned: Include available operations in error messages
- Learned: Multi-agent coordination is different complexity than implementation
- Learned: Integration testing focuses on routing, not edge cases

### UtilityAgent v2 (Day 2 Capstone!)
- Upgraded `UtilityAgent` to v2 with 5 major enhancements (63 tests passing)
- **Enhancement 1**: CalculatorAgent integration (7 new operations, 17 total)
- **Enhancement 2**: Operation aliases (10 shortcuts: rev, upper, now, plus, etc.)
- **Enhancement 3**: `describe()` method for self-documenting API
- **Enhancement 4**: "Did you mean?" suggestions for typos
- **Enhancement 5**: `list_operations_by_category()` for organized discoverability
- **Zero bugs due to comprehensive v2 planning**
- Learned: Alias resolution must happen BEFORE validation
- Learned: Simple prefix matching is sufficient for typo suggestions
- Learned: Backwards compatibility requires running ALL v1 tests unchanged
- Learned: V2 planning prevents scope creep and ensures meaningful improvements

### Day 2 Totals
- Agents built: 4 (StringAgent, DateTimeAgent, UtilityAgent v1, UtilityAgent v2)
- New patterns added: 18 (4 string + 4 datetime + 6 multi-agent + 4 v2)
- New strategies added: 9 (2 string + 2 datetime + 3 multi-agent + 2 v2)
- Tests written: 159 (45 + 51 + 63)
- **ZERO code bugs across ALL FOUR agents**
- First multi-agent system + first v2 improvement successfully built

---

## Day 3 Achievements

### Theme: Error Recovery & Resilience Patterns

### ErrorRecoveryAgent (Session 1)
- Built `ErrorRecoveryAgent` with 5 failure simulators + 5 recovery strategies (42 tests passing)
- Implemented: retry_with_backoff, circuit_breaker, fallback_strategy, graceful_degradation, timeout_wrapper
- Custom exceptions: TransientError, PermanentError, RateLimitError, CircuitOpenError
- **Zero bugs due to planning-first approach**
- Learned: Transient vs Permanent errors require different handling
- Learned: Circuit breaker state machine (CLOSED → OPEN → HALF_OPEN → CLOSED)
- Learned: Exponential backoff with jitter prevents thundering herd

### CalculatorAgent Integration (Session 2)
- Built `CalculatorAgent` with 7 operations (25 tests passing)
- Built `UtilityAgent` integrating CalculatorAgent + ErrorRecoveryAgent (17 tests passing)
- **Zero bugs due to planning-first approach**
- Learned: Calculator operations reuse Day 1 patterns
- Learned: Integration with error recovery agent enables resilience testing

### ResilientUtilityAgent (Session 3 - Day 3 Capstone!)
- Built `ResilientUtilityAgent` combining ALL patterns (58 tests passing)
- **Architecture**: Composes StringAgent + DateTimeAgent + CalculatorAgent (17 operations)
- **Full resilience stack**: Circuit Breaker → Retry → Fallback
- **Per-agent circuit breakers**: Isolated failure domains (3 circuits)
- **Operation-specific fallbacks**: NaN for math, -1 for counts, input for strings
- **Failure injection**: Testing infrastructure for resilience verification
- **Operation logging**: Source tracking (primary, fallback, circuit_open)
- **Zero bugs due to comprehensive planning and critical review**
- Learned: Circuit-first (fail fast) pattern protects both caller and failing service
- Learned: Fallback values should be recognizable as "error" values (not silent failures)
- Learned: Per-agent isolation prevents cascade failures

### Day 3 Totals
- Agents built: 3 (ErrorRecoveryAgent, CalculatorAgent, ResilientUtilityAgent)
- New patterns added: 5 (Patterns 28-32: Resilience patterns)
- Tests written: 142 (42 + 25 + 17 + 58)
- **ZERO code bugs across ALL THREE agents**
- First production-ready resilient system successfully built

---

## Pattern Count

| Section | Patterns |
|---------|----------|
| Code Patterns | 27 (+4 v2 patterns from Day 2) |
| Resilience Patterns | 5 (new from Day 3!) |
| Multi-Agent Patterns | 1 section |
| Mistakes to Avoid | 5 |
| Error Prevention | 14 (+2 v2 strategies from Day 2) |
| Planning Patterns | 5 |
| Review Patterns | 4+ |
| **Total** | **61+** |

---

## Test Count by Day

| Day | Agent | Tests |
|-----|-------|-------|
| Day 1 | sum_even_numbers | 9 |
| Day 1 | CalculatorAgent v1 | 29 |
| Day 1 | CalculatorAgent v2 | 47 |
| Day 2 | StringAgent | 45 |
| Day 2 | DateTimeAgent | 51 |
| Day 2 | UtilityAgent v2 | 63 |
| Day 3 | ErrorRecoveryAgent | 42 |
| Day 3 | CalculatorAgent | 25 |
| Day 3 | UtilityAgent | 17 |
| Day 3 | ResilientUtilityAgent | 58 |
| **Total** | | **386** |

---

Last updated: January 18, 2026
Day 3 - Planning-first continues with ZERO CODE BUGS
**ErrorRecoveryAgent: 42 tests, 0 errors**
**CalculatorAgent: 25 tests, 0 errors**
**ResilientUtilityAgent: 58 tests, 0 errors (Production-ready resilient system!)**
**Cumulative: 386 tests passing**
