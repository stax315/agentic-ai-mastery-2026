"""Stress tests for SimpleRetryAgent V0.1 - Revealing limitations."""
import time
import random
from simple_retry_agent import SimpleRetryAgent


def print_metrics(name: str, metrics: dict) -> None:
    """Display metrics in readable format."""
    print(f"\n{'='*60}")
    print(f"SCENARIO: {name}")
    print(f"{'='*60}")
    print(f"Total time:        {metrics['total_time']:.3f}s")
    print(f"Wasted time:       {metrics['wasted_time']:.3f}s")
    print(f"Total attempts:    {metrics['total_attempts']}")
    print(f"Successful ops:    {metrics['successful_ops']}")
    print(f"Failed ops:        {metrics['failed_ops']}")
    if metrics['failed_ops'] > 0:
        print(f"Wasted/failed op:  {metrics['wasted_time']/metrics['failed_ops']:.3f}s")
    total_ops = metrics['successful_ops'] + metrics['failed_ops']
    if total_ops > 0:
        print(f"Time per op:       {metrics['total_time']/total_ops:.3f}s")
        print(f"Success rate:      {100*metrics['successful_ops']/total_ops:.1f}%")
    print(f"{'='*60}\n")


def scenario_1_high_volume():
    """100 operations with 20% failure rate - reveals cumulative delay cost."""
    print("\n" + "="*60)
    print("SCENARIO 1: HIGH VOLUME STRESS")
    print("100 operations, 20% failure rate, max_retries=3, delay=0.1s")
    print("="*60)

    agent = SimpleRetryAgent()
    metrics = {
        "total_time": 0,
        "wasted_time": 0,
        "total_attempts": 0,
        "successful_ops": 0,
        "failed_ops": 0,
    }

    # Set seed for reproducible 20% failure rate
    random.seed(42)

    start_total = time.time()

    for i in range(100):
        # 20% chance of persistent failure (simulates permanent errors mixed in)
        will_permanently_fail = random.random() < 0.05  # 5% permanent failures
        will_transiently_fail = random.random() < 0.15  # 15% transient (recoverable)

        attempts = [0]
        op_start = time.time()

        def make_operation(idx, perm_fail, trans_fail, att):
            def operation():
                att[0] += 1
                if perm_fail:
                    raise ValueError(f"Permanent error op {idx}")
                if trans_fail and att[0] < 2:
                    raise RuntimeError(f"Transient error op {idx}")
                return f"result_{idx}"
            return operation

        try:
            result = agent.retry(
                make_operation(i, will_permanently_fail, will_transiently_fail, attempts),
                max_retries=3,
                delay=0.1
            )
            op_time = time.time() - op_start
            metrics["successful_ops"] += 1
            metrics["total_attempts"] += attempts[0]
            # Time spent on retries before success is "recovered" time
        except Exception:
            op_time = time.time() - op_start
            metrics["failed_ops"] += 1
            metrics["total_attempts"] += attempts[0]
            metrics["wasted_time"] += op_time  # All time on failed ops is wasted

        # Progress indicator every 20 ops
        if (i + 1) % 20 == 0:
            print(f"  Progress: {i+1}/100 operations completed...")

    metrics["total_time"] = time.time() - start_total
    print_metrics("High Volume (100 ops, 20% failure rate)", metrics)
    return metrics


def scenario_2_permanent_failures():
    """10 operations that always fail - reveals wasted retries."""
    print("\n" + "="*60)
    print("SCENARIO 2: SUSTAINED PERMANENT FAILURES")
    print("10 operations that ALWAYS fail (simulating auth/validation errors)")
    print("max_retries=3, delay=0.1s")
    print("="*60)

    agent = SimpleRetryAgent()
    metrics = {
        "total_time": 0,
        "wasted_time": 0,
        "total_attempts": 0,
        "successful_ops": 0,
        "failed_ops": 0,
    }

    start_total = time.time()

    for i in range(10):
        attempts = [0]
        op_start = time.time()

        def always_fail(idx, att):
            def operation():
                att[0] += 1
                # Simulates permanent error: invalid credentials, bad input, etc.
                raise ValueError(f"PERMANENT ERROR: Invalid API key for op {idx}")
            return operation

        print(f"  Op {i+1}: Attempting (will never succeed)...", end=" ")
        try:
            agent.retry(always_fail(i, attempts), max_retries=3, delay=0.1)
        except ValueError:
            op_time = time.time() - op_start
            metrics["failed_ops"] += 1
            metrics["total_attempts"] += attempts[0]
            metrics["wasted_time"] += op_time
            print(f"FAILED after {attempts[0]} attempts ({op_time:.2f}s wasted)")

    metrics["total_time"] = time.time() - start_total
    print_metrics("Permanent Failures (10 ops, 100% failure)", metrics)
    return metrics


def scenario_3_thundering_herd():
    """5 services fail simultaneously - reveals synchronized retries."""
    print("\n" + "="*60)
    print("SCENARIO 3: THUNDERING HERD SIMULATION")
    print("5 'services' all fail at t=0, all retry at exactly the same moments")
    print("max_retries=3, delay=0.1s")
    print("="*60)

    agent = SimpleRetryAgent()

    # Track when each retry happens across all "services"
    retry_timestamps = {f"service_{i}": [] for i in range(5)}

    metrics = {
        "total_time": 0,
        "wasted_time": 0,
        "total_attempts": 0,
        "successful_ops": 0,
        "failed_ops": 0,
    }

    start_total = time.time()

    # Simulate recovery after some time (service recovers at attempt 3)
    for svc_id in range(5):
        attempts = [0]
        svc_name = f"service_{svc_id}"
        op_start = time.time()

        def service_operation(name, att, timestamps, base_time):
            def operation():
                att[0] += 1
                timestamps[name].append(time.time() - base_time)
                if att[0] < 3:  # Fail first 2 attempts, succeed on 3rd
                    raise ConnectionError(f"{name} unavailable")
                return f"{name}_ok"
            return operation

        try:
            result = agent.retry(
                service_operation(svc_name, attempts, retry_timestamps, start_total),
                max_retries=3,
                delay=0.1
            )
            metrics["successful_ops"] += 1
        except Exception:
            metrics["failed_ops"] += 1
            metrics["wasted_time"] += time.time() - op_start

        metrics["total_attempts"] += attempts[0]

    metrics["total_time"] = time.time() - start_total

    # Analyze thundering herd effect
    print("\n  RETRY TIMING ANALYSIS (seconds from start):")
    print("  " + "-"*50)
    for svc, timestamps in retry_timestamps.items():
        ts_str = ", ".join([f"{t:.3f}s" for t in timestamps])
        print(f"  {svc}: [{ts_str}]")

    # Show synchronized pattern
    print("\n  THUNDERING HERD VISUALIZATION:")
    print("  " + "-"*50)
    all_times = []
    for ts_list in retry_timestamps.values():
        all_times.extend(ts_list)

    # Group attempts by time window (within 0.01s = same "moment")
    time_buckets = {}
    for t in sorted(all_times):
        bucket = round(t, 1)  # Round to 0.1s bucket
        time_buckets[bucket] = time_buckets.get(bucket, 0) + 1

    print("  Time (s) | Concurrent Attempts")
    for bucket, count in sorted(time_buckets.items()):
        bar = "#" * count
        print(f"  {bucket:>6.1f}   | {bar} ({count})")

    print_metrics("Thundering Herd (5 services, synchronized)", metrics)
    return metrics


def run_all_stress_tests():
    """Execute all stress test scenarios."""
    print("\n" + "="*70)
    print("  SIMPLERETRYAGENT V0.1 STRESS TESTS")
    print("  Objective: Reveal V0.1 limitations through experience")
    print("="*70)

    results = {}

    # Scenario 1: High Volume
    results["high_volume"] = scenario_1_high_volume()

    # Scenario 2: Permanent Failures
    results["permanent_failures"] = scenario_2_permanent_failures()

    # Scenario 3: Thundering Herd
    results["thundering_herd"] = scenario_3_thundering_herd()

    # Summary
    print("\n" + "="*70)
    print("  STRESS TEST SUMMARY")
    print("="*70)

    total_wasted = sum(r["wasted_time"] for r in results.values())
    total_attempts = sum(r["total_attempts"] for r in results.values())
    total_failed = sum(r["failed_ops"] for r in results.values())

    print(f"\n  Total wasted time across all scenarios: {total_wasted:.2f}s")
    print(f"  Total retry attempts: {total_attempts}")
    print(f"  Total failed operations: {total_failed}")

    if total_failed > 0:
        print(f"  Average wasted time per failure: {total_wasted/total_failed:.3f}s")

    print("\n" + "="*70)

    return results


if __name__ == "__main__":
    run_all_stress_tests()
