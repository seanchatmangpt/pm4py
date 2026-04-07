# Deferred Choice

> **Therefore**: Defer the choice between alternatives until runtime based on which occurs first.

---

## Context
You have multiple possible paths, but you don't know which one to take until runtime—based on which event occurs first or which condition becomes true.

## Problem
**How do you choose between alternatives at runtime instead of design time?**

Exclusive choice (Pattern 2) decides at design time which path to take based on conditions. Deferred choice waits for runtime events—like "wait for customer approval OR timeout, whichever comes first."

## Solution
Offer multiple alternatives but defer the choice until runtime, selecting the path based on which event occurs first or which condition becomes true.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Deferred choice: wait for first event
model = parse_powl_model_string("""
    sequence(
        'Start',
        operator_choice(
            sequence('Event A Occurs', 'Handle A'),
            sequence('Event B Occurs', 'Handle B')
        )
    )
""")

# At runtime: whichever event occurs first determines the path
```

## Example
**Payment Processing**: Wait for payment OR timeout:
1. Customer pays (Event A)
2. Payment window expires (Event B)

```python
payment_model = parse_powl_model_string("""
    sequence(
        'Send Invoice',
        operator_choice(
            sequence('Payment Received', 'Process Order'),
            sequence('Payment Timeout', 'Cancel Order')
        )
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Choice depends on which event occurs first
- Multiple external events can trigger next step
- You need to wait for one of several alternatives

❌ Don't use when:
- Choice can be made at design time (use Exclusive Choice)
- All alternatives must be executed (use Parallel Split)
- Choice is based on data conditions (use Multi-Choice)

## Related Patterns
- [Exclusive Choice](./exclusive-choice.md) - Design-time choice
- [Multi-Choice](./multi-choice.md) - Multiple paths can execute
- [Discriminator](./discriminator.md) - Proceed after first N complete
- [Event-Based Choice](./milestone.md) - State-based choice

## Implementation Notes

### POWL v2
- Deferred choice uses `operator_choice()` with external event monitoring
- Requires event engine to detect which event occurs first
- Once chosen, other alternatives are cancelled

### BPMN 2.0
- Use **Event-Based Gateway** (diamond with pentagon icon)
- Multiple **Intermediate Events** (message, timer, condition)
- First event that occurs determines the path

### Petri Nets
- **Conflict** between transitions
- First transition to fire wins
- Other transitions become disabled

### YAWL
- Use **OR-split** with external triggers
- Each alternative waits for specific event
- First event triggers that path, cancels others

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | No deadlock if events are mutually exclusive |
| **Efficiency** | ✅ Excellent | No waiting for all alternatives |
| **Maintainability** | ✅ High | Clear event-driven logic |
| **Flexibility** | ✅ High | Easy to add alternatives |
| **Scalability** | ✅ High | Many alternatives handled efficiently |

## Common Pitfalls

1. **Race Conditions**: Two events occur simultaneously
2. **Event Storms**: Too many events, unclear which wins
3. **Resource Leaks**: Cancelled alternatives may hold resources

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_deferred_choice():
    # Activities
    send_invoice = POWL("Send Invoice")
    payment = POWL("Payment Received")
    process_order = POWL("Process Order")
    timeout = POWL("Payment Timeout")
    cancel_order = POWL("Cancel Order")

    # Create deferred choice (external event monitoring)
    choice = Operator(Operator.CHOICE)

    # Alternative 1: Payment received
    choice.add_child(Operator.make_sequence(payment, process_order))

    # Alternative 2: Timeout
    choice.add_child(Operator.make_sequence(timeout, cancel_order))

    # Main sequence
    main = Operator(Operator.SEQUENCE)
    main.add_child(send_invoice)
    main.add_child(choice)

    return main

# Visualize
model = create_deferred_choice()
pm4py.view_powl(model, format='png')

# Note: Requires external event engine to monitor which event occurs first
```

## Implementation with Event Monitoring

```python
class DeferredChoiceEngine:
    def __init__(self, alternatives):
        self.alternatives = alternatives  # {event_name: activity}
        self.completed = False

    def on_event(self, event_name):
        """Handle first occurring event"""
        if self.completed:
            return  # Already chosen

        if event_name in self.alternatives:
            self.completed = True
            chosen_activity = self.alternatives[event_name]
            self.cancel_other_alternatives(event_name)
            return chosen_activity.execute()
        else:
            raise ValueError(f"Unknown event: {event_name}")

    def cancel_other_alternatives(self, chosen_event):
        """Cancel all alternatives except chosen one"""
        for event_name in self.alternatives:
            if event_name != chosen_event:
                # Cancel waiting activity
                self.alternatives[event_name].cancel()

# Usage
engine = DeferredChoiceEngine({
    "payment_received": payment_activity,
    "payment_timeout": timeout_activity
})

# When event occurs:
# engine.on_event("payment_received")  # Executes payment_activity
# engine.on_event("payment_timeout")   # Executes timeout_activity
```

## Real-World Examples

1. **Auction Processing**: Bid received OR auction ends (whichever first)
2. **Approval Workflow**: Manager approves OR escalation timeout (whichever first)
3. **API Retry**: Success response OR max retries exceeded (whichever first)

## Verification Checklist

- [ ] Events are mutually exclusive (only one can win)
- [ ] Cancelled alternatives are properly cleaned up
- [ ] No resource leaks from waiting alternatives
- [ ] Clear tie-breaking rule if events occur simultaneously

## References
- van der Aalst, W. M. P., ter Hofstede, A. H. M., Kiepuszewski, B., & Barros, A. P. (2003). "Workflow Patterns". *Distributed and Parallel Databases*, 14(3), 5-51.
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #12 of 43**
