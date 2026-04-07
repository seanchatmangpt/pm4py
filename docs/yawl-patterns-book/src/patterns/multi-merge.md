# Multi-Merge

> **Therefore**: Merge multiple concurrent paths without waiting for synchronization.

---

## Context
You have multiple concurrent paths that need to rejoin, but you don't need to wait for all of them—proceed as soon as any one path completes.

## Problem
**How do you merge concurrent paths without synchronization?**

Synchronization (Pattern 4) waits for ALL paths, which may be unnecessary. Multi-merge allows the process to continue as soon as ANY path completes, potentially executing the merge activity multiple times (once per incoming path).

## Solution
Merge multiple paths without synchronization—proceed immediately when any path arrives, executing the merge activity for each incoming path separately.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Multi-merge: each path triggers merge independently
model = parse_powl_model_string("""
    sequence(
        operator_parallel(
            'A',
            'B',
            'C'
        ),
        'D'  # D executes THREE times (once per incoming path)
    )
""")

# A completes → D executes
# B completes → D executes again
# C completes → D executes again
```

## Example
**Email Notification System**: Multiple events can trigger email notifications:
1. Order shipped
2. Payment received
3. Item returned

Each event should trigger an independent email:

```python
email_model = parse_powl_model_string("""
    sequence(
        operator_parallel(
            'Order Shipped',
            'Payment Received',
            'Item Returned'
        ),
        'Send Email Notification'  # Executes 3 times
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Each incoming path should independently trigger the merge activity
- No synchronization needed between paths
- Merge activity is idempotent (safe to run multiple times)

❌ Don't use when:
- You need to wait for all paths (use Synchronization)
- Merge activity should execute only once (use Synchronizing Merge)
- Paths share resources that could conflict

## Related Patterns
- [Synchronization](./synchronization.md) - Waits for all paths
- [Simple Merge](./simple-merge.md) - Merges alternative (not concurrent) paths
- [Discriminator](./discriminator.md) - Waits for first path, then ignores others
- [Synchronizing Merge](./synchronizing-merge.md) - Waits for activated paths

## Implementation Notes

### POWL v2
- Multi-merge is **implicit** when parallel operator's children converge
- Each child of parallel operator independently triggers subsequent activities
- No explicit multi-merge construct needed

### BPMN 2.0
- Use **Parallel Gateway** split + **Event-Based Gateway** merge
- Or use multiple **Message Events** triggered independently
- No native multi-merge—requires event-driven architecture

### Petri Nets
- **Transition** with multiple input places
- Fires **for each token** in any input place
- No accumulation—each token triggers transition independently

### YAWL
- Use **AND-split** for divergence
- Use **OR-join** with "multi-instance" semantics
- Each incoming branch triggers join independently

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ⚠️ Requires Care | Risk of race conditions |
| **Efficiency** | ✅ Excellent | No waiting for other paths |
| **Maintainability** | ⚠️ Medium | Can be confusing—merge executes multiple times |
| **Flexibility** | ✅ High | Easy to add/remove paths |
| **Scalability** | ✅ High | Many paths handled efficiently |

## Common Pitfalls

1. **Unexpected Multiple Executions**: Merge activity runs N times (once per path)
2. **Race Conditions**: Multiple paths accessing shared resources
3. **Order Dependence**: Results may vary based on which path completes first

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_multi_merge():
    # Create parallel activities
    shipped = POWL("Order Shipped")
    payment = POWL("Payment Received")
    returned = POWL("Item Returned")
    send_email = POWL("Send Email Notification")

    # Create parallel split
    parallel = Operator(Operator.PARALLEL)
    parallel.add_child(shipped)
    parallel.add_child(payment)
    parallel.add_child(returned)

    # Create sequence: parallel → multi-merge
    sequence = Operator(Operator.SEQUENCE)
    sequence.add_child(parallel)
    sequence.add_child(send_email)

    return sequence

# Visualize
model = create_multi_merge()
pm4py.view_powl(model, format='png')

# Note: send_email will execute 3 times (once per parallel branch)
```

## Verification Checklist

- [ ] Merge activity is idempotent (safe to run multiple times)
- [ ] No shared state between parallel paths
- [ ] Order of execution doesn't matter
- [ ] Resource conflicts are handled (e.g., database locks)

## Real-World Examples

1. **Sensor Network**: Multiple sensors trigger alerts independently
2. **User Actions**: Click, scroll, type all trigger analytics events
3. **Microservices**: Multiple services write to same log independently

## References
- van der Aalst, W. M. P., ter Hofstede, A. H. M., Kiepuszewski, B., & Barros, A. P. (2003). "Workflow Patterns". *Distributed and Parallel Databases*, 14(3), 5-51.
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #8 of 43**
