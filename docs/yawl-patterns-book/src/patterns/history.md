# History

> **Therefore**: Resume process from a previous state after cancellation or interruption.

---

## Context
You need to restart a process from a previous state, possibly after cancellation or failure.

## Problem
**How do you restore a process to a previous state and resume execution?**

Cancel case (Pattern 19) terminates process. History allows resuming from previous state.

## Solution
Record process state at specific points and allow resuming from those points after interruption.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# History: save state, resume later
model = parse_powl_model_string("""
    sequence(
        'Activity A',
        'Save State',
        'Activity B',
        operator_choice(
            'Continue',
            sequence('Restore State', 'Resume from Save Point')
        )
    )
""")
```

## Example
**Long-Running Process**:
1. Start process
2. Complete step 1
3. Save checkpoint
4. Complete step 2
5. If failure → restore from checkpoint
6. Resume from checkpoint

```python
process_model = parse_powl_model_string("""
    sequence(
        'Step 1',
        'Save Checkpoint',
        'Step 2',
        operator_choice(
            'Complete',
            sequence('Restore Checkpoint', 'Resume from Checkpoint')
        )
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Long-running processes
- Risk of interruption
- Need to resume from checkpoints

❌ Don't use when:
- Short processes (no history needed)
- No interruption risk
- Stateless processes

## Related Patterns
- [Cancel Case](./cancel-case.md) - Terminate process
- [Recovery](./recovery.md) - Recover from failure
- [Complete](./complete.md) - Complete process

## Implementation Notes

### POWL v2
- Requires external state persistence
- Checkpoints at key points
- Restore mechanism

### BPMN 2.0
- **Intermediate Event** for checkpoint
- **Message Event** to resume
- State persistence

### Petri Nets
- **Marking** represents state
- Save marking at checkpoints
- Restore marking to resume

### YAWL
- **State persistence** in engine
- **Resume** capability
- Checkpoint mechanism

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | Clear state semantics |
| **Efficiency** | ⚠️ Medium | Overhead for state saving |
| **Maintainability** | ✅ High | Clear checkpoints |
| **Flexibility** | ✅ High | Multiple checkpoints |
| **Scalability** | ⚠️ Medium | State storage grows |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_history():
    # Activities
    step1 = POWL("Step 1")
    save = POWL("Save Checkpoint")
    step2 = POWL("Step 2")
    complete = POWL("Complete")
    restore = POWL("Restore Checkpoint")
    resume = POWL("Resume from Checkpoint")

    # Choice: complete or restore
    choice = Operator(Operator.CHOICE)
    choice.add_child(complete)
    choice.add_child(Operator.make_sequence(restore, resume))

    # Main sequence
    main = Operator(Operator.SEQUENCE)
    main.add_child(step1)
    main.add_child(save)
    main.add_child(step2)
    main.add_child(choice)

    return main

# Visualize
model = create_history()
pm4py.view_powl(model, format='png')

# Note: Requires external state persistence
```

## Real-World Examples

1. **Workflow Engine**: Resume workflow after server restart
2. **E-Commerce**: Resume checkout after abandonment
3. **Batch Processing**: Resume batch job from checkpoint

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #24 of 43**
