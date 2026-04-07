# Cancellation Region

> **Therefore**: Cancel all activities within a specific region.

---

## Context
You need to cancel all activities within a specific region of the process when a cancellation event occurs.

## Problem
**How do you cancel all activities within a region?**

Cancel case (Pattern 19) cancels entire process. Cancellation region cancels specific region.

## Solution
Define a cancellation region containing activities; when cancellation occurs, all activities in that region are cancelled.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Cancellation region: cancel activities in region
model = parse_powl_model_string("""
    sequence(
        'Start',
        operator_choice(
            sequence('Region Activity A', 'Region Activity B', 'Complete'),
            sequence('Cancel Region', 'Cancel All Region Activities')
        )
    )
""")
```

## Example
**Parallel Processing with Cancellation**:
1. Start parallel processing
2. Region: Multiple parallel activities
3. If error → cancel entire region
4. Continue with fallback

```python
region_model = parse_powl_model_string("""
    sequence(
        'Start Processing',
        operator_choice(
            sequence(
                operator_parallel(
                    'Region: Process A',
                    'Region: Process B',
                    'Region: Process C'
                ),
                'Complete'
            ),
            sequence('Cancel Region', 'Fallback Process')
        )
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Group of activities must cancel together
- Regional cancellation needed
- Fallback required

❌ Don't use when:
- Individual activity cancellation (use Cancel Activity)
- Entire process cancellation (use Cancel Case)
- No cancellation needed

## Related Patterns
- [Cancel Activity](./cancel-activity.md) - Cancel single activity
- [Cancel Case](./cancel-case.md) - Cancel entire process
- [Cancellation Area](./cancellation-area.md) - Cancel area with state

## Implementation Notes

### POWL v2
- Region defined by structure
- Cancellation affects region
- External monitoring

### BPMN 2.0
- **Subprocess** with cancellation event
- **Cancel Event** attached to subprocess
- All activities in subprocess cancelled

### Petri Nets
- **Region** in net
- Cancellation transition
- All activities in region cancelled

### YAWL
- **Cancellation set** for region
- External trigger
- All activities cancelled

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | Clear region semantics |
| **Efficiency** | ✅ High | Regional cancellation |
| **Maintainability** | ✅ High | Clear region boundaries |
| **Flexibility** | ✅ High | Easy to define regions |
| **Scalability** | ✅ High | Many regions |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_cancellation_region():
    # Region: parallel activities
    region = Operator(Operator.PARALLEL)
    region.add_child(POWL("Region: Process A"))
    region.add_child(POWL("Region: Process B"))
    region.add_child(POWL("Region: Process C"))

    # Choice: complete or cancel
    choice = Operator(Operator.CHOICE)
    choice.add_child(Operator.make_sequence(region, POWL("Complete")))
    choice.add_child(Operator.make_sequence(
        POWL("Cancel Region"),
        POWL("Fallback Process")
    ))

    # Main sequence
    main = Operator(Operator.SEQUENCE)
    main.add_child(POWL("Start Processing"))
    main.add_child(choice)

    return main

# Visualize
model = create_cancellation_region()
pm4py.view_powl(model, format='png')

# Note: Requires external monitoring for cancellation
```

## Real-World Examples

1. **Batch Processing**: Cancel entire batch on error
2. **Parallel Requests**: Cancel all requests on timeout
3. **Multi-Step Process**: Cancel remaining steps on failure

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #32 of 43**
