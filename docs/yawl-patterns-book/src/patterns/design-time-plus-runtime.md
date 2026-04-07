# Design Time Plus Runtime

> **Therefore**: Combine design-time and runtime instance creation.

---

## Context
You need to create some instances known at design time and additional instances determined at runtime.

## Problem
**How do you combine design-time and runtime instance creation?**

A-priori design time (Pattern 37) knows all at design time. A-priori runtime (Pattern 38) knows all at runtime. Design time plus runtime combines both.

## Solution
Create some instances known at design time and additional instances determined at runtime, combining both approaches.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Design time plus runtime: combination
model = parse_powl_model_string("""
    sequence(
        'Create Design-Time Instances (Fixed)',
        'Determine Runtime Instances',
        'Create Runtime Instances (Dynamic)'
    )
""")
```

## Example
**Document Review with Fixed and Dynamic Reviewers**:
1. Always require 3 fixed reviewers (design time)
2. Additional reviewers based on document complexity (runtime)
3. Total = 3 + N

```python
review_model = parse_powl_model_string("""
    sequence(
        'Submit Document',
        operator_parallel(
            'Reviewer 1 (Fixed)',
            'Reviewer 2 (Fixed)',
            'Reviewer 3 (Fixed)'
        ),
        'Determine Additional Reviewers (N)',
        'Create N Additional Reviewers',
        'Collect All Reviews'
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Fixed + dynamic instances
- Hybrid approach
- Partial design-time knowledge

❌ Don't use when:
- All instances known at design time (use a-priori design time)
- All instances dynamic (use without a-priori runtime)
- Single instance

## Related Patterns
- [A-Priori Design Time](./a-priori-design-time.md) - All known at design time
- [A-Priori Runtime](./a-priori-runtime.md) - All known at runtime
- [Without A-Priori Runtime](./without-a-priori-runtime.md) - All dynamic

## Implementation Notes

### POWL v2
- Fixed instances at design time
- Dynamic instances at runtime
- Hybrid structure

### BPMN 2.0
- **Multi-Instance Activity** with base + dynamic
- Partial cardinality known
- Runtime additions

### Petri Nets
- **Fixed places** + dynamic places
- Hybrid structure
- Combined approach

### YAWL
- **Multi-instance** with base + dynamic
- Partial design-time knowledge
- Runtime extensions

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | Hybrid semantics |
| **Efficiency** | ✅ High | Optimized for fixed + dynamic |
| **Maintainability** | ⚠️ Medium | Hybrid complexity |
| **Flexibility** | ✅ High | Best of both |
| **Scalability** | ✅ High | Handles both cases |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_design_time_plus_runtime():
    # Fixed design-time reviewers
    parallel_fixed = Operator(Operator.PARALLEL)
    parallel_fixed.add_child(POWL("Reviewer 1 (Fixed)"))
    parallel_fixed.add_child(POWL("Reviewer 2 (Fixed)"))
    parallel_fixed.add_child(POWL("Reviewer 3 (Fixed)"))

    # Runtime determination
    determine = POWL("Determine Additional Reviewers (N)")
    create_runtime = POWL("Create N Additional Reviewers")
    collect = POWL("Collect All Reviews")

    # Main sequence
    main = Operator(Operator.SEQUENCE)
    main.add_child(POWL("Submit Document"))
    main.add_child(parallel_fixed)
    main.add_child(determine)
    main.add_child(create_runtime)
    main.add_child(collect)

    return main

# Visualize
model = create_design_time_plus_runtime()
pm4py.view_powl(model, format='png')

# Note: 3 fixed reviewers + N runtime reviewers
```

## Real-World Examples

1. **Peer Review**: Fixed reviewers + dynamic reviewers based on complexity
2. **Validation**: Fixed checks + dynamic checks based on data
3. **Approval**: Fixed approvers + dynamic approvers based on amount

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #42 of 43**
