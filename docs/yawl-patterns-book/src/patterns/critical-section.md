# Critical Section

> **Therefore**: Ensure only one instance executes critical section at a time.

---

## Context
You have multiple instances that need to access a shared resource, but only one instance should access it at a time.

## Problem
**How do you ensure only one instance accesses a resource at a time?**

Multiple instance patterns create concurrent instances. Critical section serializes access.

## Solution
Define a critical section that only one instance can execute at a time, serializing access to shared resources.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Critical section: serialized access
model = parse_powl_model_string("""
    sequence(
        'Create Multiple Instances',
        'Acquire Lock',
        'Critical Section',
        'Release Lock'
    )
""")
```

## Example
**Database Update from Multiple Instances**:
1. Multiple instances process data
2. Each instance needs to update database
3. Only one instance can update at a time (critical section)
4. Instances take turns

```python
database_model = parse_powl_model_string("""
    sequence(
        'Create Processing Instances',
        'For Each Instance:',
        sequence(
            'Acquire Database Lock',
            'Update Database',
            'Release Lock'
        )
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Shared resource access
- Mutual exclusion needed
- Prevent race conditions

❌ Don't use when:
- No shared resources
- Concurrent access safe
- No conflicts

## Related Patterns
- [Without Synchronization](./without-synchronization.md) - No sync
- [Thread Join](./thread-join.md) - Synchronize threads
- [Arbitrary Cycles](./arbitrary-cycles.md) - Loop patterns

## Implementation Notes

### POWL v2
- Lock mechanism required
- Critical section protected
- External coordination

### BPMN 2.0
- **Exclusive Gateway** with lock
- **Message Event** for lock acquisition
- Serialize access

### Petri Nets
- **Mutex place** for lock
- Token represents lock
- Serialized execution

### YAWL
- **Mutex** or lock
- **Critical section** task
- Serialize access

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | Mutual exclusion |
| **Efficiency** | ⚠️ Medium | Serial bottleneck |
| **Maintainability** | ✅ High | Clear semantics |
| **Flexibility** | ✅ High | Easy to add |
| **Scalability** | ⚠️ Low | Serial bottleneck |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_critical_section():
    # Critical section with lock
    acquire = POWL("Acquire Database Lock")
    update = POWL("Update Database")
    release = POWL("Release Lock")

    # Sequence: lock → critical section → unlock
    critical_section = Operator.make_sequence(acquire, update, release)

    return critical_section

# Visualize
model = create_critical_section()
pm4py.view_powl(model, format='png')

# Note: Requires external lock mechanism
```

## Real-World Examples

1. **Database Updates**: Serialize database writes
2. **File Access**: Serialize file writes
3. **Resource Allocation**: Serialize resource access

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #40 of 43**
