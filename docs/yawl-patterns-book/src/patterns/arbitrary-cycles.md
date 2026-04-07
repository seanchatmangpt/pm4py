# Arbitrary Cycles

> **Therefore**: Allow repeated execution of activities without predefined structure.

---

## Context
You need to loop back to earlier activities in the process, but the loop isn't a simple "do-while" or "for-each"—it's based on runtime conditions and can occur at multiple points.

## Problem
**How do you allow cycles in the workflow without restricting when and how many times?**

Structured loops (Pattern 19) have clear entry/exit points. Arbitrary cycles allow any activity to revisit any previous activity based on conditions—like "go back to step 1 if validation fails" or "repeat review cycle until approved."

## Solution
Allow transitions that go backward in the process, creating cycles that can be traversed multiple times based on runtime conditions.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Arbitrary cycle: loop back to earlier activity
model = parse_powl_model_string("""
    sequence(
        'Submit Application',
        operator_choice(
            sequence('Review', 'Approve'),
            sequence('Review', 'Reject', 'Submit Application')  # Cycle back
        )
    )
""")

# If review fails → cycle back to Submit Application
```

## Example
**Document Review Process**:
1. Submit document
2. Review document
3. If issues found → return to submitter (cycle back)
4. If approved → proceed

```python
review_model = parse_powl_model_string("""
    sequence(
        'Submit Document',
        operator_choice(
            # Approved: proceed
            sequence('Review', 'Approve', 'Publish'),
            # Rejected: cycle back
            sequence('Review', 'Reject', 'Submit Document')
        )
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Activities need to be repeated based on runtime conditions
- Review/approval cycles with rework
- Validation that may require multiple attempts

❌ Don't use when:
- Loop has clear structure (use Structured Loop)
- Maximum iterations are known (use Structured Loop with counter)
- Cycle is predictable (use Sequence with conditions)

## Related Patterns
- [Structured Loop](./structured-loop.md) - Bounded, predictable loops
- [Deferred Choice](./deferred-choice.md) - Runtime path selection
- [Implicit Termination](./implicit-termination.md) - Detect cycle completion

## Implementation Notes

### POWL v2
- Use `operator_loop()` for explicit cycles
- Or use `operator_choice()` with backward references
- Loop operator provides structured cycles

### BPMN 2.0
- Use **Sequence Flow** going backward to earlier activities
- Or use **Subprocess with Loop**
- Ensure no deadlock (all cycles have exit conditions)

### Petri Nets
- **Cycles** are natural (places → transitions → places)
- Ensure liveness: all cycles can eventually exit
- Boundedness: cycles don't grow unbounded

### YAWL
- Use **explicit arcs** from later to earlier tasks
- Conditions on arcs determine when cycle occurs
- Decomposition loops for complex cycles

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ⚠️ Requires Care | Risk of infinite loops |
| **Efficiency** | ✅ High | Flexible, conditions-based |
| **Maintainability** | ⚠️ Medium | Can be hard to trace execution |
| **Flexibility** | ✅ Excellent | Any activity can cycle |
| **Scalability** | ⚠️ Medium | Complex cycles may be confusing |

## Common Pitfalls

1. **Infinite Loops**: No clear exit condition from cycle
2. **State Accumulation**: Each iteration may add state, causing issues
3. **Unbounded Cycles**: No maximum iteration limit

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_arbitrary_cycle():
    # Activities
    submit = POWL("Submit Document")
    review = POWL("Review")
    approve = POWL("Approve")
    reject = POWL("Reject")
    publish = POWL("Publish")

    # Create choice: approve or cycle back
    choice = Operator(Operator.CHOICE)

    # Path 1: Approved
    choice.add_child(Operator.make_sequence(review, approve, publish))

    # Path 2: Rejected (cycle back)
    cycle_sequence = Operator(Operator.SEQUENCE)
    cycle_sequence.add_child(review)
    cycle_sequence.add_child(reject)
    cycle_sequence.add_child(submit)  # Back to start
    choice.add_child(cycle_sequence)

    # Main sequence
    main = Operator(Operator.SEQUENCE)
    main.add_child(submit)
    main.add_child(choice)

    return main

# Visualize
model = create_arbitrary_cycle()
pm4py.view_powl(model, format='png')
```

## Bounded Cycle Example

```python
def create_bounded_cycle(max_iterations=3):
    """Cycle with maximum iteration limit"""
    # Use external counter to track iterations
    # After max_iterations reached, force exit path

    submit = POWL("Submit Document")
    review = POWL("Review")
    approve = POWL("Approve")
    reject = POWL("Reject")

    # Create loop with exit condition
    loop = Operator(Operator.LOOP)
    loop.set_do(Operator.make_sequence(submit, review))
    loop.set_exit(Operator.make_sequence(approve, 'Finalize'))
    loop.set_redo(Operator.make_sequence(reject))

    # External monitor: track iteration count
    # if iteration >= max: force exit
    # else: allow redo

    return loop
```

## Verification Checklist

- [ ] All cycles have exit conditions
- [ ] Maximum iteration limit defined (if applicable)
- [ ] No risk of infinite loops
- [ ] State is properly managed across iterations

## Real-World Examples

1. **Software Development**: Code → Review → Fix → Review (cycle)
2. **Procurement**: Request → Quote → Negotiate → Quote (cycle)
3. **Compliance**: Audit → Find Issues → Remediate → Audit (cycle)

## References
- van der Aalst, W. M. P., ter Hofstede, A. H. M., Kiepuszewski, B., & Barros, A. P. (2003). "Workflow Patterns". *Distributed and Parallel Databases*, 14(3), 5-51.
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #10 of 43**
