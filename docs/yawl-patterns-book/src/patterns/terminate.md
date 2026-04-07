# Terminate

> **Therefore**: Force immediate termination of process instance.

---

## Context
You need to immediately terminate a process instance, potentially before all activities complete.

## Problem
**How do you force immediate termination of a process?**

Cancel case (Pattern 19) cancels process. Terminate forces immediate stop.

## Solution
Immediately terminate the process instance, stopping all activities without completing or compensating.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Terminate: immediate stop
model = parse_powl_model_string("""
    sequence(
        'Start Process',
        operator_choice(
            sequence('Continue', 'Complete'),
            'Terminate Immediately'  # Force stop
        )
    )
""")
```

## Example
**Emergency Shutdown**:
1. Process running
2. Emergency detected
3. Terminate immediately (no cleanup, no compensation)
4. Process stopped

```python
emergency_model = parse_powl_model_string("""
    sequence(
        'Start Process',
        operator_choice(
            sequence('Normal Operation', 'Complete'),
            'Terminate Immediately'  # Emergency stop
        )
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Immediate termination required
- No time for cleanup
- Emergency stop

❌ Don't use when:
- Graceful shutdown needed (use Cancel Case)
- Cleanup required (use Cancellation Area)
- Normal completion (use Complete)

## Related Patterns
- [Cancel Case](./cancel-case.md) - Cancel with cleanup
- [Complete](./complete.md) - Complete process
- [Cancel Activity](./cancel-activity.md) - Cancel single activity

## Implementation Notes

### POWL v2
- Immediate termination
- No cleanup
- External trigger

### BPMN 2.0
- **Terminate End Event** (solid circle with X)
- Immediate termination
- No compensation

### Petri Nets
- **Sink transition**
- Consumes all tokens
- Immediate stop

### YAWL
- **Terminate** predicate
- Immediate stop
- No cleanup

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ⚠️ Requires Care | Abrupt termination |
| **Efficiency** | ✅ Excellent | Immediate stop |
| **Maintainability** | ⚠️ Medium | Abrupt semantics |
| **Flexibility** | ✅ High | Easy to add |
| **Scalability** | ✅ High | Works for complex processes |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_terminate():
    # Choice: continue or terminate
    choice = Operator(Operator.CHOICE)
    choice.add_child(Operator.make_sequence(
        POWL("Normal Operation"),
        POWL("Complete")
    ))
    choice.add_child(POWL("Terminate Immediately"))

    # Main sequence
    main = Operator(Operator.SEQUENCE)
    main.add_child(POWL("Start Process"))
    main.add_child(choice)

    return main

# Visualize
model = create_terminate()
pm4py.view_powl(model, format='png')

# Note: Terminate is immediate - no cleanup
```

## Real-World Examples

1. **Emergency Stop**: Immediate shutdown of machinery
2. **Security Breach**: Terminate all processes
3. **System Failure**: Emergency termination

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #35 of 43**
