# Complete State

> **Therefore**: Mark process as complete with final state recorded.

---

## Context
You need to explicitly mark the process as complete and record the final state.

## Problem
**How do you complete a process and record final state?**

Complete (Pattern 20) completes process. Complete state also records final state.

## Solution
Explicitly complete the process instance and record the final state for audit and reporting.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Complete state: complete with state
model = parse_powl_model_string("""
    sequence(
        'Process Activities',
        'Record Final State',
        'Complete Process'
    )
""")
```

## Example
**Loan Application Completion**:
1. Process loan application
2. Make decision (approve/reject)
3. Record final state (decision, reason, timestamp)
4. Complete process

```python
loan_model = parse_powl_model_string("""
    sequence(
        'Process Application',
        'Make Decision',
        'Record Final State: Decision, Reason, Timestamp',
        'Complete Loan Process'
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Final state must be recorded
- Audit trail required
- Completion with state

❌ Don't use when:
- Implicit termination sufficient
- No state recording needed
- Process ends naturally

## Related Patterns
- [Complete](./complete.md) - Complete process
- [Implicit Termination](./implicit-termination.md) - No explicit end
- [Cancel Case](./cancel-case.md) - Terminate without completion

## Implementation Notes

### POWL v2
- Final activity records state
- Process completes
- State persisted

### BPMN 2.0
- **End Event** with state data
- Records final state
- Process termination

### Petri Nets
- **Final place** with state
- State recorded
- Process terminated

### YAWL
- **End task** with state
- State persisted
- Completion recorded

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | Clear completion |
| **Efficiency** | ✅ High | Explicit completion |
| **Maintainability** | ✅ High | Clear end point |
| **Flexibility** | ✅ High | Customizable state |
| **Scalability** | ✅ High | Works for complex processes |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_complete_state():
    # Activities
    process = POWL("Process Application")
    decision = POWL("Make Decision")
    record = POWL("Record Final State: Decision, Reason, Timestamp")
    complete = POWL("Complete Loan Process")

    # Sequence with state recording
    model = Operator.make_sequence(process, decision, record, complete)

    return model

# Visualize
model = create_complete_state()
pm4py.view_powl(model, format='png')

# Note: Final state must be persisted externally
```

## Real-World Examples

1. **Purchase Order**: Complete with final status
2. **Project**: Complete with final report
3. **Loan**: Complete with funding decision

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #34 of 43**
