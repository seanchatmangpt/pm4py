# Static Partial Join

> **Therefore**: Join some instances while others continue.

---

## Context
You have multiple instances executing, but only some need to join at a specific point.

## Problem
**How do you join only some instances while others continue?**

Partial join (Pattern 17) joins some paths. Static partial join joins some instances.

## Solution
Join a subset of multiple instances at a specific point, while other instances continue executing.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Static partial join: join some instances
model = parse_powl_model_string("""
    sequence(
        operator_parallel(
            sequence('Instance 1', 'Join Point'),
            sequence('Instance 2', 'Join Point'),
            'Instance 3'  # Continues independently
        ),
        'After Join'
    )
""")
```

## Example
**Multi-Instance Processing with Partial Join**:
1. Create 3 instances
2. Instances 1 and 2 join at checkpoint
3. Instance 3 continues independently
4. All complete eventually

```python
processing_model = parse_powl_model_string("""
    sequence(
        operator_parallel(
            sequence('Instance 1: Process A', 'Join Point'),
            sequence('Instance 2: Process B', 'Join Point'),
            'Instance 3: Process C (Independent)'
        ),
        'Continue'
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Some instances need synchronization
- Other instances independent
- Partial join required

❌ Don't use when:
- All instances join (use synchronization)
- No join needed (use without synchronization)
- Single instance

## Related Patterns
- [Partial Join](./partial-join.md) - Join some paths
- [Thread Partial Merge](./thread-partial-merge.md) - Merge some threads
- [Dynamic Partial Join](./dynamic-partial-join.md) - Dynamic partial join

## Implementation Notes

### POWL v2
- Nested parallel operators
- Some instances join
- Others continue

### BPMN 2.0
- **Parallel Gateway** partial join
- Some instances converge
- Others bypass

### Petri Nets
- **Partial join transition**
- Some instances trigger join
- Others continue

### YAWL
- **Partial AND-join**
- Some instances join
- Others continue

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ⚠️ Requires Care | Complex verification |
| **Efficiency** | ✅ High | Selective join |
| **Maintainability** | ⚠️ Medium | Complex structure |
| **Flexibility** | ✅ High | Selective joining |
| **Scalability** | ⚠️ Medium | Complexity grows |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_static_partial_join():
    # Instances 1 and 2 join
    seq1 = Operator.make_sequence(
        POWL("Instance 1: Process A"),
        POWL("Join Point")
    )

    seq2 = Operator.make_sequence(
        POWL("Instance 2: Process B"),
        POWL("Join Point")
    )

    # Instance 3 continues independently
    instance3 = POWL("Instance 3: Process C (Independent)")

    # Parallel: instances 1+2 join, instance3 continues
    parallel = Operator(Operator.PARALLEL)
    parallel.add_child(seq1)
    parallel.add_child(seq2)
    parallel.add_child(instance3)

    # Main sequence
    main = Operator(Operator.SEQUENCE)
    main.add_child(parallel)
    main.add_child(POWL("Continue"))

    return main

# Visualize
model = create_static_partial_join()
pm4py.view_powl(model, format='png')

# Note: Instances 1 and 2 join, instance3 continues
```

## Real-World Examples

1. **Multi-Stage Processing**: Some instances sync at stages
2. **Phased Completion**: Partial sync points
3. **Independent Workers**: Some sync, others independent

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #43 of 43**
