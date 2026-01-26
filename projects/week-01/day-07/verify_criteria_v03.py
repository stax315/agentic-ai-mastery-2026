"""Verify all V0.3 success criteria."""
from error_recovery_agent_v03 import ErrorRecoveryAgent, CircuitOpenError
import time
import subprocess

print("="*60)
print("V0.3 SUCCESS CRITERIA VERIFICATION")
print("="*60)

all_pass = True

# 1. Circuit opens after N failures
print("\n1. Circuit opens after threshold failures")
agent = ErrorRecoveryAgent(failure_threshold=3)
for _ in range(3):
    try: agent.retry(lambda: (_ for _ in ()).throw(TimeoutError()), 1, 0.001)
    except TimeoutError: pass
result = agent.circuit_open == True
print(f"   circuit_open: {agent.circuit_open} (expected: True)")
print(f"   Status: {'✓ PASS' if result else '✗ FAIL'}")
all_pass = all_pass and result

# 2. Operations fail when open
print("\n2. Operations fail when circuit open")
agent = ErrorRecoveryAgent(failure_threshold=1)
try: agent.retry(lambda: (_ for _ in ()).throw(TimeoutError()), 1, 0.001)
except TimeoutError: pass
try:
    agent.retry(lambda: "ok", 1, 0.001)
    result = False
except CircuitOpenError:
    result = True
print(f"   CircuitOpenError raised: {result}")
print(f"   Status: {'✓ PASS' if result else '✗ FAIL'}")
all_pass = all_pass and result

# 3. Circuit closes after success
print("\n3. Circuit closes after success")
agent = ErrorRecoveryAgent(failure_threshold=3)
agent._consecutive_failures = 2
agent.retry(lambda: "ok", 1, 0.001)
result = agent.circuit_open == False and agent.consecutive_failures == 0
print(f"   circuit_open: {agent.circuit_open}, failures: {agent.consecutive_failures}")
print(f"   Status: {'✓ PASS' if result else '✗ FAIL'}")
all_pass = all_pass and result

# 4. Permanent errors don't count
print("\n4. Permanent errors don't affect circuit")
agent = ErrorRecoveryAgent(failure_threshold=3)
for _ in range(10):
    try: agent.retry(lambda: (_ for _ in ()).throw(ValueError()), 1, 0.001)
    except ValueError: pass
result = agent.circuit_open == False and agent.consecutive_failures == 0
print(f"   After 10 ValueErrors: circuit_open={agent.circuit_open}, failures={agent.consecutive_failures}")
print(f"   Status: {'✓ PASS' if result else '✗ FAIL'}")
all_pass = all_pass and result

# 5. Circuit state observable
print("\n5. Circuit state observable via properties")
agent = ErrorRecoveryAgent(failure_threshold=5)
agent._consecutive_failures = 3
agent._circuit_open = True
prop_result = agent.circuit_open == True and agent.consecutive_failures == 3
print(f"   circuit_open property: {agent.circuit_open}")
print(f"   consecutive_failures property: {agent.consecutive_failures}")
print(f"   Status: {'✓ PASS' if prop_result else '✗ FAIL'}")
all_pass = all_pass and prop_result

# 6. Scenario 3 < 0.5s
print("\n6. Scenario 3 completes in <0.5s")
agent = ErrorRecoveryAgent(failure_threshold=3)
start = time.time()
for _ in range(10):
    try: agent.retry(lambda: (_ for _ in ()).throw(TimeoutError()), 3, 0.1)
    except (TimeoutError, CircuitOpenError): pass
elapsed = time.time() - start
result = elapsed < 0.5
print(f"   Time: {elapsed:.4f}s (expected: <0.5s)")
print(f"   Status: {'✓ PASS' if result else '✗ FAIL'}")
all_pass = all_pass and result

# 7. 90%+ waste eliminated
print("\n7. 90%+ waste eliminated")
# V0.2 would have done 30 attempts (10 calls * 3 retries)
# V0.3 does 3 attempts (circuit opens after 3)
agent = ErrorRecoveryAgent(failure_threshold=3)
total = 0
for _ in range(10):
    count = [0]
    def op(): count[0] += 1; raise TimeoutError()
    try: agent.retry(op, 3, 0.001)
    except (TimeoutError, CircuitOpenError): pass
    total += count[0]
expected_v02 = 30
actual_v03 = total
reduction = (expected_v02 - actual_v03) / expected_v02 * 100
result = reduction >= 90
print(f"   V0.2 would do: 30 attempts")
print(f"   V0.3 did: {actual_v03} attempts")
print(f"   Reduction: {reduction:.0f}%")
print(f"   Status: {'✓ PASS' if result else '✗ FAIL'}")
all_pass = all_pass and result

# 8. All V0.2 tests still pass
print("\n8. All V0.2-compatible tests still pass")
v = ErrorRecoveryAgent().verify()
v02_tests = ["succeeds first try", "retry succeeds", "exhausts retries", "permanent no retry",
             "rejects max_retries=0", "rejects delay=-1", "unknown no retry"]
v02_pass = all(d["status"] == "PASS" for d in v["details"] if any(t in d["test"] for t in v02_tests))
print(f"   V0.2 tests: {'✓ PASS' if v02_pass else '✗ FAIL'}")
all_pass = all_pass and v02_pass

# 9. New circuit tests pass
print("\n9. New circuit breaker tests pass")
circuit_tests = ["circuit opens", "circuit blocks", "success resets", "permanent no circuit", "manual reset"]
circuit_pass = all(d["status"] == "PASS" for d in v["details"] if any(t in d["test"] for t in circuit_tests))
print(f"   Circuit tests: {'✓ PASS' if circuit_pass else '✗ FAIL'}")
all_pass = all_pass and circuit_pass

# 10. LOC <= 135
print("\n10. LOC ≤ 135")
result = subprocess.run(["wc", "-l", "error_recovery_agent_v03.py"], capture_output=True, text=True)
loc = int(result.stdout.split()[0])
loc_pass = loc <= 135
print(f"   Lines: {loc} (limit: 135, target: 130)")
print(f"   Status: {'✓ PASS' if loc_pass else '✗ FAIL'}")
all_pass = all_pass and loc_pass

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"All criteria met: {'✓ YES' if all_pass else '✗ NO'}")
