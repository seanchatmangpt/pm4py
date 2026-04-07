# Arbitrary Interleaving

> **Therefore**: Execute multiple activities in any order without constraints.

---

## Context
You have a set of activities that need to be executed, but there are absolutely no constraints on the order—they can execute in any sequence, even interleaved.

## Problem
**How do you execute multiple activities with complete flexibility in ordering?**

Interleaved parallel routing (Pattern 13) allows concurrent execution. Arbitrary interleaving goes further—activities can execute in any order, even sequentially, with full flexibility.

## Solution
Execute multiple activities where the order is completely unspecified—any interleaving is valid, including sequential execution.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Arbitrary interleaving: complete order flexibility
model = parse_powl_model_string("""
    operator_sequence(
        operator_parallel('A', 'B', 'C')
    )
""")

# Valid executions: A→B→C, B→A→C, A→C→B, C→B→A, etc.
# Even: A→B→A→C→B (with iterations)
```

## Example
**Document Signing**: Three people need to sign a document:
1. Manager signs
2. HR signs
3. Legal signs

Order doesn't matter at all—any sequence is valid.

```python
signing_model = parse_powl_model_string("""
    sequence(
        'Prepare Document',
        operator_parallel(
            'Manager Sign',
            'HR Sign',
            'Legal Sign'
        ),
        'File Document'
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Complete order flexibility is required
- No dependencies between activities
- Any execution order is valid

❌ Don't use when:
- Some order constraints exist (use Sequence)
- Activities must execute concurrently (use Parallel Split)
- Order matters for correctness

## Related Patterns
- [Interleaved Parallel Routing](./interleaved-parallel-routing.md) - Concurrent with order flexibility
- [Parallel Split](./parallel-split.md) - True simultaneous execution
- [Sequence](./sequence.md) - Fixed order

## Implementation Notes

### POWL v2
- Use `operator_parallel()` for maximum flexibility
- No order constraints between branches
- All branches must complete before parent completes

### BPMN 2.0
- Use **Parallel Gateway** with no conditions
- All activities enabled simultaneously
- Order of execution completely unspecified

### Petri Nets
- **Place** with multiple output transitions
- All transitions enabled
- Any firing sequence is valid

### YAWL
- Use **AND-split** with all tasks enabled
- No order constraints
- Complete flexibility

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | No deadlock if activities independent |
| **Efficiency** | ✅ Excellent | Maximum flexibility |
| **Maintainability** | ✅ High | Clear independence |
| **Flexibility** | ✅ Excellent | Complete order freedom |
| **Scalability** | ✅ High | Many activities handled efficiently |

## Common Pitfalls

1. **Hidden Dependencies**: Activities assumed independent but aren't
2. **Resource Contention**: Activities compete for same resources
3. **Order Assumptions**: Downstream code assumes specific order

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_arbitrary_interleaving():
    # Create independent activities
    manager = POWL("Manager Sign")
    hr = POWL("HR Sign")
    legal = POWL("Legal Sign")
    file_doc = POWL("File Document")

    # Create arbitrary interleaving
    parallel = Operator(Operator.PARALLEL)
    parallel.add_child(manager)
    parallel.add_child(hr)
    parallel.add_child(legal)

    # Main sequence
    main = Operator(Operator.SEQUENCE)
    main.add_child(POWL("Prepare Document"))
    main.add_child(parallel)
    main.add_child(file_doc)

    return main

# Visualize
model = create_arbitrary_interleaving()
pm4py.view_powl(model, format='png')

# Note: Any order of signing is valid
# Could be: Manager → HR → Legal, or Legal → Manager → HR, etc.
```

## Verification Checklist

- [ ] Activities are truly independent
- [ ] No shared state between activities
- [ ] Any execution order produces correct result
- [ ] Resource conflicts are resolved

## Real-World Examples

1. **Data Collection**: Collect data from multiple sources (any order)
2. **Notifications**: Send notifications to multiple recipients (any order)
3. **Validation**: Run multiple validation rules (any order)

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #16 of 43**
