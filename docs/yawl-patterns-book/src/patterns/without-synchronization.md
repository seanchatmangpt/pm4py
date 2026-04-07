# Without Synchronization

> **Therefore**: Execute multiple instances without waiting for all to complete.

---

## Context
You need to create multiple instances of an activity, but you don't need to wait for all instances to complete before proceeding.

## Problem
**How do you execute multiple instances without synchronization?**

Multiple instance patterns create multiple copies. Without synchronization proceeds independently.

## Solution
Create multiple instances of an activity that execute concurrently without synchronization—proceed without waiting for all instances.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Without synchronization: multiple instances, no sync
model = parse_powl_model_string("""
    sequence(
        'Create Multiple Instances',
        operator_parallel(
            'Instance 1',
            'Instance 2',
            'Instance 3'
        ),
        'Continue'  # Doesn't wait for all instances
    )
""")
```

## Example
**Bulk Notification**:
1. Send notifications to 1000 recipients
2. Each notification is independent instance
3. Process continues without waiting for all notifications

```python
notification_model = parse_powl_model_string("""
    sequence(
        'Send Notifications to 1000 Recipients',
        'Continue Process'  # Doesn't wait for all 1000
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Fire-and-forget semantics
- No need to wait for completion
- Independent instances

❌ Don't use when:
- Synchronization needed (use with synchronization)
- Results needed from all instances
- Coordination required

## Related Patterns
- [A-Priori Design Time](./a-priori-design-time.md) - Known instances
- [Without A-Priori Runtime](./without-a-priori-runtime.md) - Unknown instances
- [Multi-Merge](./multi-merge.md) - No synchronization

## Implementation Notes

### POWL v2
- Multiple instances created
- No synchronization point
- Proceed independently

### BPMN 2.0
- **Multi-Instance Activity** with waitForCompletion=false
- Parallel instances
- No synchronization

### Petri Nets
- **Multiple tokens** for instances
- No synchronization transition
- Independent execution

### YAWL
- **Multi-instance** task
- No synchronization
- Independent instances

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | No synchronization needed |
| **Efficiency** | ✅ Excellent | No waiting |
| **Maintainability** | ✅ High | Clear semantics |
| **Flexibility** | ✅ High | Easy to implement |
| **Scalability** | ✅ Excellent | Many instances |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_without_synchronization():
    # Create instances (fire-and-forget)
    # Process continues immediately
    send = POWL("Send Notifications to 1000 Recipients")
    continue_process = POWL("Continue Process")

    # Sequence: no waiting for notifications
    model = Operator.make_sequence(send, continue_process)

    return model

# Visualize
model = create_without_synchronization()
pm4py.view_powl(model, format='png')

# Note: Instances execute independently, no synchronization
```

## Real-World Examples

1. **Bulk Email**: Send emails, continue without waiting
2. **Logging**: Log events asynchronously
3. **Metrics**: Collect metrics without blocking

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #36 of 43**
