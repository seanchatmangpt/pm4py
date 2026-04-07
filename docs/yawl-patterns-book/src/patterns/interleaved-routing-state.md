# Interleaved Routing State

> **Therefore**: Route activities based on process state.

---

## Context
You need to route activities through different paths based on the current state of the process.

## Problem
**How do you route activities based on process state?**

Interleaved routing (Pattern 22) routes with flexible order. Interleaved routing state uses process state.

## Solution
Route activities through different paths based on the current state of the process, enabling dynamic routing decisions.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Interleaved routing state: route based on state
model = parse_powl_model_string("""
    sequence(
        'Set State',
        operator_choice(
            sequence('State A Path', 'Update State'),
            sequence('State B Path', 'Update State'),
            sequence('State C Path', 'Update State')
        )
    )
""")
```

## Example
**Document Routing Based on State**:
1. Document submitted
2. Based on state (type, priority, department) → route
3. State updates after each routing decision

```python
routing_model = parse_powl_model_string("""
    sequence(
        'Submit Document',
        operator_choice(
            sequence('State: High Priority', 'Route to Expedited'),
            sequence('State: Normal Priority', 'Route to Standard'),
            sequence('State: Low Priority', 'Route to Batch')
        ),
        'Update State'
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Routing depends on state
- Dynamic routing decisions
- State changes during process

❌ Don't use when:
- Static routing (use Exclusive Choice)
- No state tracking (use Interleaved Routing)
- Fixed routing paths

## Related Patterns
- [Interleaved Routing](./interleaved-routing.md) - Flexible routing
- [Milestone](./milestone.md) - State-based enabling
- [Multi-Choice](./multi-choice.md) - Conditional routing

## Implementation Notes

### POWL v2
- Requires state tracking
- Choice based on state
- State updates after routing

### BPMN 2.0
- **Exclusive Gateway** with conditions
- Conditions check process state
- State variables

### Petri Nets
- **Place** represents state
- Transition based on state
- State changes

### YAWL
- **Predicate** based on state
- Dynamic routing
- State variables

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | Clear state semantics |
| **Efficiency** | ✅ High | Dynamic routing |
| **Maintainability** | ⚠️ Medium | State complexity |
| **Flexibility** | ✅ High | Dynamic routing |
| **Scalability** | ✅ High | Many states |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_interleaved_routing_state():
    # Choice based on state
    choice = Operator(Operator.CHOICE)
    choice.add_child(Operator.make_sequence(
        POWL("State: High Priority"),
        POWL("Route to Expedited")
    ))
    choice.add_child(Operator.make_sequence(
        POWL("State: Normal Priority"),
        POWL("Route to Standard")
    ))
    choice.add_child(Operator.make_sequence(
        POWL("State: Low Priority"),
        POWL("Route to Batch")
    ))

    # Main sequence
    main = Operator(Operator.SEQUENCE)
    main.add_child(POWL("Submit Document"))
    main.add_child(choice)
    main.add_child(POWL("Update State"))

    return main

# Visualize
model = create_interleaved_routing_state()
pm4py.view_powl(model, format='png')

# Note: Requires external state tracking
```

## Real-World Examples

1. **Incident Management**: Route based on severity state
2. **Loan Processing**: Route based on approval state
3. **Customer Support**: Route based on issue state

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #30 of 43**
