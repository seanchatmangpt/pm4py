# Thread Merge

> **Therefore**: Merge multiple threads into single thread of execution.

---

## Context
You have multiple concurrent threads that need to merge back into a single thread.

## Problem
**How do you merge multiple concurrent threads into one?**

Synchronization (Pattern 4) merges concurrent paths. Thread merge specifically merges threads.

## Solution
Merge multiple concurrent threads into a single thread, synchronizing their completion.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Thread merge: merge threads
model = parse_powl_model_string("""
    sequence(
        operator_parallel(
            'Thread 1',
            'Thread 2',
            'Thread 3'
        ),
        'Merged Thread'
    )
""")
```

## Example
**Multi-Threaded Order Processing**:
1. Thread 1: Process payment
2. Thread 2: Update inventory
3. Thread 3: Send confirmation
4. Merge: All threads complete → single thread continues

```python
thread_model = parse_powl_model_string("""
    sequence(
        operator_parallel(
            'Thread 1: Process Payment',
            'Thread 2: Update Inventory',
            'Thread 3: Send Confirmation'
        ),
        'Merged: Complete Order'
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Multiple threads need to merge
- Synchronization after parallel work
- Single thread continuation

❌ Don't use when:
- Threads continue independently
- No merging needed
- Implicit termination sufficient

## Related Patterns
- [Thread Split](./thread-split.md) - Create threads
- [Thread Join](./thread-join.md) - Synchronize threads
- [Synchronization](./synchronization.md) - Merge concurrent paths

## Implementation Notes

### POWL v2
- Parallel operator ends → merge
- All threads complete before merge
- Single thread continues

### BPMN 2.0
- **Parallel Gateway** merge
- All tokens arrive → single token
- Synchronized merge

### Petri Nets
- **Transition** waits for all tokens
- Tokens from threads consumed
- Single output token

### YAWL
- **AND-join** merges threads
- All threads complete
- Single continuation

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | Clear merge semantics |
| **Efficiency** | ✅ High | Clean merge |
| **Maintainability** | ✅ High | Clear synchronization |
| **Flexibility** | ✅ High | Easy to add threads |
| **Scalability** | ✅ High | Many threads |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_thread_merge():
    # Create threads
    thread1 = POWL("Thread 1: Process Payment")
    thread2 = POWL("Thread 2: Update Inventory")
    thread3 = POWL("Thread 3: Send Confirmation")
    merged = POWL("Merged: Complete Order")

    # Parallel threads
    parallel = Operator(Operator.PARALLEL)
    parallel.add_child(thread1)
    parallel.add_child(thread2)
    parallel.add_child(thread3)

    # Sequence: parallel → merge
    main = Operator(Operator.SEQUENCE)
    main.add_child(parallel)
    main.add_child(merged)

    return main

# Visualize
model = create_thread_merge()
pm4py.view_powl(model, format='png')
```

## Real-World Examples

1. **MapReduce**: Map threads merge into reduce
2. **Fork-Join**: Fork threads merge at join
3. **Parallel Processing**: Workers merge results

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #27 of 43**
