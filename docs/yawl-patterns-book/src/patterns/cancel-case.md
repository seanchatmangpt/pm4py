# Cancel Case

> **Therefore**: Terminate the entire process instance.

---

## Context
You need to completely stop and terminate an entire process instance, cancelling all activities and cleaning up resources.

## Problem
**How do you terminate an entire process instance immediately?**

Cancel activity (Pattern 18) cancels a single activity. Cancel case terminates the entire process—stopping all activities and cleaning up.

## Solution
Immediately terminate the entire process instance, cancelling all active and enabled activities and performing cleanup.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Cancel case: terminate entire process
model = parse_powl_model_string("""
    sequence(
        'Start Process',
        operator_choice(
            sequence('Continue', 'Complete'),
            'Cancel Case'  # Terminates entire process
        )
    )
""")
```

## Example
**Loan Application Cancellation**:
1. Start loan application
2. Customer can cancel at any time
3. If cancelled → terminate all activities, clean up
4. If not cancelled → continue to completion

```python
loan_model = parse_powl_model_string("""
    sequence(
        'Start Application',
        operator_choice(
            sequence('Process Application', 'Approve/Reject'),
            'Cancel Application'  # Terminates entire process
        )
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Entire process must be terminated
- All activities should stop immediately
- Cleanup required after termination

❌ Don't use when:
- Only some activities should stop (use Cancel Activity)
- Process should continue (use other patterns)
- Partial completion is acceptable

## Related Patterns
- [Cancel Activity](./cancel-activity.md) - Cancel single activity
- [Complete](./complete.md) - Complete process instance
- [Terminate](./terminate.md) - Force termination

## Implementation Notes

### POWL v2
- Requires external process engine
- Engine terminates entire POWL instance
- Cleanup of all resources

### BPMN 2.0
- Use **Terminate End Event** (solid circle with X)
- Immediately terminates process instance
- No compensation or cleanup by default

### Petri Nets
- **Sink transition** that consumes all tokens
- Removes all tokens from places
- Process terminated

### YAWL
- Use **cancel case** predicate
- Engine terminates workflow instance
- All activities cancelled

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | Clear termination semantics |
| **Efficiency** | ✅ Excellent | Immediate termination |
| **Maintainability** | ✅ High | Clear termination logic |
| **Flexibility** | ✅ High | Easy to add cancellation |
| **Scalability** | ✅ High | Handles complex processes |

## Common Pitfalls

1. **Incomplete Cleanup**: Resources not released
2. **State Corruption**: Partial state left inconsistent
3. **Orphan Activities**: Some activities continue running

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_cancel_case():
    # Activities
    start = POWL("Start Application")
    process = POWL("Process Application")
    decision = POWL("Approve/Reject")
    cancel = POWL("Cancel Application")

    # Choice: continue or cancel
    choice = Operator(Operator.CHOICE)
    choice.add_child(Operator.make_sequence(process, decision))
    choice.add_child(cancel)  # Terminates entire process

    # Main sequence
    main = Operator(Operator.SEQUENCE)
    main.add_child(start)
    main.add_child(choice)

    return main

# Visualize
model = create_cancel_case()
pm4py.view_powl(model, format='png')

# Note: Requires process engine to handle termination
```

## Implementation with Case Cancellation

```python
class CaseCancellation:
    def __init__(self, case_id):
        self.case_id = case_id
        self.active_activities = set()
        self.is_cancelled = False

    def register_activity(self, activity_id):
        """Register an activity as part of this case"""
        if not self.is_cancelled:
            self.active_activities.add(activity_id)
            return True
        return False  # Case already cancelled

    def cancel_case(self):
        """Cancel entire case"""
        self.is_cancelled = True
        # Cancel all active activities
        for activity_id in self.active_activities:
            self.cancel_activity(activity_id)
        self.active_activities.clear()
        # Perform cleanup
        self.cleanup()

    def cancel_activity(self, activity_id):
        """Cancel a specific activity"""
        # Stop activity, release resources
        pass

    def cleanup(self):
        """Cleanup resources after cancellation"""
        # Release database connections, file handles, etc.
        pass

# Usage
case = CaseCancellation("loan-app-123")
case.register_activity("process-application")
case.register_activity("credit-check")

# When cancellation requested:
# case.cancel_case()  # Cancels all activities, performs cleanup
```

## Real-World Examples

1. **E-Commerce Order**: Customer cancels entire order
2. **Workflow Process**: Admin cancels stuck workflow
3. **Batch Job**: Operator cancels long-running job

## Verification Checklist

- [ ] All activities are cancelled
- [ ] Resources are properly released
- [ ] State is cleaned up
- [ ] No orphan activities continue running

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #19 of 43**
