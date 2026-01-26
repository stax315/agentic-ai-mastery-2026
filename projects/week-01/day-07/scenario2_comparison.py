"""Scenario 2 Comparison: V0.1 vs V0.2 - Permanent Error Handling."""
import time
import sys
sys.path.insert(0, '/Users/godson/Desktop/python_projects/ai-mastery-2026/projects/week-01/day-06')

from simple_retry_agent import SimpleRetryAgent
from error_recovery_agent_v02 import ErrorRecoveryAgent

def permanent_error():
    """Always raises ValueError - permanent error."""
    raise ValueError("Invalid input - this will never succeed")

def run_scenario_2(agent, agent_name, max_retries=3, delay=0.1):
    """Run 10 operations that all fail with permanent errors."""
    print(f"\n{'='*60}")
    print(f"Scenario 2: {agent_name}")
    print(f"10 operations, all permanent errors (ValueError)")
    print(f"max_retries={max_retries}, delay={delay}s")
    print(f"{'='*60}")

    start = time.time()
    total_attempts = 0

    for i in range(10):
        attempt_count = [0]
        def tracked_op():
            attempt_count[0] += 1
            permanent_error()

        try:
            agent.retry(tracked_op, max_retries, delay)
        except ValueError:
            pass
        total_attempts += attempt_count[0]

    elapsed = time.time() - start

    # Calculate waste
    expected_attempts_no_waste = 10  # 1 attempt per operation (immediate fail)
    actual_retries = total_attempts - 10  # Subtract initial attempts
    max_possible_retries = 10 * (max_retries - 1)  # 10 ops * 2 retries each
    waste_pct = (actual_retries / max_possible_retries * 100) if max_possible_retries > 0 else 0

    print(f"\nResults:")
    print(f"  Time: {elapsed:.3f}s")
    print(f"  Total attempts: {total_attempts}")
    print(f"  Retries: {actual_retries} (wasted)")
    print(f"  Waste: {waste_pct:.0f}%")

    return elapsed, total_attempts, actual_retries, waste_pct

if __name__ == "__main__":
    print("\n" + "="*60)
    print("SCENARIO 2: PERMANENT FAILURES COMPARISON")
    print("Pain point: 'STOP! IT'S THE SAME ERROR!'")
    print("="*60)

    # V0.1: No classification
    v01 = SimpleRetryAgent()
    v01_time, v01_attempts, v01_retries, v01_waste = run_scenario_2(v01, "V0.1 (SimpleRetryAgent)")

    # V0.2: With classification
    v02 = ErrorRecoveryAgent()
    v02_time, v02_attempts, v02_retries, v02_waste = run_scenario_2(v02, "V0.2 (ErrorRecoveryAgent)")

    # Comparison
    print("\n" + "="*60)
    print("COMPARISON SUMMARY")
    print("="*60)
    print(f"\n{'Metric':<20} {'V0.1':<15} {'V0.2':<15} {'Improvement':<15}")
    print("-"*60)
    print(f"{'Time':<20} {v01_time:.3f}s{'':<10} {v02_time:.3f}s{'':<10} {((v01_time-v02_time)/v01_time*100):.0f}% faster")
    print(f"{'Total Attempts':<20} {v01_attempts:<15} {v02_attempts:<15} {v01_attempts - v02_attempts} fewer")
    print(f"{'Wasted Retries':<20} {v01_retries:<15} {v02_retries:<15} {v01_retries - v02_retries} eliminated")
    print(f"{'Waste %':<20} {v01_waste:.0f}%{'':<12} {v02_waste:.0f}%{'':<12} {'SOLVED' if v02_waste == 0 else 'REDUCED'}")

    print("\n" + "="*60)
    print("SCREAMING MOMENT: 'STOP! IT'S THE SAME ERROR!'")
    print("="*60)
    if v02_retries == 0:
        print("✓ SOLVED - Permanent errors now fail IMMEDIATELY")
        print(f"  V0.1 wasted {v01_time:.3f}s retrying the same error")
        print(f"  V0.2 takes {v02_time:.3f}s (no wasted retries)")
    else:
        print("✗ NOT SOLVED - Still retrying permanent errors")
