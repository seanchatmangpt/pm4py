# Recovery

> **Therefore**: Recover from failure and retry or compensate.

---

## Context
You need to handle failures in the process and recover by retrying activities or compensating for completed work.

## Problem
**How do you recover from failures and restore consistent state?**

Cancel activity (Pattern 18) stops activity. Recovery handles failures and restores state.

## Solution
Detect failures and recover by retrying activities, compensating completed work, or rolling back to safe state.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Recovery: handle failure
model = parse_powl_model_string("""
    sequence(
        'Activity',
        operator_choice(
            'Success',
            sequence('Failure', 'Recover', 'Retry')
        )
    )
""")
```

## Example
**Payment Processing with Recovery**:
1. Process payment
2. If success → complete
3. If failure → recover (refund if partial) → retry

```python
payment_model = parse_powl_model_string("""
    sequence(
        'Process Payment',
        operator_choice(
            'Payment Success',
            sequence('Payment Failure', 'Refund if Partial', 'Retry Payment')
        )
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Activities may fail
- Recovery action needed
- Retry or compensation required

❌ Don't use when:
- No failure handling needed
- Activities always succeed
- No compensation possible

## Related Patterns
- [Cancel Activity](./cancel-activity.md) - Stop activity
- [History](./history.md) - Resume from checkpoint
- [Structured Loop](./structured-loop.md) - Retry loop

## Implementation Notes

### POWL v2
- Exception handling
- Compensation activities
- Retry logic

### BPMN 2.0
- **Error Event** attached to activity
- **Compensation Activity**
- **Retry** mechanism

### Petri Nets
- **Failure transition**
- **Compensation place**
- **Retry** transition

### YAWL
- **Exception handling**
- **Compensation** workflow
- **Retry** logic

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | Clear recovery semantics |
| **Efficiency** | ⚠️ Medium | Recovery overhead |
| **Maintainability** | ✅ High | Clear error handling |
| **Flexibility** | ✅ High | Multiple recovery strategies |
| **Scalability** | ✅ High | Handles many failures |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_recovery():
    # Activities
    process = POWL("Process Payment")
    success = POWL("Payment Success")
    failure = POWL("Payment Failure")
    refund = POWL("Refund if Partial")
    retry = POWL("Retry Payment")

    # Choice: success or recover
    choice = Operator(Operator.CHOICE)
    choice.add_child(success)
    choice.add_child(Operator.make_sequence(failure, refund, retry))

    # Main sequence
    main = Operator(Operator.SEQUENCE)
    main.add_child(process)
    main.add_child(choice)

    return main

# Visualize
model = create_recovery()
pm4py.view_powl(model, format='png')
```

## Real-World Examples

1. **Database Transaction**: Rollback on failure
2. **API Call**: Retry with exponential backoff
3. **Payment**: Refund and retry on failure

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #25 of 43**
