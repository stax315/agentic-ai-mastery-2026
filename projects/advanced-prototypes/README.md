# Advanced Prototypes: Built Early, Study Later

## Purpose

These agents were built during Week 1 Days 3-4, jumping ahead to Week 17-20 complexity. They demonstrate production-grade patterns but were built before completing foundational learning.

**Key Insight:** I can *implement* these patterns, but I haven't *discovered* why they're needed through progressive learning.

---

## Agents Preserved

### 1. ErrorRecoveryAgent
- **File:** `error_recovery_agent.py`
- **Tests:** `test_error_recovery_agent.py` (42 tests)
- **Complexity:** Week 17-20 level

**Patterns Demonstrated:**
- Custom exception hierarchy (TransientError vs PermanentError)
- Circuit breaker state machine (CLOSED -> OPEN -> HALF_OPEN)
- Exponential backoff with jitter
- Fallback strategy with graceful degradation
- Failure injection for deterministic testing
- Timeout wrapper using threading

### 2. ResilientUtilityAgent
- **File:** `resilient_utility_agent.py`
- **Tests:** `test_resilient_utility_agent.py` (58 tests)
- **Complexity:** Week 17-20 level

**Patterns Demonstrated:**
- Resilient wrapper (Circuit Breaker -> Retry -> Fallback layering)
- Per-agent circuit breaker isolation
- Recognizable fallback values (NaN for calc, epoch for dates)
- Failure injection for testing resilience
- Operation logging with source tracking
- Configurable retry/circuit settings

---

## Also Preserved (Day 4 - Off-Roadmap Topic)

These agents were built on Day 4 as a "simplicity pivot" but the roadmap called for Conversation Memory instead. They're preserved here but are actually **simple** agents, not advanced.

### 3. FileOperationsAgent
- **File:** `file_operations_agent.py`
- **Tests:** `test_file_operations_agent.py` (18 tests)
- **Complexity:** Simple (intentionally minimal)
- **Note:** Good example of anti-overengineering, but built off-roadmap

### 4. APIAgent
- **File:** `api_agent.py`
- **Tests:** `test_api_agent.py` (21 tests)
- **Complexity:** Simple (mock-based learning)
- **Note:** Demonstrates retry pattern with mocked responses

---

## When to Revisit

**Target:** Week 17-20 (Production Patterns & Optimization phase)

At that point:
1. Compare these early prototypes to current understanding
2. Extract patterns missed during initial build
3. Refactor with full foundational knowledge
4. Document the learning difference
5. Understand WHY each pattern exists (after experiencing the pain)

---

## Current Value

- **Proof that I CAN build:** Advanced resilience systems
- **Proof that I CAN test:** 100 tests, all passing
- **Proof that I CAN document:** Full pattern extraction

## Future Value

- **Proof that I UNDERSTAND:** Why these patterns exist
- **Proof that I PROGRESSED:** From simple to complex deliberately
- **Proof that I LEARNED:** The foundational pain points

---

## What's Missing (To Build First)

Before revisiting these agents, complete:

1. **Simple Retry** - Fixed delay, no backoff
2. **Simple Error Propagation** - Just log and re-raise
3. **Simple Memory** - List + JSON save/load
4. **Sequential Agent Calls** - A -> B -> C without orchestration
5. **Basic Circuit Breaker** - Just failure count, no states

These simple versions will reveal WHY the advanced patterns in this directory are needed.

---

## File Structure

```
advanced-prototypes/
├── README.md                       # This file
├── error_recovery_agent.py         # Advanced resilience patterns
├── resilient_utility_agent.py      # Full resilience stack
├── file_operations_agent.py        # Simple file I/O (off-roadmap)
├── api_agent.py                    # Simple mock HTTP (off-roadmap)
├── test_error_recovery_agent.py    # 42 tests
├── test_resilient_utility_agent.py # 58 tests
├── test_file_operations_agent.py   # 18 tests
└── test_api_agent.py               # 21 tests
```

---

## Stats

| Agent | Methods | Tests | Complexity |
|-------|---------|-------|------------|
| ErrorRecoveryAgent | 10+ | 42 | Week 17-20 |
| ResilientUtilityAgent | 17 ops | 58 | Week 17-20 |
| FileOperationsAgent | 4 | 18 | Simple |
| APIAgent | 3 | 21 | Simple |
| **Total** | | **139** | Mixed |

---

Last updated: January 20, 2026
Original build: Week 1 Days 3-4
Appropriate revisit: Week 17-20
