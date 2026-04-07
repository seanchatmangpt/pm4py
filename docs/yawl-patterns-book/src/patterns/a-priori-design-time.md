# A-Priori Design Time

> **Therefore**: Create known number of instances at design time.

---

## Context
You need to create a specific number of instances of an activity, known at design time.

## Problem
**How do you create a known number of instances at design time?**

Multiple instance patterns create instances. A-priori design time knows the number at design time.

## Solution
Create a fixed number of instances of an activity, with the number known at design time.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# A-priori design time: known instances
model = parse_powl_model_string("""
    operator_parallel(
        'Instance 1',
        'Instance 2',
        'Instance 3',
        'Instance 4',
        'Instance 5'
    )
""")
```

## Example
**Document Review by 5 Reviewers**:
1. Document submitted
2. Create 5 instances (5 reviewers)
3. Each reviewer reviews independently
4. All 5 reviews complete

```python
review_model = parse_powl_model_string("""
    sequence(
        'Submit Document',
        operator_parallel(
            'Reviewer 1',
            'Reviewer 2',
            'Reviewer 3',
            'Reviewer 4',
            'Reviewer 5'
        ),
        'Collect All Reviews'
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Number of instances known at design time
- Fixed number of parallel executions
- Static instance count

❌ Don't use when:
- Number unknown at design time (use a-priori runtime)
- Dynamic instances (use without a-priori runtime)
- Single instance (use single activity)

## Related Patterns
- [A-Priori Runtime](./a-priori-runtime.md) - Known at runtime
- [Without A-Priori Runtime](./without-a-priori-runtime.md) - Unknown instances
- [Parallel Split](./parallel-split.md) - Concurrent activities

## Implementation Notes

### POWL v2
- Fixed number of parallel branches
- Known at design time
- All instances created together

### BPMN 2.0
- **Multi-Instance Activity** with fixed cardinality
- Sequential or parallel
- Known at design time

### Petri Nets
- **Fixed number** of tokens/places
- Known structure
- Static instances

### YAWL
- **Multi-instance** with cardinality
- Fixed number
- Design-time knowledge

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | Known instances |
| **Efficiency** | ✅ High | Parallel execution |
| **Maintainability** | ✅ High | Clear structure |
| **Flexibility** | ⚠️ Low | Fixed number |
| **Scalability** | ⚠️ Medium | Fixed limit |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_a_priori_design_time():
    # Create 5 reviewer instances
    parallel = Operator(Operator.PARALLEL)
    for i in range(1, 6):
        parallel.add_child(POWL(f"Reviewer {i}"))

    # Main sequence
    main = Operator(Operator.SEQUENCE)
    main.add_child(POWL("Submit Document"))
    main.add_child(parallel)
    main.add_child(POWL("Collect All Reviews"))

    return main

# Visualize
model = create_a_priori_design_time()
pm4py.view_powl(model, format='png')

# Note: 5 instances created at design time
```

## Real-World Examples

1. **Peer Review**: 3 reviewers for document
2. **Quote Comparison**: 5 vendors for quotes
3. **Data Validation**: 4 validation rules

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #37 of 43**
