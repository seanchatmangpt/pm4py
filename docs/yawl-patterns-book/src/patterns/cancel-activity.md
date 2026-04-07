# Cancel Activity

> **Therefore**: Disable a specific activity before it executes.

---

## Context
You need to prevent a specific activity from executing, even if it's been enabled, based on some condition or event.

## Problem
**How do you disable a specific activity before it starts?**

An activity may be enabled but should be cancelled based on external events—like "cancel shipment" if customer requests it.

## Solution
Disable a specific activity before it executes, based on a condition or event that occurs after the activity was enabled.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Cancel activity: disable before execution
model = parse_powl_model_string("""
    sequence(
        'Enable Activity',
        operator_choice(
            'Execute Activity',
            'Cancel Activity'  # Disables the activity
        )
    )
""")
```

## Example
**Shipment Cancellation**:
1. Order shipped
2. Customer can cancel before delivery
3. If cancelled → stop shipment
4. If not cancelled → deliver

```python
shipment_model = parse_powl_model_string("""
    sequence(
        'Ship Order',
        operator_choice(
            sequence('Cancel Request', 'Stop Shipment'),
            sequence('Deliver', 'Complete')
        )
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Activity should be cancellable after being enabled
- External events can prevent execution
- Graceful cancellation needed

❌ Don't use when:
- Activity executes immediately (no cancellation window)
- Cancellation not needed
- Activity always executes

## Related Patterns
- [Cancel Case](./cancel-case.md) - Cancel entire process
- [Milestone](./milestone.md) - Enable/disable based on state
- [Deferred Choice](./deferred-choice.md) - Runtime choice

## Implementation Notes

### POWL v2
- Requires external state tracking
- Monitor for cancellation events
- Disable activity when cancellation occurs

### BPMN 2.0
- Use **Cancel Event** attached to activity
- Or use **Message Event** to trigger cancellation
- Activity terminates when cancellation received

### Petri Nets
- **Inhibitor arc** to prevent transition firing
- External signal to disable transition
- Activity cannot execute after cancellation

### YAWL
- Use **cancellation set** on task
- External trigger to cancel
- Task removed from enabled set

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | Clear cancellation semantics |
| **Efficiency** | ✅ High | Prevents unnecessary work |
| **Maintainability** | ✅ High | Clear cancellation logic |
| **Flexibility** | ✅ High | Easy to add cancellations |
| **Scalability** | ✅ High | Many cancellable activities |

## Common Pitfalls

1. **Late Cancellation**: Cancellation after activity started
2. **Resource Leaks**: Resources not released on cancellation
3. **State Inconsistency**: Partial state after cancellation

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_cancel_activity():
    # Activities
    ship = POWL("Ship Order")
    cancel = POWL("Cancel Request")
    stop = POWL("Stop Shipment")
    deliver = POWL("Deliver")
    complete = POWL("Complete")

    # Choice: cancel or proceed
    choice = Operator(Operator.CHOICE)
    choice.add_child(Operator.make_sequence(cancel, stop))
    choice.add_child(Operator.make_sequence(deliver, complete))

    # Main sequence
    main = Operator(Operator.SEQUENCE)
    main.add_child(ship)
    main.add_child(choice)

    return main

# Visualize
model = create_cancel_activity()
pm4py.view_powl(model, format='png')

# Note: Requires external monitoring for cancellation events
```

## Implementation with Cancellation Monitoring

```python
class CancellationMonitor:
    def __init__(self):
        self.enabled_activities = set()
        self.cancelled_activities = set()

    def enable_activity(self, activity_id):
        """Enable an activity"""
        self.enabled_activities.add(activity_id)

    def cancel_activity(self, activity_id):
        """Cancel an activity"""
        self.cancelled_activities.add(activity_id)
        self.enabled_activities.discard(activity_id)

    def is_activity_enabled(self, activity_id):
        """Check if activity is enabled and not cancelled"""
        return (
            activity_id in self.enabled_activities and
            activity_id not in self.cancelled_activities
        )

# Usage
monitor = CancellationMonitor()
monitor.enable_activity("shipment")

# When cancellation request received:
# monitor.cancel_activity("shipment")

# Before executing activity:
# if monitor.is_activity_enabled("shipment"):
#     execute_shipment()
# else:
#     handle_cancellation()
```

## Real-World Examples

1. **Print Job**: Cancel print job before printing starts
2. **Scheduled Task**: Cancel scheduled task before execution
3. **Background Process**: Cancel background process

## Verification Checklist

- [ ] Cancellation is possible before activity starts
- [ ] Resources are released on cancellation
- [ ] State is consistent after cancellation
- [ ] No race conditions in cancellation

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #18 of 43**
