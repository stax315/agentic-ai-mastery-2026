# SimpleRetryAgent - Simple Version Specification

## Core Function (One Sentence)
> "Retry an operation multiple times with increasing delays when it fails."

## Version: V0.1

---

## Must Have (Minimum Requirements)

- [x] `retry(operation, max_retries=3)` - retry operation with fixed delay
- [x] Basic validation (positive integer for max_retries)
- [x] `verify()` method with 3-5 self-tests
- [x] `verify_print()` method for human-readable output
- [x] `self.version` attribute
- [x] Raises last exception if all retries fail
- [x] Returns result on success

---

## Must NOT Have (Prohibited Complexity)

| Prohibited | Why Excluded |
|------------|--------------|
| Custom exceptions (TransientError, PermanentError) | Use stdlib only - advanced pattern |
| Exponential backoff | Fixed 1s delay is simpler |
| Jitter (randomness) | Deterministic delays are easier to test |
| Circuit breaker | State machine is advanced (Week 17+) |
| Fallback strategy | Convenience, not core function |
| Timeout wrapper | Requires threading (Week 13+) |
| Metrics tracking | Observability is operations concern |
| Failure simulators | Testing aid, not core function |
| max_delay cap | No exponential = no need for cap |
| Operation-specific handling | All errors treated the same |

---

## Design Constraints

| Constraint | Limit | Justification |
|------------|-------|---------------|
| Max LOC | 80 | Fits on one screen |
| Max Public Methods | 3 | retry, verify, verify_print |
| Max Private Methods | 1 | _validate_retries (optional) |
| Prohibited Imports | threading, enum, dataclass | Keeps complexity low |
| Exception Type | ValueError only | stdlib sufficient |
| Delay Type | Fixed (1 second) | No backoff calculation |

---

## Intentional Limitations

| Limitation | What Breaks | Pain Point | Drives Upgrade To |
|------------|-------------|------------|-------------------|
| Fixed delays | No backoff pressure relief | Service recovery slower, retry storms | V0.2 |
| Retries all errors | Retries permanent failures (auth, validation) | Wastes time on errors that will never succeed | V0.2 |
| No circuit breaker | Hammers failing services repeatedly | Prolongs outages, wastes resources | V0.3 |
| No jitter | Thundering herd on recovery | All clients retry at same moment | V0.3 |
| No fallback | All-or-nothing failure | No graceful degradation | V0.4 |
| No timeout | Operations can hang forever | Stuck processes, resource leaks | V0.4 |
| No metrics | Can't observe retry behavior | Debugging production issues blind | V0.5 |

---

## Expected Lifespan

### Works For:
- Simple scripts with occasional network failures
- Learning retry patterns conceptually
- Low-traffic scenarios (few requests/minute)
- Development/testing environments
- Single-service integrations

### Breaks When:
- High traffic (retry storms overwhelm service)
- Mixed error types (permanent errors waste retries)
- Intermittent outages (no circuit protection)
- Production observability needed
- Multiple services failing (cascade failures)

---

## Progression to Next Version

### V0.1 → V0.2 (Smart Retry)

**Current Pain:** Retries permanent errors, wasting time on failures that will never succeed.

**V0.2 Adds:**
- TransientError vs PermanentError distinction
- max_delay cap (prevents absurd delays)
- Exponential backoff (2^attempt formula)

**LOC Increase:** +120 lines (~200 total)

**New Limitation:** Still hammers failing services (no circuit breaker)

---

## API Design

```python
class SimpleRetryAgent:
    """
    Simple retry wrapper for operations that might fail.

    V0.1: Fixed delays, no error classification, basic retry.
    """

    def __init__(self):
        self.version = "0.1"

    def retry(
        self,
        operation: Callable[[], Any],
        max_retries: int = 3,
        delay: float = 1.0
    ) -> Any:
        """
        Retry operation up to max_retries times with fixed delay.

        Args:
            operation: Callable to retry (no arguments)
            max_retries: Maximum retry attempts (default 3)
            delay: Fixed delay between retries in seconds (default 1.0)

        Returns:
            Result from operation if successful

        Raises:
            ValueError: If max_retries < 1 or delay <= 0
            Exception: Last exception if all retries fail
        """
        pass

    def verify(self) -> dict:
        """Run self-tests, return results dict."""
        pass

    def verify_print(self) -> bool:
        """Run self-tests, print readable output, return pass/fail."""
        pass
```

---

## Test Plan (15-20 tests)

| Test Category | Count | Examples |
|---------------|-------|----------|
| Happy path | 3 | Succeeds first try, succeeds on retry, returns correct value |
| Validation | 4 | None retries, zero retries, negative retries, bool rejection |
| Retry behavior | 5 | Fails then succeeds, exhausts retries, correct attempt count |
| Error propagation | 3 | Last exception raised, original error type preserved |
| verify() tests | 3 | Returns dict, correct keys, all tests pass |

**Total:** ~18 tests (right-sized for simple agent)

---

## Pseudocode Implementation

```python
def retry(self, operation, max_retries=3, delay=1.0):
    # Validate inputs
    if max_retries < 1:
        raise ValueError("max_retries must be >= 1")
    if delay <= 0:
        raise ValueError("delay must be > 0")

    last_exception = None

    for attempt in range(max_retries):
        try:
            return operation()  # Success - return immediately
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                time.sleep(delay)  # Fixed delay

    # All retries failed
    raise last_exception
```

---

## Comparison: V0.1 vs V1.0 (Current ErrorRecoveryAgent)

| Aspect | V0.1 (SimpleRetryAgent) | V1.0 (ErrorRecoveryAgent) |
|--------|-------------------------|---------------------------|
| LOC | ~80 | 850 |
| Public methods | 3 | 10+ |
| Exception types | stdlib only | 4 custom (Transient, Permanent, RateLimit, CircuitOpen) |
| Delay strategy | Fixed | Exponential + jitter |
| State tracking | None | Circuit breaker state machine |
| Metrics | None | Full retry/circuit metrics |
| Fallback | None | primary → fallback → default chain |
| Timeout | None | Threading-based timeout wrapper |
| Testing support | None | Failure injection |

**Complexity ratio:** ~10x simpler

---

## Verification Checklist

After building V0.1:

- [ ] Core function fits in ONE sentence
- [ ] ≤3 public methods (retry, verify, verify_print)
- [ ] ≤80 LOC total
- [ ] No prohibited patterns (threading, dataclass, enum)
- [ ] Every limitation has documented pain point
- [ ] Progression path to V0.2 is clear
- [ ] All tests pass
- [ ] verify() returns correct structure

---

## Key Learning Objectives

Building V0.1 teaches:

1. **Basic retry mechanics** - The core loop pattern
2. **Why fixed delays are insufficient** - Experience the pain before learning backoff
3. **Why error classification matters** - Watch permanent errors waste retries
4. **The value of simplicity** - 80 lines does 80% of the job

**What V0.1 doesn't teach (intentionally):**
- Why exponential backoff prevents thundering herd
- Why circuit breakers protect failing services
- Why fallbacks enable graceful degradation

*These are learned by experiencing V0.1's limitations, then building V0.2+*

---

Created: January 20, 2026
Part of: Day 5 - Two-Session Review Workflow
Derived from: ErrorRecoveryAgent complexity analysis
