# Milestone

> **Therefore**: Enable an activity only after reaching a specific state.

---

## Context
You have an activity that should only be possible after certain conditions are met or after reaching a specific milestone in the process.

## Problem
**How do you enable an activity only after reaching a specific state?**

Some activities should only be possible after certain conditions are met—like "cancel order" is only possible before shipping, or "return item" is only possible after delivery.

## Solution
Enable an activity only when the process reaches a specific state or milestone—before the milestone, the activity is disabled; after the milestone, it becomes enabled.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Milestone: enable activity only after specific point
model = parse_powl_model_string("""
    sequence(
        'Start',
        operator_choice(
            sequence('A', 'Milestone Reached', 'Enabled Activity'),
            'Enabled Activity'  # Disabled until milestone
        )
    )
""")

# "Enabled Activity" only possible after "Milestone Reached"
```

## Example
**Order Cancellation**: Customer can cancel order only before shipping:
1. Order placed
2. Payment processed
3. **Milestone: Order shipped**
4. Cancellation no longer possible

```python
cancellation_model = parse_powl_model_string("""
    sequence(
        'Order Placed',
        operator_choice(
            # Before shipping: can cancel
            sequence('Cancel Order', 'Refund'),
            # After shipping: cannot cancel
            sequence('Order Shipped', 'Delivery')
        )
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Activity should only be possible after certain conditions
- You need to enable/disable activities based on state
- Milestone-based access control

❌ Don't use when:
- Activity is always available (no milestone needed)
- Choice is based on data conditions (use Exclusive Choice)
- Activity is always enabled (use Sequence)

## Related Patterns
- [Deferred Choice](./deferred-choice.md) - Runtime event-based choice
- [Milestone State](./milestone-state.md) - State-based enabling
- [Cancel Activity](./cancel-activity.md) - Disable activity after milestone

## Implementation Notes

### POWL v2
- Milestone requires **state tracking** outside POWL core
- Implement via monitoring process state
- Enable/disable activities based on state

### BPMN 2.0
- Use **Intermediate Conditional Event**
- Or use **Message Event** with state check
- Condition evaluates current process state

### Petri Nets
- **Place** represents milestone state
- Transition to activity only enabled when place has token
- Inhibitor arc to disable before milestone

### YAWL
- Use **predicate** on task
- Predicate checks process state
- Task only enabled when predicate is true

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | Clear enable/disable semantics |
| **Efficiency** | ✅ High | No unnecessary checks |
| **Maintainability** | ✅ High | Clear state-based logic |
| **Flexibility** | ✅ High | Easy to add milestones |
| **Scalability** | ✅ High | Many milestones handled efficiently |

## Common Pitfalls

1. **State Mismatch**: Milestone state doesn't match actual process state
2. **Stale State**: State not updated when process advances
3. **Race Conditions**: Activity enabled just before milestone changes

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_milestone():
    # Activities
    order_placed = POWL("Order Placed")
    cancel = POWL("Cancel Order")
    refund = POWL("Refund")
    ship = POWL("Order Shipped")
    delivery = POWL("Delivery")

    # Create choice: cancel before ship, or proceed
    choice = Operator(Operator.CHOICE)

    # Path 1: Cancel (only before milestone)
    choice.add_child(Operator.make_sequence(cancel, refund))

    # Path 2: Ship (milestone - cancellation disabled after this)
    choice.add_child(Operator.make_sequence(ship, delivery))

    # Main sequence
    main = Operator(Operator.SEQUENCE)
    main.add_child(order_placed)
    main.add_child(choice)

    return main

# Visualize
model = create_milestone()
pm4py.view_powl(model, format='png')

# Note: Milestone logic requires external state tracking
# "Cancel Order" only enabled before "Order Shipped"
```

## Implementation with State Tracking

```python
class MilestoneTracker:
    def __init__(self):
        self.milestones_reached = set()
        self.activity_milestones = {
            "cancel_order": "before_shipping",
            "return_item": "after_delivery",
            "refund": "always"
        }

    def reach_milestone(self, milestone):
        """Mark milestone as reached"""
        self.milestones_reached.add(milestone)

    def is_activity_enabled(self, activity):
        """Check if activity is enabled based on milestones"""
        required_milestone = self.activity_milestones.get(activity)

        if required_milestone == "always":
            return True
        elif required_milestone.startswith("before_"):
            # Enabled only if milestone NOT reached
            milestone = required_milestone.replace("before_", "")
            return milestone not in self.milestones_reached
        elif required_milestone.startswith("after_"):
            # Enabled only if milestone IS reached
            milestone = required_milestone.replace("after_", "")
            return milestone in self.milestones_reached

        return False

# Usage
tracker = MilestoneTracker()

# Initially: cancellation enabled
tracker.is_activity_enabled("cancel_order")  # True

# After shipping milestone
tracker.reach_milestone("shipping")
tracker.is_activity_enabled("cancel_order")  # False (disabled)
```

## Real-World Examples

1. **Voting**: Change vote only before polls close
2. **Auction**: Place bid only before auction ends
3. **Software**: Release version only after all tests pass

## Verification Checklist

- [ ] Milestone state is accurately tracked
- [ ] Activities are properly enabled/disabled
- [ ] State transitions are atomic
- [ ] No race conditions in state checks

## References
- van der Aalst, W. M. P., ter Hofstede, A. H. M., Kiepuszewski, B., & Barros, A. P. (2003). "Workflow Patterns". *Distributed and Parallel Databases*, 14(3), 5-51.
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #14 of 43**
