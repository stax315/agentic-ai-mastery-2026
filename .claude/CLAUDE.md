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

Last updated: January 19, 2026
Week 1 Complete: 13 agents, 425 tests, 0 bugs
