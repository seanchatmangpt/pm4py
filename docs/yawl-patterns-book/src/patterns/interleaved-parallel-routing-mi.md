# Interleaved Parallel Routing MI

> **Therefore**: Route multiple instances through paths in any order.

---

## Context
You have multiple instances that need to be routed through different paths, with flexible ordering.

## Problem
**How do you route multiple instances through multiple paths with flexible ordering?**

Interleaved parallel routing (Pattern 13) routes single instance. Interleaved parallel routing MI routes multiple instances.

## Solution
Route multiple instances through multiple paths where the order of routing is completely flexible.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Interleaved parallel routing MI: multiple instances
model = parse_powl_model_string("""
    sequence(
        'Create Multiple Instances',
        operator_parallel(
            'Path A',
            'Path B',
            'Path C'
        )
    )
""")
```

## Example
**Multi-Instance Document Processing**:
1. Create N document instances
2. Route each instance through different paths (validation, approval, notification)
3. Order of routing flexible

```python
processing_model = parse_powl_model_string("""
    sequence(
        'Create N Document Instances',
        operator_parallel(
            'Validation Path',
            'Approval Path',
            'Notification Path'
        )
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Multiple instances
- Flexible routing order
- No dependencies

❌ Don't use when:
- Single instance (use Interleaved Parallel Routing)
- Fixed routing order
- Routing dependencies

## Related Patterns
- [Interleaved Parallel Routing](./interleaved-parallel-routing.md) - Single instance
- [Arbitrary Interleaving](./arbitrary-interleaving.md) - Complete flexibility
- [Multi-Choice](./multi-choice.md) - Conditional routing

## Implementation Notes

### POWL v2
- Multiple instances
- Parallel paths
- Flexible order

### BPMN 2.0
- **Multi-Instance Activity** with parallel routing
- **Parallel Gateway** for routing
- Flexible order

### Petri Nets
- **Multiple tokens** for instances
- **Multiple output paths**
- Flexible routing

### YAWL
- **Multi-instance** with parallel routing
- Flexible order
- Independent paths

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | No routing conflicts |
| **Efficiency** | ✅ High | Maximum flexibility |
| **Maintainability** | ✅ High | Clear routing logic |
| **Flexibility** | ✅ Excellent | Complete flexibility |
| **Scalability** | ✅ High | Many instances |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_interleaved_parallel_routing_mi():
    # Create parallel routing paths
    parallel = Operator(Operator.PARALLEL)
    parallel.add_child(POWL("Validation Path"))
    parallel.add_child(POWL("Approval Path"))
    parallel.add_child(POWL("Notification Path"))

    # Main sequence
    main = Operator(Operator.SEQUENCE)
    main.add_child(POWL("Create N Document Instances"))
    main.add_child(parallel)

    return main

# Visualize
model = create_interleaved_parallel_routing_mi()
pm4py.view_powl(model, format='png')

# Note: Multiple instances routed through paths in any order
```

## Real-World Examples

1. **Multi-Instance Approval**: Multiple documents, flexible routing
2. **Batch Processing**: Multiple items, flexible processing
3. **Parallel Validation**: Multiple instances, flexible validation

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #41 of 43**
