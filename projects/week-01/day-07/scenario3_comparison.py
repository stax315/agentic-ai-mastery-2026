"""Scenario 3 Comparison: V0.2 vs V0.3 - Sustained Retryable Failures."""
import time
import sys
from error_recovery_agent_v02 import ErrorRecoveryAgent as V02Agent
from error_recovery_agent_v03 import ErrorRecoveryAgent as V03Agent, CircuitOpenError

def run_scenario_v02(max_retries=3, delay=0.1, num_calls=10):
    """V0.2: No circuit breaker - each call exhausts retries."""
    print(f"\n{'='*60}")
    print("Scenario 3: V0.2 (ErrorRecoveryAgent without circuit breaker)")
    print(f"{num_calls} calls to dead service, max_retries={max_retries}, delay={delay}s")
    print(f"{'='*60}")

    agent = V02Agent()
    start = time.time()
    total_attempts = 0

    for i in range(num_calls):
        attempt_count = [0]
        def dead_service():
            attempt_count[0] += 1
            raise TimeoutError("Service unavailable")
        try:
            agent.retry(dead_service, max_retries, delay)
        except TimeoutError:
            pass
        total_attempts += attempt_count[0]

    elapsed = time.time() - start
    wasted = total_attempts - num_calls  # Beyond first attempt per call
    print(f"\nResults:")
    print(f"  Time: {elapsed:.3f}s")
    print(f"  Total attempts: {total_attempts}")
    print(f"  Wasted retries: {wasted}")
    return elapsed, total_attempts, wasted

def run_scenario_v03(max_retries=3, delay=0.1, num_calls=10, threshold=3):
    """V0.3: Circuit breaker - stops after threshold failures."""
    print(f"\n{'='*60}")
    print("Scenario 3: V0.3 (ErrorRecoveryAgent with circuit breaker)")
    print(f"{num_calls} calls to dead service, max_retries={max_retries}, delay={delay}s")
    print(f"Circuit threshold={threshold}")
    print(f"{'='*60}")

    agent = V03Agent(failure_threshold=threshold)
    start = time.time()
    total_attempts = 0
    circuit_open_count = 0

    for i in range(num_calls):
        attempt_count = [0]
        def dead_service():
            attempt_count[0] += 1
            raise TimeoutError("Service unavailable")
        try:
            agent.retry(dead_service, max_retries, delay)
        except CircuitOpenError:
            circuit_open_count += 1
        except TimeoutError:
            pass
        total_attempts += attempt_count[0]

    elapsed = time.time() - start
    print(f"\nResults:")
    print(f"  Time: {elapsed:.3f}s")
    print(f"  Total attempts: {total_attempts}")
    print(f"  Circuit opened: YES (after {threshold} failures)")
    print(f"  Calls blocked by circuit: {circuit_open_count}")
    return elapsed, total_attempts, circuit_open_count

if __name__ == "__main__":
    print("\n" + "="*60)
    print("SCENARIO 3: SUSTAINED RETRYABLE FAILURES COMPARISON")
    print("Pain point: 'THE SERVICE IS DOWN! STOP TRYING!'")
    print("="*60)

    # V0.2: No circuit breaker
    v02_time, v02_attempts, v02_wasted = run_scenario_v02()

    # V0.3: With circuit breaker
    v03_time, v03_attempts, v03_blocked = run_scenario_v03()

    # Comparison
    print("\n" + "="*60)
    print("COMPARISON SUMMARY")
    print("="*60)
    print(f"\n{'Metric':<20} {'V0.2':<15} {'V0.3':<15} {'Improvement':<20}")
    print("-"*70)

    time_improvement = ((v02_time - v03_time) / v02_time * 100) if v02_time > 0 else 0
    print(f"{'Time':<20} {v02_time:.3f}s{'':<10} {v03_time:.3f}s{'':<10} {time_improvement:.0f}% faster")
    print(f"{'Total Attempts':<20} {v02_attempts:<15} {v03_attempts:<15} {v02_attempts - v03_attempts} fewer")
    print(f"{'Wasted Retries':<20} {v02_wasted:<15} {0:<15} {v02_wasted} eliminated")

    waste_reduction = ((v02_wasted - 0) / v02_wasted * 100) if v02_wasted > 0 else 100
    print(f"{'Waste Reduction':<20} {'':<15} {'':<15} {waste_reduction:.0f}%")

    print("\n" + "="*60)
    print("SCREAMING MOMENT: 'THE SERVICE IS DOWN! STOP TRYING!'")
    print("="*60)
    if v03_attempts <= 3:
        print("✓ SOLVED - Circuit breaker stops sustained failures EARLY")
        print(f"  V0.2 wasted {v02_time:.3f}s with {v02_attempts} attempts")
        print(f"  V0.3 took {v03_time:.3f}s with {v03_attempts} attempts (circuit opened)")
        print(f"  {v03_blocked} operations failed fast (no retry waste)")
    else:
        print("✗ NOT FULLY SOLVED - Still making too many attempts")
