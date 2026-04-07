# Thread Split

> **Therefore**: Split process into multiple concurrent threads of execution.

---

## Context
You need to split a process into multiple independent threads that execute concurrently.

## Problem
**How do you create multiple concurrent threads of execution?**

Parallel split (Pattern 3) splits into concurrent activities. Thread split creates independent threads.

## Solution
Split process into multiple independent threads that execute concurrently, each with its own state.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Thread split: concurrent threads
model = parse_powl_model_string("""
    operator_parallel(
        'Thread 1',
        'Thread 2',
        'Thread 3'
    )
""")
```

## Example
**Multi-Threaded Processing**:
1. Main process starts
2. Thread 1: Process data
3. Thread 2: Send notifications
4. Thread 3: Update analytics

```python
thread_model = parse_powl_model_string("""
    sequence(
        'Start Process',
        operator_parallel(
            'Thread 1: Process Data',
            'Thread 2: Send Notifications',
            'Thread 3: Update Analytics'
        ),
        'Join Threads'
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Independent concurrent execution
- Separate threads with own state
- Parallel processing needed

❌ Don't use when:
- Shared state between threads (use synchronization)
- Sequential execution sufficient
- No concurrency needed

## Related Patterns
- [Parallel Split](./parallel-split.md) - Concurrent activities
- [Thread Merge](./thread-merge.md) - Merge threads
- [Thread Join](./thread-join.md) - Synchronize threads

## Implementation Notes

### POWL v2
- Parallel operator creates threads
- Each thread independent
- State isolated per thread

### BPMN 2.0
- **Parallel Gateway** splits into threads
- **Token** per thread
- Independent execution

### Petri Nets
- **Transition** creates multiple tokens
- Each token represents thread
- Independent places

### YAWL
- **AND-split** creates threads
- Each thread independent
- Separate execution contexts

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | Isolated threads |
| **Efficiency** | ✅ High | True parallelism |
| **Maintainability** | ⚠️ Medium | Thread complexity |
| **Flexibility** | ✅ High | Easy to add threads |
| **Scalability** | ✅ High | Many threads |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_thread_split():
    # Create threads
    thread1 = POWL("Thread 1: Process Data")
    thread2 = POWL("Thread 2: Send Notifications")
    thread3 = POWL("Thread 3: Update Analytics")
    join = POWL("Join Threads")

    # Parallel threads
    parallel = Operator(Operator.PARALLEL)
    parallel.add_child(thread1)
    parallel.add_child(thread2)
    parallel.add_child(thread3)

    # Main sequence
    main = Operator(Operator.SEQUENCE)
    main.add_child(POWL("Start Process"))
    main.add_child(parallel)
    main.add_child(join)

    return main

# Visualize
model = create_thread_split()
pm4py.view_powl(model, format='png')
```

## Real-World Examples

1. **Web Server**: Handle multiple requests concurrently
2. **Data Processing**: Process multiple data streams
3. **Background Tasks**: Run multiple background jobs

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #26 of 43**
