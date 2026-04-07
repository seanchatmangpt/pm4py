# Synchronizing Merge

> **Therefore**: Wait for all activated branches from a multi-choice to complete.

---

## Context
You have a multi-choice (Pattern 6) that activated multiple concurrent paths. You need to wait for **all activated paths** (not all possible paths) before proceeding.

## Problem
**How do you merge only the paths that were actually activated?**

Unlike synchronization (Pattern 4) which waits for ALL possible branches, synchronizing merge waits only for branches that were actually activated by the multi-choice. If 3 of 5 possible paths were activated, wait for those 3.

## Solution
Merge multiple paths where the number of paths to wait for is determined dynamically at runtime based on which branches were activated.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Multi-choice with synchronizing merge
model = parse_powl_model_string("""
    sequence(
        'Start',
        operator_choice(
            # Path A only
            sequence('A', 'Next'),
            # Paths B and C in parallel
            operator_parallel(
                sequence('B', 'Next'),
                sequence('C', 'Next')
            ),
            # Paths D, E, F in parallel
            operator_parallel(
                sequence('D', 'Next'),
                sequence('E', 'Next'),
                sequence('F', 'Next')
            )
        )
    )
""")

# If choice branch 2 selected: wait for B AND C
# If choice branch 3 selected: wait for D AND E AND F
```

## Example
**Loan Application**: Additional documentation may be required:
1. Tax returns (if self-employed)
2. Bank statements (if large deposit)
3. Employer verification (if new job)

```python
loan_model = parse_powl_model_string("""
    sequence(
        'Receive Application',
        operator_choice(
            # Standard employee
            sequence('Employer Verify', 'Underwriting'),
            # Self-employed (needs tax + employer)
            operator_parallel(
                sequence('Tax Returns', 'Underwriting'),
                sequence('Employer Verify', 'Underwriting')
            ),
            # Large deposit (needs bank + employer)
            operator_parallel(
                sequence('Bank Statements', 'Underwriting'),
                sequence('Employer Verify', 'Underwriting')
            ),
            # Self-employed + large deposit (needs all three)
            operator_parallel(
                sequence('Tax Returns', 'Underwriting'),
                sequence('Bank Statements', 'Underwriting'),
                sequence('Employer Verify', 'Underwriting')
            )
        )
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Merging paths from a multi-choice (dynamic number of paths)
- You need to wait for all activated paths before proceeding
- Paths were activated based on runtime conditions

❌ Don't use when:
- All possible paths always execute (use Synchronization)
- Only one path executes (use Simple Merge)
- Proceeding as soon as any path completes is acceptable (use Multi-Merge)

## Related Patterns
- [Multi-Choice](./multi-choice.md) - Creates the dynamic branches
- [Synchronization](./synchronization.md) - Waits for ALL possible paths
- [Discriminator](./discriminator.md) - Waits for n of m paths
- [Multi-Merge](./multi-merge.md) - No synchronization

## Implementation Notes

### POWL v2
- Use nested `operator_choice()` containing `operator_parallel()` branches
- Each parallel branch represents a combination of activated paths
- Synchronization is implicit within each parallel branch

### BPMN 2.0
- Use **Inclusive Gateway** for both split and merge
- Split: Evaluate conditions, activate matching paths
- Merge: Wait for all activated paths (based on tokens)

### Petri Nets
- Complex to implement—requires dynamic join
- Transition must track which branches were activated
- Requires additional places to count activated paths

### YAWL
- Use **OR-split** with conditions
- Use **OR-join** for synchronizing merge
- OR-join waits for all active branches to complete

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | If all combinations enumerated |
| **Efficiency** | ✅ High | No waiting for unused paths |
| **Maintainability** | ⚠️ Medium | Must enumerate all valid combinations |
| **Flexibility** | ⚠️ Medium | Adding conditions requires new combinations |
| **Scalability** | ⚠️ Low | Exponential growth with conditions |

## Common Pitfalls

1. **Missing Combinations**: Forgetting to enumerate some path combinations
2. **Deadlock**: If a path doesn't lead to merge, process hangs
3. **Complexity**: 3 conditions = 7 combinations to enumerate

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_synchronizing_merge():
    # Activities
    tax = POWL("Tax Returns")
    bank = POWL("Bank Statements")
    employer = POWL("Employer Verify")
    underwriting = POWL("Underwriting")

    # Create choice with all valid combinations
    choice = Operator(Operator.CHOICE)

    # Standard: employer only
    choice.add_child(Operator.make_sequence(employer, underwriting))

    # Self-employed: tax + employer
    parallel_tax = Operator(Operator.PARALLEL)
    parallel_tax.add_child(Operator.make_sequence(tax, underwriting))
    parallel_tax.add_child(Operator.make_sequence(employer, underwriting))
    choice.add_child(parallel_tax)

    # Large deposit: bank + employer
    parallel_bank = Operator(Operator.PARALLEL)
    parallel_bank.add_child(Operator.make_sequence(bank, underwriting))
    parallel_bank.add_child(Operator.make_sequence(employer, underwriting))
    choice.add_child(parallel_bank)

    # All three: tax + bank + employer
    parallel_all = Operator(Operator.PARALLEL)
    parallel_all.add_child(Operator.make_sequence(tax, underwriting))
    parallel_all.add_child(Operator.make_sequence(bank, underwriting))
    parallel_all.add_child(Operator.make_sequence(employer, underwriting))
    choice.add_child(parallel_all)

    return choice

# Visualize
model = create_synchronizing_merge()
pm4py.view_powl(model, format='png')
```

## Verification Checklist

- [ ] All valid path combinations are enumerated
- [ ] Every path in each combination leads to merge activity
- [ ] No path bypasses the merge
- [ ] Merge activity executes exactly once per choice

## References
- van der Aalst, W. M. P., ter Hofstede, A. H. M., Kiepuszewski, B., & Barros, A. P. (2003). "Workflow Patterns". *Distributed and Parallel Databases*, 14(3), 5-51.
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #7 of 43**
