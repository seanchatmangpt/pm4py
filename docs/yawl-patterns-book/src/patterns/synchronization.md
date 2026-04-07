# Synchronization

> **Therefore**: Wait for all concurrent paths to complete before proceeding.

---

## Context
You have a process that splits into multiple concurrent activities that must all complete before the process can move forward.

## Problem
**How do you ensure all parallel branches complete before proceeding?**

When activities execute in parallel, you often need to wait for all of them to finish before continuing. Without proper synchronization, the process may proceed prematurely with incomplete data or missed side effects.

## Solution
Join multiple concurrent paths into a single flow, waiting for **all** incoming branches to complete before enabling the outgoing transition.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Parallel split with synchronization
model = parse_powl_model_string("""
    operator_parallel(
        sequence('A', 'C'),
        sequence('B', 'C')
    )
""")

# All paths (A→C and B→C) must complete before proceeding past C
```

## Example
**Loan Approval Process**: A loan application requires three parallel checks:
1. Credit verification (A)
2. Employment verification (B)
3. Property appraisal (C)

All three checks must complete before the underwriting decision (D) can be made.

```python
loan_model = parse_powl_model_string("""
    operator_parallel(
        sequence('Credit Check', 'Underwriting Decision'),
        sequence('Employment Check', 'Underwriting Decision'),
        sequence('Property Appraisal', 'Underwriting Decision')
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Multiple independent tasks must all complete before proceeding
- Results from all branches are needed for subsequent decisions
- You need to ensure data completeness before moving forward

❌ Don't use when:
- Only some branches need to complete (use Multi-Merge or Discriminator)
- Branches have different priorities (use Structured Loop with conditions)
- You need to proceed as soon as any branch completes (use Simple Merge)

## Related Patterns
- [Parallel Split](./parallel-split.md) - Creates the concurrent paths
- [Simple Merge](./simple-merge.md) - Waits for only one branch
- [Multi-Merge](./multi-merge.md) - Joins without synchronizing
- [Discriminator](./discriminator.md) - Waits for n of m branches

## Implementation Notes

### POWL v2
- Use `operator_parallel()` to create parallel structure
- All children of parallel operator must complete before parent completes
- Natural synchronization semantics built into POWL parallel operator

### BPMN 2.0
- Use **Parallel Gateway** (diamond with plus icon)
- Split: One incoming → multiple outgoing
- Join: Multiple incoming → one outgoing
- All incoming tokens required to trigger outgoing flow

### Petri Nets
- **Place** after join transition waits for all tokens
- Transition fires only when all input places have tokens
- Ensures all branches have completed

### YAWL
- Use **AND-split** for parallel divergence
- Use **AND-join** for synchronization
- Explicit join condition: all branches must complete

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | No deadlocks if all branches are reachable |
| **Efficiency** | ⚠️ Potential Bottleneck | Slowest branch determines overall time |
| **Maintainability** | ✅ High | Clear visual representation |
| **Flexibility** | ⚠️ Medium | Fixed number of branches required |
| **Scalability** | ⚠️ Medium | Many branches may cause performance issues |

## Common Pitfalls

1. **Unbalanced Branches**: If one branch takes significantly longer, it blocks the entire process
2. **Missing Branches**: If a branch can be skipped, use Discriminator instead
3. **Data Dependencies**: Ensure downstream activities can handle incomplete data if branches fail

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

# Create synchronization pattern programmatically
def create_synchronization():
    # Create activities
    a = POWL("Credit Check")
    b = POWL("Employment Check")
    c = POWL("Property Appraisal")
    d = POWL("Underwriting Decision")

    # Create parallel structure with synchronization
    parallel = Operator(Operator.PARALLEL)
    parallel.add_child(Operator.make_sequence(a, d))
    parallel.add_child(Operator.make_sequence(b, d))
    parallel.add_child(Operator.make_sequence(c, d))

    return parallel

# Visualize
model = create_synchronization()
pm4py.view_powl(model, format='png')
```

## References
- van der Aalst, W. M. P., ter Hofstede, A. H. M., Kiepuszewski, B., & Barros, A. P. (2003). "Workflow Patterns". *Distributed and Parallel Databases*, 14(3), 5-51.
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #4 of 43**
