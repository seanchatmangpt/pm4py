# Simple Merge

> **Therefore**: Continue as soon as any one of multiple alternative paths completes.

---

## Context
You have multiple alternative paths in a process, but you only need one to complete before proceeding.

## Problem
**How do you merge multiple alternative paths without waiting for all of them?**

When a process splits into exclusive choices (only one path is taken), you need to merge these paths back together. Unlike synchronization (which waits for ALL paths), a simple merge proceeds as soon as ANY one path completes.

## Solution
Merge multiple alternative paths into a single flow, proceeding as soon as **one** incoming branch completes.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Exclusive choice with simple merge
model = parse_powl_model_string("""
    sequence(
        operator_choice(
            sequence('A', 'D'),
            sequence('B', 'D'),
            sequence('C', 'D')
        )
    )
""")

# Only ONE of (A→D, B→D, C→D) executes, then D proceeds
```

## Example
**Payment Processing**: A customer can pay via:
1. Credit card (A)
2. PayPal (B)
3. Bank transfer (C)

Only one payment method is used. After payment, the order confirmation (D) is sent immediately—no need to wait for the other payment methods.

```python
payment_model = parse_powl_model_string("""
    sequence(
        operator_choice(
            sequence('Credit Card', 'Order Confirmation'),
            sequence('PayPal', 'Order Confirmation'),
            sequence('Bank Transfer', 'Order Confirmation')
        )
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Merging paths from an exclusive choice (only one path executes)
- You want to proceed immediately after the chosen path completes
- Paths are mutually exclusive alternatives

❌ Don't use when:
- Merging parallel paths (use Synchronization)
- Multiple paths can execute simultaneously (use Multi-Merge or Discriminator)
- You need to wait for specific branches to complete (use Synchronizing Merge)

## Related Patterns
- [Exclusive Choice](./exclusive-choice.md) - Creates the alternative paths
- [Synchronization](./synchronization.md) - Waits for all branches
- [Multi-Merge](./multi-merge.md) - Merges without synchronization
- [Discriminator](./discriminator.md) - Waits for n of m branches

## Implementation Notes

### POWL v2
- Use `operator_choice()` for exclusive branching
- Simple merge is implicit—activities after choice execute when any choice completes
- No explicit merge construct needed in POWL v2

### BPMN 2.0
- Use **Exclusive Gateway** (diamond with X icon)
- Split: One incoming → multiple outgoing (based on conditions)
- Merge: Multiple incoming → one outgoing (proceeds on first arrival)
- Merge gateway has no conditions—just convergence

### Petri Nets
- **Transition** with multiple input places
- Fires when **any** input place has a token
- No synchronization required

### YAWL
- Use **XOR-split** for exclusive divergence
- Use **XOR-join** for simple merge
- Join proceeds when any incoming branch completes

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | No deadlocks if paths are truly exclusive |
| **Efficiency** | ✅ Excellent | No waiting for unnecessary branches |
| **Maintainability** | ✅ High | Clear semantic: "merge alternatives" |
| **Flexibility** | ✅ High | Easy to add/remove alternative paths |
| **Scalability** | ✅ High | Many alternatives handled efficiently |

## Common Pitfalls

1. **Confusion with Synchronization**: Simple merge is for alternatives, not parallel paths
2. **Incomplete Coverage**: Ensure all possible paths are covered by the merge
3. **Orphan Paths**: Every branch from the choice must lead to the merge

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

# Create simple merge pattern programmatically
def create_simple_merge():
    # Create activities
    credit_card = POWL("Credit Card")
    paypal = POWL("PayPal")
    bank_transfer = POWL("Bank Transfer")
    confirmation = POWL("Order Confirmation")

    # Create choice (exclusive)
    choice = Operator(Operator.CHOICE)
    choice.add_child(Operator.make_sequence(credit_card, confirmation))
    choice.add_child(Operator.make_sequence(paypal, confirmation))
    choice.add_child(Operator.make_sequence(bank_transfer, confirmation))

    return choice

# Visualize
model = create_simple_merge()
pm4py.view_powl(model, format='png')
```

## Verification Checklist

- [ ] All paths from the choice lead to the merge activity
- [ ] No path bypasses the merge activity
- [ ] Merge activity executes exactly once per choice
- [ ] No deadlock possible (all choice paths are valid)

## References
- van der Aalst, W. M. P., ter Hofstede, A. H. M., Kiepuszewski, B., & Barros, A. P. (2003). "Workflow Patterns". *Distributed and Parallel Databases*, 14(3), 5-51.
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #5 of 43**
