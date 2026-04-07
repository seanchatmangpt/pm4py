# Milestone State

> **Therefore**: Enable activities based on reaching specific states.

---

## Context
You need to enable or disable activities based on whether the process has reached specific milestone states.

## Problem
**How do you enable activities only after reaching specific states?**

Milestone (Pattern 14) enables activities after milestones. Milestone state uses state for enabling.

## Solution
Enable activities only when the process reaches specific milestone states, disabling activities before those states are reached.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Milestone state: enable based on state
model = parse_powl_model_string("""
    sequence(
        'Reach State A',
        operator_choice(
            sequence('State A Reached', 'Enabled Activity'),
            'Disabled Activity'  # Until State A reached
        )
    )
""")
```

## Example
**Approval Milestones**:
1. Submit request
2. State: Manager Approved
3. Activity: Finance Review (enabled only after manager approval)

```python
approval_model = parse_powl_model_string("""
    sequence(
        'Submit Request',
        'Manager Approval',
        operator_choice(
            sequence('State: Manager Approved', 'Finance Review'),
            'Wait for Manager Approval'  # Disabled until approved
        )
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Activities enabled by state
- Milestone-based enabling
- State-driven workflow

❌ Don't use when:
- Activities always enabled (no state check)
- Event-based enabling (use Deferred Choice)
- No state tracking

## Related Patterns
- [Milestone](./milestone.md) - Enable after milestone
- [Interleaved Routing State](./interleaved-routing-state.md) - Route based on state
- [Cancel Activity](./cancel-activity.md) - Disable activity

## Implementation Notes

### POWL v2
- State tracking required
- Activities check state
- Enable/disable based on state

### BPMN 2.0
- **Conditional Event**
- Checks process state
- Enables when state reached

### Petri Nets
- **Place** represents state
- Transition enabled when place has token
- State-based enabling

### YAWL
- **Predicate** on task
- Checks state
- Enables when predicate true

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | Clear state semantics |
| **Efficiency** | ✅ High | State-based enabling |
| **Maintainability** | ✅ High | Clear milestones |
| **Flexibility** | ✅ High | Easy to add states |
| **Scalability** | ✅ High | Many states |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_milestone_state():
    # Choice: enabled only after state reached
    choice = Operator(Operator.CHOICE)
    choice.add_child(Operator.make_sequence(
        POWL("State: Manager Approved"),
        POWL("Finance Review")
    ))
    choice.add_child(POWL("Wait for Manager Approval"))

    # Main sequence
    main = Operator(Operator.SEQUENCE)
    main.add_child(POWL("Submit Request"))
    main.add_child(POWL("Manager Approval"))
    main.add_child(choice)

    return main

# Visualize
model = create_milestone_state()
pm4py.view_powl(model, format='png')

# Note: Requires external state tracking
```

## Real-World Examples

1. **Software Release**: Enable deployment only after testing complete
2. **Procurement**: Enable payment only after goods received
3. **Compliance**: Enable audit only after training complete

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #31 of 43**
