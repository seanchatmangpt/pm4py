# Multi-Choice

> **Therefore**: Branch into multiple paths based on multiple conditions that may all be true.

---

## Context
You need to split a process into multiple paths where **two or more** paths may be taken simultaneously, not just one.

## Problem
**How do you branch into multiple concurrent paths based on conditions?**

Exclusive choice (Pattern 2) only allows one path. Multi-choice allows multiple paths to execute based on conditions—like "if credit score > 700 AND income > $50k, do BOTH premium approval AND fast track."

## Solution
Split into multiple paths where **zero or more** conditions can be true, executing all matching paths concurrently.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Multi-choice: conditions A, B, C may all be true
model = parse_powl_model_string("""
    sequence(
        'Start',
        operator_choice(
            sequence('A', 'Merge'),
            operator_parallel(
                sequence('B', 'Merge'),
                sequence('C', 'Merge')
            )
        )
    )
""")

# If only A true: execute A
# If B and C true: execute both B and C in parallel
# If all true: execute A, B, C
```

## Example
**Insurance Claim Processing**: A claim may require:
1. Auto damage assessment (if vehicle involved)
2. Medical review (if injury reported)
3. Police report verification (if police called)

Multiple conditions can be true simultaneously:

```python
insurance_model = parse_powl_model_string("""
    sequence(
        'Receive Claim',
        operator_choice(
            # Only property damage
            sequence('Assess Property Damage', 'Process Claim'),
            # Property + medical (parallel)
            operator_parallel(
                sequence('Assess Property Damage', 'Process Claim'),
                sequence('Medical Review', 'Process Claim')
            ),
            # Property + medical + police (parallel)
            operator_parallel(
                sequence('Assess Property Damage', 'Process Claim'),
                sequence('Medical Review', 'Process Claim'),
                sequence('Verify Police Report', 'Process Claim')
            )
        )
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Multiple conditions can be true simultaneously
- You need to execute all applicable paths
- Paths are independent and can run concurrently

❌ Don't use when:
- Only one condition can be true (use Exclusive Choice)
- Paths must execute sequentially (use Sequence)
- Conditions are mutually exclusive

## Related Patterns
- [Exclusive Choice](./exclusive-choice.md) - Only one path
- [Parallel Split](./parallel-split.md) - Always execute all paths
- [Deferred Choice](./deferred-choice.md) - Choice made at runtime
- [Synchronizing Merge](./synchronizing-merge.md) - Merge multi-choice paths

## Implementation Notes

### POWL v2
- Use nested `operator_choice()` and `operator_parallel()`
- Each choice branch represents a combination of conditions
- Must enumerate all valid condition combinations

### BPMN 2.0
- Use **Inclusive Gateway** (diamond with circle icon)
- Split: Evaluate all conditions, execute all true paths
- Merge: Use **Inclusive Gateway** to join (waits for all activated paths)

### Petri Nets
- **Transition** with multiple output places
- Places represent conditions; tokens flow to all true conditions
- Requires merging transition to synchronize

### YAWL
- Use **OR-split** with multiple conditions
- Each condition can be true independently
- OR-join required to merge activated paths

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ⚠️ Requires Care | Must handle all condition combinations |
| **Efficiency** | ✅ High | Parallel execution of applicable paths |
| **Maintainability** | ⚠️ Medium | Complexity grows with conditions (2^n combinations) |
| **Flexibility** | ✅ High | Easy to add new conditions |
| **Scalability** | ⚠️ Medium | Many conditions = exponential complexity |

## Common Pitfalls

1. **Combinatorial Explosion**: 3 conditions = 7 combinations (2³ - 1)
2. **Incomplete Coverage**: Missing some condition combinations
3. **Race Conditions**: Parallel paths accessing shared resources

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_multi_choice():
    # Activities
    assess_damage = POWL("Assess Damage")
    medical_review = POWL("Medical Review")
    police_verify = POWL("Police Verify")
    process_claim = POWL("Process Claim")

    # Create multi-choice combinations
    choice = Operator(Operator.CHOICE)

    # Only damage
    choice.add_child(Operator.make_sequence(assess_damage, process_claim))

    # Damage + medical
    parallel_2 = Operator(Operator.PARALLEL)
    parallel_2.add_child(Operator.make_sequence(assess_damage, process_claim))
    parallel_2.add_child(Operator.make_sequence(medical_review, process_claim))
    choice.add_child(parallel_2)

    # Damage + medical + police
    parallel_3 = Operator(Operator.PARALLEL)
    parallel_3.add_child(Operator.make_sequence(assess_damage, process_claim))
    parallel_3.add_child(Operator.make_sequence(medical_review, process_claim))
    parallel_3.add_child(Operator.make_sequence(police_verify, process_claim))
    choice.add_child(parallel_3)

    return choice

# Visualize
model = create_multi_choice()
pm4py.view_powl(model, format='png')
```

## Verification Checklist

- [ ] All valid condition combinations are covered
- [ ] Merge point waits for all activated paths
- [ ] No deadlock possible (all paths lead to merge)
- [ ] Parallel paths are independent (no shared state)

## References
- van der Aalst, W. M. P., ter Hofstede, A. H. M., Kiepuszewski, B., & Barros, A. P. (2003). "Workflow Patterns". *Distributed and Parallel Databases*, 14(3), 5-51.
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #6 of 43**
