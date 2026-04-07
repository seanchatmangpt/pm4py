# Parent Join

> **Therefore**: Merge subprocess results back into parent process.

---

## Context
You have a subprocess that executes multiple concurrent activities, and you need to merge the results back into the parent process.

## Problem
**How do you merge subprocess results into the parent process?**

Synchronization (Pattern 4) merges paths within same process. Parent join merges subprocess results back into parent.

## Solution
Merge multiple paths from a subprocess back into the parent process, synchronizing subprocess completion.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Parent join: merge subprocess results
model = parse_powl_model_string("""
    sequence(
        'Start Parent',
        operator_parallel(
            sequence('Subprocess A', 'Parent Join'),
            sequence('Subprocess B', 'Parent Join'),
            sequence('Subprocess C', 'Parent Join')
        ),
        'Continue Parent'
    )
""")
```

## Example
**Order Processing Subprocess**:
1. Start order process
2. Execute subprocesses: payment, inventory, shipping
3. Join all subprocess results
4. Continue with fulfillment

```python
order_model = parse_powl_model_string("""
    sequence(
        'Start Order',
        operator_parallel(
            sequence('Payment Subprocess', 'Join Results'),
            sequence('Inventory Subprocess', 'Join Results'),
            sequence('Shipping Subprocess', 'Join Results')
        ),
        'Fulfillment'
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Subprocess has multiple concurrent paths
- Results need to merge into parent
- Synchronization after subprocess

❌ Don't use when:
- No subprocess (use Synchronization)
- Subprocess doesn't merge (use Implicit Termination)

## Related Patterns
- [Synchronization](./synchronization.md) - Merge within same level
- [Partial Join](./partial-join.md) - Merge some paths
- [Thread Join](./thread-join.md) - Thread-based join

## Implementation Notes

### POWL v2
- Parallel operator represents subprocess
- All branches complete before parent continues
- Results aggregated at join point

### BPMN 2.0
- Use **Subprocess** with parallel activities
- **Parallel Gateway** joins subprocess paths
- Data passed back to parent

### Petri Nets
- **Subnet** representing subprocess
- Merge transition joins subnet outputs
- Synchronization at subnet boundary

### YAWL
- Use **composite task** for subprocess
- **AND-join** merges subprocess results
- Data aggregation at join

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | Clear synchronization |
| **Efficiency** | ✅ High | Concurrent subprocess |
| **Maintainability** | ✅ High | Clear subprocess structure |
| **Flexibility** | ⚠️ Medium | Fixed subprocess structure |
| **Scalability** | ✅ High | Multiple subprocesses |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_parent_join():
    # Create subprocess branches
    payment = Operator.make_sequence(
        POWL("Payment Subprocess"),
        POWL("Join Results")
    )

    inventory = Operator.make_sequence(
        POWL("Inventory Subprocess"),
        POWL("Join Results")
    )

    shipping = Operator.make_sequence(
        POWL("Shipping Subprocess"),
        POWL("Join Results")
    )

    # Parallel subprocess
    parallel = Operator(Operator.PARALLEL)
    parallel.add_child(payment)
    parallel.add_child(inventory)
    parallel.add_child(shipping)

    # Parent process
    parent = Operator(Operator.SEQUENCE)
    parent.add_child(POWL("Start Order"))
    parent.add_child(parallel)
    parent.add_child(POWL("Fulfillment"))

    return parent

# Visualize
model = create_parent_join()
pm4py.view_powl(model, format='png')
```

## Real-World Examples

1. **Loan Approval**: Multiple checks merge into decision
2. **Project Management**: Multiple tasks merge into milestone
3. **Manufacturing**: Multiple assembly lines merge into product

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #21 of 43**
