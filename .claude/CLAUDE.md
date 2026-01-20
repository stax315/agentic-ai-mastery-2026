# AI Development Knowledge Base - Master Index

## Quick Reference (CRITICAL RULES)

### Rule #1: ALWAYS PLAN FIRST
Before writing ANY code, create a detailed plan with steps, files, tests, verification.
**Proof: 4 days, 13 agents, 0 bugs - all through planning-first.**

### Rule #2: DOCUMENT EVERY ERROR
Capture in ERROR_LOG.md: what happened, why, how to prevent.

### Rule #3: TEST-AS-YOU-GO
Write tests after each method. Never batch testing at the end.

---

## Anti-Overengineering (CRITICAL)

- No abstractions until duplication exists (3+ times)
- No design patterns unless problem demands them
- No complex error handling for 1% edge cases
- Inline simple functions; reuse existing code first
- Happy path first, edge cases when encountered
- **See:** [patterns/anti-patterns.md](patterns/anti-patterns.md)

---

## Pattern Files (Organized by Topic)

### Core Patterns
**File:** [patterns/core-patterns.md](patterns/core-patterns.md)
- verify() method (universal - MUST have)
- Input validation patterns
- Agent class structure
- String/DateTime patterns
- Inline validation for simple agents

### Multi-Agent Patterns
**File:** [patterns/multi-agent-patterns.md](patterns/multi-agent-patterns.md)
- Operation Registry (recommended routing)
- Agent composition
- Error propagation
- Alias resolution, typo suggestions
- Integration testing

### Error & Resilience Patterns
**File:** [patterns/error-patterns.md](patterns/error-patterns.md)
- Retry with exponential backoff
- Circuit breaker (per-agent isolation)
- Fallback strategies
- Failure injection for testing
- Error prevention strategies

### Testing Patterns
**File:** [patterns/testing-patterns.md](patterns/testing-patterns.md)
- Test count guidance (15-50 tests based on complexity)
- Mock testing for fast tests
- Integration testing strategy
- Planning patterns
- Code review checklist

### Anti-Patterns (What NOT to Do)
**File:** [patterns/anti-patterns.md](patterns/anti-patterns.md)
- Overengineering examples
- When to inline vs abstract
- 1% edge cases to skip
- Complexity to avoid
- V2 planning checklist

### Meta-Patterns (Learning Efficiency)
**File:** [patterns/meta-patterns.md](patterns/meta-patterns.md)
- Pattern replication speed (2x by Day 4)
- 7-minute integration proof
- Simplicity metrics
- Day-by-day achievements
- Test counts and statistics

---

## Usage

### Starting a Session:
1. Review this file (core rules above)
2. Check relevant pattern file for today's work
3. Plan before building

### After Each Session:
- Add new patterns to appropriate file
- Update this index if new categories emerge
- Document errors in ERROR_LOG.md

---

## Stats (Week 1 Complete)

| Day | Theme | Agents | Tests | Bugs |
|-----|-------|--------|-------|------|
| Day 1 | Foundation | 3 | 85 | 0 |
| Day 2 | Multi-Agent | 4 | 159 | 0 |
| Day 3 | Resilience | 4 | 142 | 0 |
| Day 4 | Simplicity | 2 | 39 | 0 |
| **Total** | | **13** | **425** | **0** |

**Pattern files:** 6
**Total patterns:** 65+
**Learning velocity:** 2x improvement from Day 1

---

## Test Count Guidance

| Agent Complexity | Recommended Tests |
|------------------|-------------------|
| Simple (2-4 methods) | 15-25 tests |
| Medium (5-8 methods) | 30-50 tests |
| Complex (9+ methods) | 50+ tests |

---

## Universal Patterns (ALWAYS Use)

Every new agent MUST have:
- `verify()` method - self-test returning dict
- `verify_print()` method - human-readable output
- `self.version` attribute - track versions
- `ValueError` for validation errors
- Docstrings on all public methods

---

## ADVANCED PATTERNS (Built Early - Revisit Week 17-20)

These patterns were implemented on Days 3-4, jumping ahead of the roadmap.
Document what was learned for future reference.

### Production-Grade Error Handling (ErrorRecoveryAgent)

**What I Learned:**
- Custom exception hierarchy matters: `TransientError` vs `PermanentError` enables smart retry decisions
- Retry shouldn't be blind - permanent errors should fail immediately
- Validation errors are permanent; network timeouts are transient
- Error messages should include context (what operation, what value)

**Key Patterns:**
```python
class TransientError(Exception):
    """Error that might succeed on retry (network timeout, rate limit)."""
    pass

class PermanentError(Exception):
    """Error that will NOT succeed on retry (invalid input, auth failure)."""
    pass
```

### Retry with Exponential Backoff

**What I Learned:**
- Formula: `delay = min(base_delay * 2^attempt, max_delay)`
- Jitter prevents thundering herd: `delay * random(0.5, 1.5)`
- Must cap max_delay or delays become absurd
- Track metrics for observability

**Implementation Insight:**
```python
for attempt in range(max_retries + 1):
    try:
        return operation()
    except PermanentError:
        raise  # Don't retry permanent errors
    except Exception:
        delay = min(base_delay * (2 ** attempt), max_delay)
        if jitter:
            delay *= random.uniform(0.5, 1.5)
        time.sleep(delay)
```

### Circuit Breaker (Per-Agent Isolation)

**What I Learned:**
- State machine: CLOSED -> OPEN -> HALF_OPEN -> CLOSED
- OPEN = fail fast (protect failing service from overload)
- HALF_OPEN = test if service recovered
- Per-operation isolation prevents cascade failures
- Need reset_timeout to know when to try again

**State Transitions:**
- CLOSED --[failures >= threshold]--> OPEN
- OPEN --[timeout elapsed]--> HALF_OPEN
- HALF_OPEN --[success]--> CLOSED
- HALF_OPEN --[failure]--> OPEN

### Fallback Strategies

**What I Learned:**
- Fallbacks should be recognizable as "degraded" values
- Calculator: Return NaN (math convention for undefined)
- DateTime: Return epoch (1970-01-01) or midnight (00:00:00)
- Strings: Return input unchanged (safe default)
- Count operations: Return -1 (0 is valid for empty input)

**Graceful Degradation Pattern:**
```python
def graceful_degradation(operations):
    """Execute multiple ops, return partial results on failures."""
    results = {}
    errors = {}
    for name, op in operations.items():
        try:
            results[name] = op()
        except Exception as e:
            errors[name] = str(e)
    return {"results": results, "errors": errors, "success_rate": ...}
```

### Resilient Wrapper (ResilientUtilityAgent)

**What I Learned:**
- Layer order matters: Circuit Breaker -> Retry -> Fallback
- Circuit breaker is outermost (fail fast if service down)
- Retry is middle (handle transient failures)
- Fallback is innermost (return safe default if all fails)

**Resilience Stack:**
```python
def _execute_with_resilience(operation, args):
    try:
        # 1. Circuit breaker (per-agent isolation)
        # 2. Retry with backoff
        return retry_with_backoff(circuit_breaker(raw_operation))
    except CircuitOpenError:
        return fallback_value  # Circuit open - fail fast
    except Exception:
        return fallback_value  # All retries failed
```

### Failure Injection for Testing

**What I Learned:**
- Inject failures to test resilience without real external services
- Control failure type (transient vs permanent) and count
- Reset state between tests
- Makes resilience testable and deterministic

---

## FOUNDATIONAL PATTERNS (To Revisit)

### Patterns I May Have Skipped by Jumping Ahead:

1. **Simple Error Handling (Before Production-Grade)**
   - Basic try/except without custom exceptions
   - Single retry without backoff
   - Simple error messages without context
   - *Why it matters:* Understanding simple patterns first reveals why complex ones exist

2. **Basic API Integration (Before Multi-Provider)**
   - Single API, no fallback
   - Simple request/response without retry
   - Manual error handling
   - *Why it matters:* Production patterns make more sense after feeling the pain

3. **Sequential Agent Coordination (Before Resilient Systems)**
   - Agents call each other directly
   - No registry, no routing abstraction
   - Errors propagate naturally
   - *Why it matters:* Helps appreciate why registries and wrappers help

4. **Code Review Workflow (Two-Session Pattern)**
   - Session 1: Build, basic tests
   - Session 2: Review, edge cases, production hardening
   - *Why it matters:* v1 -> v2 evolution teaches incremental improvement

### Why Building Simple First Teaches Deeper Patterns:

1. **Pain-Driven Learning:** You don't appreciate retry patterns until you've manually recovered from failures

2. **Incremental Complexity:** Each layer of abstraction solves a specific problem you've already encountered

3. **Debugging Clarity:** Simpler systems are easier to debug; understanding them helps debug complex ones

4. **Anti-Pattern Recognition:** Building simple first helps recognize when complexity is actually needed vs. premature

### Recommended Sequence (If Restarting):

```
Week 1-2: Single-domain agents, basic validation
Week 3-4: Multi-agent coordination, simple routing
Week 5-8: Basic API integration, simple retry
Week 9-12: Error handling evolution (simple -> production)
Week 13-16: System integration basics
Week 17-20: Full resilience patterns (what I built on Day 3)
```

---

## Inventory Reference

For detailed agent-by-agent breakdown, see: [AGENT_INVENTORY.md](../AGENT_INVENTORY.md)

---

Last updated: January 20, 2026
Week 1 Complete: 9 unique agents, 425 tests, 0 bugs
