# Anti-Patterns (What NOT to Do)

Patterns to AVOID. Anti-overengineering discipline.

---

## Style Guide
- Use existing patterns; examine codebase first
- Minimal changes only: surgical edits, no refactors unless breaking

---

## What NOT to Do (Anti-Overengineering)
- No abstractions until duplication exists
- No design patterns unless problem demands them
- No complex error handling for 1% edge cases
- No configurations for rarely-changing values
- No new utils/helpers for one-off logic
- Inline simple functions; reuse existing code first
- Minimal changes only: edit files surgically
- Assume happy path until proven otherwise

---

## Day 4 Anti-Overengineering Wins
- **No _validate methods** for simple agents (inline is cleaner)
- **No custom exceptions** (ValueError, ConnectionError sufficient)
- **No real HTTP** (mocks sufficient for learning patterns)
- **No async** (blocking fine for learning)
- **20 tests, not 40+** for simple agents (right-sized for complexity)
- **0 abstractions** created in Day 4 (inline everything)

---

## When to Abstract

| Abstract When | Evidence |
|---------------|----------|
| Same code appears 3+ times | Duplication proven |
| Abstraction simplifies | Clear improvement |
| Pattern is reusable | Used across agents |
| Cost of abstraction < cost of duplication | Net benefit |

**Default:** DON'T abstract. Wait for duplication to prove need.

---

## When to Inline

| Inline When | Evidence |
|-------------|----------|
| Single use case | Only used once |
| Logic is simple (1-5 lines) | No complexity hidden |
| Abstraction would obscure meaning | Indirection hurts |
| No duplication proven yet | Premature otherwise |

**Day 4 proof:** file_operations_agent and api_agent have NO _validate methods. Inline validation is cleaner for simple agents.

---

## When to Mock

| Mock When | Example |
|-----------|---------|
| External dependencies | APIs, databases, network |
| Non-deterministic behavior | Random, current time |
| Slow operations | time.sleep(), large I/O |
| Testing error scenarios | Flaky endpoints, failures |

**Day 4 proof:** `@patch('api_agent.time.sleep')` makes retry tests instant instead of minutes.

---

## When to Skip

| Skip | Why |
|------|-----|
| 1% edge cases | Until encountered in practice |
| Custom exceptions | Built-ins (ValueError, ConnectionError) sufficient |
| Configuration files | Hardcoded values fine for learning |
| Async code | Blocking simpler until proven insufficient |
| Helper utilities | Inline until duplication exists |

---

## Optional Patterns (Use When Needed)

| Pattern | When to Use | When to Skip |
|---------|-------------|--------------|
| `_validate_*` methods | 3+ methods share validation | Simple agents (≤4 methods) |
| Operation Registry | Multi-agent coordinators | Single-purpose agents |
| Retry with backoff | I/O operations (API, file, network) | Pure computation |
| Circuit breaker | High-reliability production | Learning/practice code |
| Custom exceptions | Learning resilience patterns | All other cases |
| Separate test files | Agents with 5+ methods | Simple agents |

---

## Multi-Agent Routing Checklist

Before implementing a coordinator agent, ask:
- [ ] What operations will be routed?
- [ ] Which sub-agent handles each operation?
- [ ] What's the routing mechanism (registry recommended)?
- [ ] How are unknown operations handled?
- [ ] How do sub-agent errors propagate?
- [ ] How can users discover available operations?
- [ ] Is the operation naming intuitive?

---

## Eliminate Ambiguity by Design

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

---

## V2 Planning Checklist

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

---

Last updated: January 19, 2026
