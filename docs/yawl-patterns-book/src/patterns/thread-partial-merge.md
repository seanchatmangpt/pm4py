# Thread Partial Merge

> **Therefore**: Merge some threads while others continue.

---

## Context
You have multiple concurrent threads, but only some need to merge at a specific point—others continue independently.

## Problem
**How do you merge only some threads while others continue?**

Thread merge (Pattern 27) merges all threads. Thread partial merge merges only some.

## Solution
Merge a subset of concurrent threads at a specific point, while other threads continue executing.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Thread partial merge: merge some threads
model = parse_powl_model_string("""
    sequence(
        operator_parallel(
            sequence('Thread 1', 'Partial Merge'),
            sequence('Thread 2', 'Partial Merge'),
            'Thread 3'  # Continues independently
        ),
        'After Merge'
    )
""")
```

## Example
**Order Processing Threads**:
1. Thread 1: Payment (merges)
2. Thread 2: Inventory (merges)
3. Thread 3: Shipping (continues)
4. Threads 1+2 merge → confirmation
5. Thread 3 continues independently

```python
thread_model = parse_powl_model_string("""
    sequence(
        operator_parallel(
            sequence('Thread 1: Payment', 'Partial Merge'),
            sequence('Thread 2: Inventory', 'Partial Merge'),
            'Thread 3: Shipping'
        ),
        'Confirmation'
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Only some threads need to merge
- Other threads continue
- Selective synchronization

❌ Don't use when:
- All threads merge (use Thread Merge)
- No merging needed (use Implicit Termination)
- All threads independent (use Thread Split)

## Related Patterns
- [Thread Split](./thread-split.md) - Create threads
- [Thread Merge](./thread-merge.md) - Merge all threads
- [Partial Join](./partial-join.md) - Merge some paths

## Implementation Notes

### POWL v2
- Nested parallel operators
- Some branches merge, others don't
- Complex structure

### BPMN 2.0
- **Parallel Gateway** split
- Some paths converge
- Others bypass

### Petri Nets
- **Partial merge transition**
- Some input places trigger
- Others remain active

### YAWL
- **Partial AND-join**
- Some threads join
- Others continue

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ⚠️ Requires Care | Complex verification |
| **Efficiency** | ✅ High | Selective merge |
| **Maintainability** | ⚠️ Medium | Complex structure |
| **Flexibility** | ✅ High | Selective merging |
| **Scalability** | ⚠️ Medium | Complexity grows |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_thread_partial_merge():
    # Thread 1 and 2 merge
    seq1 = Operator.make_sequence(
        POWL("Thread 1: Payment"),
        POWL("Partial Merge")
    )

    seq2 = Operator.make_sequence(
        POWL("Thread 2: Inventory"),
        POWL("Partial Merge")
    )

    # Thread 3 continues
    thread3 = POWL("Thread 3: Shipping")

    # Parallel: threads 1+2 merge, thread3 continues
    parallel = Operator(Operator.PARALLEL)
    parallel.add_child(seq1)
    parallel.add_child(seq2)
    parallel.add_child(thread3)

    # Main sequence
    main = Operator(Operator.SEQUENCE)
    main.add_child(parallel)
    main.add_child(POWL("Confirmation"))

    return main

# Visualize
model = create_thread_partial_merge()
pm4py.view_powl(model, format='png')
```

## Real-World Examples

1. **Microservices**: Some services sync, others continue
2. **Data Pipeline**: Some streams merge, others independent
3. **Multi-Phase Process**: Partial sync at milestones

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #28 of 43**
