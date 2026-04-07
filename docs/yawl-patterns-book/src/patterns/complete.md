# Complete

> **Therefore**: Explicitly complete a process instance with final state.

---

## Context
You need to explicitly mark a process instance as completed, potentially with final state or results.

## Problem
**How do you explicitly complete a process instance with final state?**

Implicit termination (Pattern 11) ends when no work remains. Complete explicitly marks the process as completed with final state.

## Solution
Explicitly complete the process instance, potentially recording final state, results, or performing final actions.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Complete: explicit completion
model = parse_powl_model_string("""
    sequence(
        'Process Activities',
        'Complete Process'  # Explicit completion
    )
""")
```

## Example
**Project Completion**:
1. Execute project tasks
2. Verify all deliverables
3. Complete project with final report

```python
project_model = parse_powl_model_string("""
    sequence(
        'Execute Tasks',
        'Verify Deliverables',
        'Complete Project'  # Explicit completion
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Explicit completion action needed
- Final state must be recorded
- Cleanup or finalization required

❌ Don't use when:
- Implicit termination sufficient
- No final action needed
- Process ends naturally

## Related Patterns
- [Implicit Termination](./implicit-termination.md) - No explicit end
- [Cancel Case](./cancel-case.md) - Terminate without completion
- [Complete State](./complete-state.md) - State-based completion

## Implementation Notes

### POWL v2
- Final activity in process
- Records completion state
- Triggers cleanup

### BPMN 2.0
- Use **End Event** (circle with thick border)
- Can include result data
- Triggers process completion

### Petri Nets
- **Final place** with token
- Marks process completed
- No further transitions

### YAWL
- Use **end task** or **completion condition**
- Explicit completion
- Records final state

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | Clear completion |
| **Efficiency** | ✅ High | Explicit completion |
| **Maintainability** | ✅ High | Clear end point |
| **Flexibility** | ✅ High | Easy to customize |
| **Scalability** | ✅ High | Works for complex processes |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL

def create_complete():
    # Activities
    execute = POWL("Execute Tasks")
    verify = POWL("Verify Deliverables")
    complete = POWL("Complete Project")

    # Sequence with explicit completion
    model = Operator.make_sequence(execute, verify, complete)

    return model

# Visualize
model = create_complete()
pm4py.view_powl(model, format='png')
```

## Real-World Examples

1. **Purchase Order**: Complete with final approval
2. **Project**: Complete with final report
3. **Loan**: Complete with funding confirmation

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #20 of 43**
