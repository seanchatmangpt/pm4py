# Thread Join

> **Therefore**: Synchronize multiple threads at a specific point.

---

## Context
You have multiple concurrent threads that need to synchronize at a specific point, waiting for all to reach that point.

## Problem
**How do you synchronize multiple threads at a specific point?**

Thread merge (Pattern 27) merges threads. Thread join synchronizes threads at specific point.

## Solution
Synchronize multiple threads at a specific point, waiting for all threads to arrive before proceeding.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Thread join: synchronize threads
model = parse_powl_model_string("""
    sequence(
        operator_parallel(
            sequence('Thread 1', 'Join Point'),
            sequence('Thread 2', 'Join Point'),
            sequence('Thread 3', 'Join Point')
        ),
        'After Join'
    )
""")
```

## Example
**Multi-Threaded Data Processing**:
1. Thread 1: Process dataset A
2. Thread 2: Process dataset B
3. Thread 3: Process dataset C
4. Join point: All threads synchronize
5. Continue with aggregated results

```python
thread_model = parse_powl_model_string("""
    sequence(
        operator_parallel(
            sequence('Thread 1: Process A', 'Join Point'),
            sequence('Thread 2: Process B', 'Join Point'),
            sequence('Thread 3: Process C', 'Join Point')
        ),
        'Aggregate Results'
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Threads must synchronize
- Barrier synchronization needed
- All threads must reach point

❌ Don't use when:
- Threads independent (no sync needed)
- Partial synchronization (use Thread Partial Merge)
- No synchronization point

## Related Patterns
- [Thread Split](./thread-split.md) - Create threads
- [Thread Merge](./thread-merge.md) - Merge threads
- [Synchronization](./synchronization.md) - Synchronize paths

## Implementation Notes

### POWL v2
- Parallel operator with join point
- All threads reach join
- Synchronized continuation

### BPMN 2.0
- **Parallel Gateway** join
- All tokens arrive
- Barrier synchronization

### Petri Nets
- **Synchronization transition**
- All input places have tokens
- Fires when all arrive

### YAWL
- **AND-join** synchronization
- All threads arrive
- Barrier point

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | Clear synchronization |
| **Efficiency** | ⚠️ Medium | Waiting for slowest thread |
| **Maintainability** | ✅ High | Clear sync point |
| **Flexibility** | ✅ High | Easy to add threads |
| **Scalability** | ⚠️ Medium | Many threads = long wait |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_thread_join():
    # Create threads with join point
    seq1 = Operator.make_sequence(
        POWL("Thread 1: Process A"),
        POWL("Join Point")
    )

    seq2 = Operator.make_sequence(
        POWL("Thread 2: Process B"),
        POWL("Join Point")
    )

    seq3 = Operator.make_sequence(
        POWL("Thread 3: Process C"),
        POWL("Join Point")
    )

    # Parallel threads
    parallel = Operator(Operator.PARALLEL)
    parallel.add_child(seq1)
    parallel.add_child(seq2)
    parallel.add_child(seq3)

    # Main sequence
    main = Operator(Operator.SEQUENCE)
    main.add_child(parallel)
    main.add_child(POWL("Aggregate Results"))

    return main

# Visualize
model = create_thread_join()
pm4py.view_powl(model, format='png')
```

## Real-World Examples

1. **MapReduce**: Mappers synchronize before reduce
2. **Parallel Testing**: Tests sync before reporting
3. **Data Aggregation**: Workers sync before aggregation

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #29 of 43**
