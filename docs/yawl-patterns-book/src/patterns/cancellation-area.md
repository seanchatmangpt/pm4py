# Cancellation Area

> **Therefore**: Cancel activities within an area and restore state.

---

## Context
You need to cancel all activities within a specific area and potentially restore the area to a previous state.

## Problem
**How do you cancel activities within an area and restore state?**

Cancellation region (Pattern 32) cancels activities. Cancellation area also restores state.

## Solution
Define a cancellation area; when cancelled, all activities in the area are cancelled and the area is restored to a previous state.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Cancellation area: cancel and restore state
model = parse_powl_model_string("""
    sequence(
        'Save Area State',
        'Area Activities',
        operator_choice(
            'Complete',
            sequence('Cancel Area', 'Restore State', 'Retry')
        )
    )
""")
```

## Example
**Transaction Processing with Rollback**:
1. Start transaction
2. Save state
3. Execute transaction activities
4. If error → cancel area, rollback to saved state
5. Retry or abort

```python
area_model = parse_powl_model_string("""
    sequence(
        'Save Transaction State',
        operator_parallel(
            'Area: Debit Account',
            'Area: Credit Account',
            'Area: Update Ledger'
        ),
        operator_choice(
            'Commit Transaction',
            sequence('Cancel Area', 'Restore State', 'Retry')
        )
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Activities must be atomic
- State restoration needed
- Transactional semantics

❌ Don't use when:
- No state restoration (use Cancellation Region)
- Individual activity cancellation (use Cancel Activity)
- No cancellation needed

## Related Patterns
- [Cancellation Region](./cancellation-region.md) - Cancel region
- [History](./history.md) - Restore from checkpoint
- [Recovery](./recovery.md) - Recover from failure

## Implementation Notes

### POWL v2
- Area state tracking
- Cancellation triggers restore
- State restoration mechanism

### BPMN 2.0
- **Transaction Subprocess**
- **Cancel Event** triggers rollback
- State restoration

### Petri Nets
- **Area** with state
- Cancellation transition
- State restoration

### YAWL
- **Cancellation area** with state
- Rollback mechanism
- State restoration

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | Clear state semantics |
| **Efficiency** | ⚠️ Medium | State overhead |
| **Maintainability** | ✅ High | Clear area boundaries |
| **Flexibility** | ✅ High | Easy to define areas |
| **Scalability** | ⚠️ Medium | State storage grows |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_cancellation_area():
    # Area: parallel activities
    area = Operator(Operator.PARALLEL)
    area.add_child(POWL("Area: Debit Account"))
    area.add_child(POWL("Area: Credit Account"))
    area.add_child(POWL("Area: Update Ledger"))

    # Choice: commit or cancel
    choice = Operator(Operator.CHOICE)
    choice.add_child(POWL("Commit Transaction"))
    choice.add_child(Operator.make_sequence(
        POWL("Cancel Area"),
        POWL("Restore State"),
        POWL("Retry")
    ))

    # Main sequence
    main = Operator(Operator.SEQUENCE)
    main.add_child(POWL("Save Transaction State"))
    main.add_child(area)
    main.add_child(choice)

    return main

# Visualize
model = create_cancellation_area()
pm4py.view_powl(model, format='png')

# Note: Requires external state tracking and restoration
```

## Real-World Examples

1. **Database Transaction**: Rollback on error
2. **Financial Transfer**: Restore accounts on failure
3. **Multi-Step Operation**: Rollback all steps on failure

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #33 of 43**
