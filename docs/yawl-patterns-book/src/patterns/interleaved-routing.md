# Interleaved Routing

> **Therefore**: Route activities through multiple paths in any order.

---

## Context
You have multiple activities that need to be routed through different paths, but the order of routing is flexible.

## Problem
**How do you route activities through multiple paths with flexible ordering?**

Interleaved parallel routing (Pattern 13) executes activities concurrently. Interleaved routing focuses on the routing logic itself.

## Solution
Route activities through multiple paths where the order of routing is unspecified—activities can be routed in any sequence.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Interleaved routing: flexible order
model = parse_powl_model_string("""
    operator_parallel(
        'Path A',
        'Path B',
        'Path C'
    )
""")
```

## Example
**Document Approval Routing**: Document routes through multiple departments in any order:
1. HR approval
2. Finance approval
3. Legal approval

Order doesn't matter—all must approve.

```python
approval_model = parse_powl_model_string("""
    sequence(
        'Submit Document',
        operator_parallel(
            'HR Approval',
            'Finance Approval',
            'Legal Approval'
        ),
        'Final Approval'
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Routing order is flexible
- Multiple paths can be taken
- No strict routing sequence

❌ Don't use when:
- Routing order matters (use Sequence)
- Single path (use Exclusive Choice)
- Strict routing rules (use Conditional Routing)

## Related Patterns
- [Interleaved Parallel Routing](./interleaved-parallel-routing.md) - Concurrent execution
- [Arbitrary Interleaving](./arbitrary-interleaving.md) - Complete flexibility
- [Multi-Choice](./multi-choice.md) - Conditional routing

## Implementation Notes

### POWL v2
- Parallel operator for flexible routing
- No order constraints
- All routes must complete

### BPMN 2.0
- **Parallel Gateway** for routing
- Multiple outgoing paths
- Order unspecified

### Petri Nets
- **Place** with multiple output transitions
- All transitions enabled
- Any firing order valid

### YAWL
- **AND-split** for routing
- All paths enabled
- Flexible order

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | No routing conflicts |
| **Efficiency** | ✅ High | Flexible routing |
| **Maintainability** | ✅ High | Clear routing logic |
| **Flexibility** | ✅ High | Easy to modify routes |
| **Scalability** | ✅ High | Many routes |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_interleaved_routing():
    # Create parallel routing
    parallel = Operator(Operator.PARALLEL)
    parallel.add_child(POWL("HR Approval"))
    parallel.add_child(POWL("Finance Approval"))
    parallel.add_child(POWL("Legal Approval"))

    # Main sequence
    main = Operator(Operator.SEQUENCE)
    main.add_child(POWL("Submit Document"))
    main.add_child(parallel)
    main.add_child(POWL("Final Approval"))

    return main

# Visualize
model = create_interleaved_routing()
pm4py.view_powl(model, format='png')
```

## Real-World Examples

1. **Approval Workflow**: Multiple approvers in any order
2. **Data Validation**: Multiple validation checks
3. **Quality Control**: Multiple QC steps

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #22 of 43**
