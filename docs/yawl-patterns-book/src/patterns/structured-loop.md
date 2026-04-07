# Structured Loop

> **Therefore**: Repeatedly execute a set of activities until a condition is met.

---

## Context
You need to repeat a set of activities multiple times until a specific condition is met—like "retry 3 times" or "loop until approved."

## Problem
**How do you create a bounded, structured loop with clear entry and exit conditions?**

Arbitrary cycles (Pattern 10) allow any activity to revisit any previous activity. Structured loops have clear do-while or repeat-until semantics with bounded iterations.

## Solution
Repeatedly execute a set of activities (the "loop body") until a specific exit condition is met or maximum iterations reached.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Structured loop: repeat until condition
model = parse_powl_model_string("""
    operator_loop(
        'Loop Body',
        'Exit Condition',
        'Exit Action'
    )
""")

# Executes: Loop Body → Exit Condition?
# If false: Loop Body → Exit Condition? → ...
# If true: Exit Action (proceed)
```

## Example
**Invoice Approval Loop**:
1. Submit invoice
2. Review invoice
3. If rejected → resubmit (loop)
4. If approved → proceed (exit)

```python
approval_model = parse_powl_model_string("""
    operator_loop(
        sequence('Submit Invoice', 'Review'),
        'Approved?',
        'Process Payment'
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Clear loop structure with entry/exit conditions
- Maximum iterations can be bounded
- Loop body is well-defined

❌ Don't use when:
- Any activity can revisit any other (use Arbitrary Cycles)
- Loop is unbounded (use with caution)
- No clear exit condition

## Related Patterns
- [Arbitrary Cycles](./arbitrary-cycles.md) - Unstructured cycles
- [Deferred Choice](./deferred-choice.md) - Runtime choice
- [Discriminator](./discriminator.md) - N of M completion

## Implementation Notes

### POWL v2
- Use `operator_loop()` for structured loops
- Set `do` (loop body), `exit` (exit condition), `redo` (loop back)
- Loop operator provides clear semantics

### BPMN 2.0
- Use **Subprocess with LoopCharacteristics**
- Or use **Sequence Flow** going back with condition
- Standard loop: while, do-while, for-each

### Petri Nets
- **Cycle** in the net
- Transition checks exit condition
- Loop back if condition false

### YAWL
- Use **decomposition loop**
- Or use **explicit loop** with conditions
- Bounded loops with max iterations

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | If exit condition always reachable |
| **Efficiency** | ✅ High | Clear loop structure |
| **Maintainability** | ✅ High | Easy to understand |
| **Flexibility** | ⚠️ Medium | Fixed loop structure |
| **Scalability** | ✅ High | Bounded iterations |

## Common Pitfalls

1. **Infinite Loops**: Exit condition never met
2. **Unbounded Loops**: No maximum iteration limit
3. **State Accumulation**: Each iteration adds state

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_structured_loop():
    # Create loop body
    loop_body = Operator.make_sequence(
        POWL("Submit Invoice"),
        POWL("Review")
    )

    # Create loop
    loop = Operator(Operator.LOOP)
    loop.set_do(loop_body)
    loop.set_exit(POWL("Approved?"))
    loop.set_redo(POWL("Resubmit"))
    loop.set_exit_success(Operator.make_sequence(
        POWL("Process Payment"),
        POWL("Complete")
    ))

    return loop

# Visualize
model = create_structured_loop()
pm4py.view_powl(model, format='png')
```

## Bounded Loop Example

```python
def create_bounded_loop(max_iterations=3):
    """Loop with maximum iteration limit"""
    loop = Operator(Operator.LOOP)

    # Loop body
    loop_body = Operator.make_sequence(
        POWL("Attempt Action"),
        POWL("Check Result")
    )
    loop.set_do(loop_body)

    # Exit condition
    loop.set_exit(POWL("Success?"))

    # Redo (with counter check)
    # External monitoring: if iteration >= max, force exit
    loop.set_redo(POWL("Retry"))

    # Exit success
    loop.set_exit_success(POWL("Complete"))

    return loop
```

## Verification Checklist

- [ ] Exit condition is always reachable
- [ ] Maximum iterations defined (if applicable)
- [ ] Loop body doesn't accumulate state indefinitely
- [ ] No risk of infinite loops

## Real-World Examples

1. **Retry Logic**: Retry API call up to 3 times
2. **Approval Process**: Resubmit until approved (max 5 times)
3. **Data Processing**: Process records until empty

## References
- van der Aalst, W. M. P., ter Hofstede, A. H. M., Kiepuszewski, B., & Barros, A. P. (2003). "Workflow Patterns". *Distributed and Parallel Databases*, 14(3), 5-51.
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #15 of 43**
