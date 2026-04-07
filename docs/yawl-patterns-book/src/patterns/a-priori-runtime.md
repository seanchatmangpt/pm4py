# A-Priori Runtime

> **Therefore**: Create known number of instances at runtime.

---

## Context
You need to create a specific number of instances of an activity, with the number known when the process starts (at runtime).

## Problem
**How do you create a known number of instances at runtime?**

A-priori design time (Pattern 37) knows number at design time. A-priori runtime knows at runtime.

## Solution
Create a fixed number of instances of an activity, with the number determined when the process instance starts (at runtime).

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# A-priori runtime: known at runtime
model = parse_powl_model_string("""
    sequence(
        'Determine Instance Count (Runtime)',
        'Create N Instances'
    )
""")
```

## Example
**Document Review by N Reviewers**:
1. Document submitted
2. Determine number of reviewers (N) based on document type
3. Create N reviewer instances
4. All N reviews complete

```python
review_model = parse_powl_model_string("""
    sequence(
        'Submit Document',
        'Determine Reviewer Count (N)',
        'Create N Reviewer Instances',
        'Collect All Reviews'
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Number of instances known at runtime
- Dynamic but fixed number
- Runtime determination

❌ Don't use when:
- Number known at design time (use a-priori design time)
- Unknown number (use without a-priori runtime)
- Single instance

## Related Patterns
- [A-Priori Design Time](./a-priori-design-time.md) - Known at design time
- [Without A-Priori Runtime](./without-a-priori-runtime.md) - Unknown instances
- [Design Time Plus Runtime](./design-time-plus-runtime.md) - Combination

## Implementation Notes

### POWL v2
- Runtime determination
- Fixed number after determination
- External instance creation

### BPMN 2.0
- **Multi-Instance Activity** with runtime cardinality
- Collection size determines instances
- Known at runtime

### Petri Nets
- **Runtime parameter** for instance count
- Fixed after determination
- Dynamic structure

### YAWL
- **Multi-instance** with runtime cardinality
- Data-driven instance count
- Known at runtime

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | Known at runtime |
| **Efficiency** | ✅ High | Parallel execution |
| **Maintainability** | ✅ High | Clear semantics |
| **Flexibility** | ✅ High | Runtime determination |
| **Scalability** | ✅ High | Adapts to data |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_a_priori_runtime():
    # Determine instance count at runtime
    determine = POWL("Determine Reviewer Count (N)")
    create = POWL("Create N Reviewer Instances")
    collect = POWL("Collect All Reviews")

    # Sequence: runtime determination
    model = Operator.make_sequence(determine, create, collect)

    return model

# Visualize
model = create_a_priori_runtime()
pm4py.view_powl(model, format='png')

# Note: Instance count determined at runtime
# Implementation: external logic creates N instances
```

## Real-World Examples

1. **Document Review**: N reviewers based on document type
2. **Vendor Quotes**: N vendors based on product category
3. **Validation Checks**: N validations based on data sensitivity

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #38 of 43**
