# Without A-Priori Runtime

> **Therefore**: Create unknown number of instances dynamically at runtime.

---

## Context
You need to create instances of an activity dynamically, with the number not known in advance.

## Problem
**How do you create an unknown number of instances dynamically?**

A-priori runtime (Pattern 38) knows number at runtime. Without a-priori runtime doesn't know in advance.

## Solution
Create instances of an activity dynamically as needed, with the number of instances not known in advance.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Without a-priori runtime: dynamic instances
model = parse_powl_model_string("""
    sequence(
        'Process Items',
        'For Each Item: Create Instance'
    )
""")
```

## Example
**Processing Queue of Tasks**:
1. Tasks arrive in queue
2. For each task, create instance
3. Process each instance
4. Unknown number of tasks

```python
queue_model = parse_powl_model_string("""
    sequence(
        'Wait for Tasks',
        'For Each Task: Create Instance',
        'Process Task',
        'Repeat Until Queue Empty'
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Unknown number of instances
- Dynamic creation
- Runtime-driven instances

❌ Don't use when:
- Number known (use a-priori patterns)
- Fixed instances (use a-priori design time)
- Single instance

## Related Patterns
- [A-Priori Runtime](./a-priori-runtime.md) - Known at runtime
- [Design Time Plus Runtime](./design-time-plus-runtime.md) - Combination
- [Structured Loop](./structured-loop.md) - Loop with unknown iterations

## Implementation Notes

### POWL v2
- Dynamic instance creation
- No prior knowledge
- External loop logic

### BPMN 2.0
- **Multi-Instance Activity** with collection
- Collection size unknown
- Dynamic instances

### Petri Nets
- **Dynamic place/transition** creation
- Unknown instances
- Runtime structure

### YAWL
- **Multi-instance** with dynamic cardinality
- Unknown count
- Dynamic creation

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ⚠️ Requires Care | Unknown instances |
| **Efficiency** | ✅ High | Dynamic creation |
| **Maintainability** | ⚠️ Medium | Dynamic complexity |
| **Flexibility** | ✅ Excellent | Fully dynamic |
| **Scalability** | ✅ Excellent | Handles unknown numbers |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_without_a_priori_runtime():
    # Dynamic instance creation
    wait = POWL("Wait for Tasks")
    create = POWL("For Each Task: Create Instance")
    process = POWL("Process Task")
    repeat = POWL("Repeat Until Queue Empty")

    # Loop: create instances dynamically
    loop = Operator(Operator.LOOP)
    loop.set_do(Operator.make_sequence(create, process))
    loop.set_exit(repeat)
    loop.set_redo(Operator.make_sequence(wait, create, process))
    loop.set_exit_success(POWL("All Tasks Processed"))

    # Main sequence
    main = Operator(Operator.SEQUENCE)
    main.add_child(wait)
    main.add_child(loop)

    return main

# Visualize
model = create_without_a_priori_runtime()
pm4py.view_powl(model, format='png')

# Note: Instances created dynamically as tasks arrive
```

## Real-World Examples

1. **Queue Processing**: Process unknown number of queued items
2. **Event Handling**: Handle unknown number of events
3. **Batch Processing**: Process unknown batch size

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #39 of 43**
