# Partial Join

> **Therefore**: Merge only some of the concurrent paths, leaving others active.

---

## Context
You have multiple concurrent paths, but you only need to merge some of them at a specific point—leaving other paths to continue independently.

## Problem
**How do you merge only a subset of concurrent paths while others continue?**

Synchronization (Pattern 4) merges ALL paths. Partial join merges only specific paths, allowing others to continue running independently.

## Solution
Merge a subset of concurrent paths at a specific point, while other paths continue executing independently.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Partial join: merge A and B, leave C running
model = parse_powl_model_string("""
    sequence(
        operator_parallel(
            sequence('A', 'Partial Merge'),
            sequence('B', 'Partial Merge'),
            'C'  # Continues independently
        ),
        'After Merge'
    )
""")

# A and B merge at "Partial Merge"
# C continues independently
```

## Example
**Order Processing**: Multiple concurrent tasks:
1. Payment processing (A)
2. Inventory check (B)
3. Shipping preparation (C)

Payment and inventory merge for confirmation, but shipping continues independently.

```python
order_model = parse_powl_model_string("""
    sequence(
        operator_parallel(
            sequence('Payment', 'Confirm Payment'),
            sequence('Inventory', 'Confirm Payment'),
            'Shipping'  # Continues independently
        ),
        'Order Complete'
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Only some paths need to merge at specific point
- Other paths continue independently
- Selective synchronization needed

❌ Don't use when:
- All paths must merge (use Synchronization)
- No merging needed (use Implicit Termination)
- Paths are independent (use Multi-Merge)

## Related Patterns
- [Synchronization](./synchronization.md) - Merge all paths
- [Multi-Merge](./multi-merge.md) - No synchronization
- [Thread Partial Merge](./thread-partial-merge.md) - Thread-based partial join

## Implementation Notes

### POWL v2
- Nested parallel operators
- Some branches merge, others don't
- Requires careful structure design

### BPMN 2.0
- Use **Parallel Gateway** split
- Some paths converge at intermediate gateway
- Other paths bypass convergence

### Petri Nets
- **Partial join transition**
- Only some input places trigger join
- Other places remain active

### YAWL
- Use **AND-join** with subset of branches
- Explicit specification of which branches to join
- Other branches continue independently

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ⚠️ Requires Care | Complex to verify |
| **Efficiency** | ✅ High | Selective synchronization |
| **Maintainability** | ⚠️ Medium | Complex structure |
| **Flexibility** | ✅ High | Selective merging |
| **Scalability** | ⚠️ Medium | Complexity grows |

## Common Pitfalls

1. **Incomplete Join**: Forgetting to join some paths
2. **Deadlock**: Unjoined paths waiting for joined paths
3. **State Inconsistency**: Joined and unjoined paths sharing state

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_partial_join():
    # Create partial join: A and B merge, C continues
    seq_ab = Operator(Operator.SEQUENCE)
    seq_ab.add_child(POWL("Payment"))
    seq_ab.add_child(POWL("Confirm Payment"))

    seq_ab2 = Operator(Operator.SEQUENCE)
    seq_ab2.add_child(POWL("Inventory"))
    seq_ab2.add_child(POWL("Confirm Payment"))

    # Parallel: A+B merge, C independent
    parallel = Operator(Operator.PARALLEL)
    parallel.add_child(seq_ab)
    parallel.add_child(seq_ab2)
    parallel.add_child(POWL("Shipping"))

    # Main sequence
    main = Operator(Operator.SEQUENCE)
    main.add_child(parallel)
    main.add_child(POWL("Order Complete"))

    return main

# Visualize
model = create_partial_join()
pm4py.view_powl(model, format='png')
```

## Verification Checklist

- [ ] All paths eventually reach termination
- [ ] No deadlock between joined and unjoined paths
- [ ] State consistency maintained
- [ ] Clear specification of which paths join

## Real-World Examples

1. **Microservices**: Some services sync, others continue
2. **Data Pipeline**: Some streams merge, others independent
3. **Multi-Step Process**: Partial sync at milestones

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #17 of 43**
