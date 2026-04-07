# Interleaved Looping

> **Therefore**: Execute multiple loops concurrently with interleaved iterations.

---

## Context
You have multiple loops that need to execute concurrently, with iterations potentially interleaved.

## Problem
**How do you execute multiple loops concurrently with interleaved iterations?**

Structured loop (Pattern 15) executes one loop. Interleaved looping executes multiple loops concurrently.

## Solution
Execute multiple loops concurrently where iterations from different loops can interleave.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Interleaved looping: concurrent loops
model = parse_powl_model_string("""
    operator_parallel(
        operator_loop('A Body', 'A Condition', 'A Exit'),
        operator_loop('B Body', 'B Condition', 'B Exit'),
        operator_loop('C Body', 'C Condition', 'C Exit')
    )
""")
```

## Example
**Multi-Stream Processing**:
1. Process orders (loop A)
2. Process shipments (loop B)
3. Process payments (loop C)

All three loops run concurrently, interleaving iterations.

```python
processing_model = parse_powl_model_string("""
    operator_parallel(
        operator_loop('Process Order', 'More Orders?', 'Orders Complete'),
        operator_loop('Process Shipment', 'More Shipments?', 'Shipments Complete'),
        operator_loop('Process Payment', 'More Payments?', 'Payments Complete')
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Multiple loops needed concurrently
- Loops are independent
- Interleaved iterations acceptable

❌ Don't use when:
- Single loop (use Structured Loop)
- Loops must execute sequentially (use Sequence)
- Loops have dependencies

## Related Patterns
- [Structured Loop](./structured-loop.md) - Single loop
- [Arbitrary Cycles](./arbitrary-cycles.md) - Unstructured cycles
- [Interleaved Parallel Routing](./interleaved-parallel-routing.md) - Concurrent activities

## Implementation Notes

### POWL v2
- Multiple loop operators in parallel
- Each loop independent
- Iterations can interleave

### BPMN 2.0
- **Multiple Subprocesses** with loop characteristics
- All subprocesses active concurrently
- Iterations interleave

### Petri Nets
- **Multiple cycles** in net
- All cycles active
- Transitions fire in any order

### YAWL
- **Multiple decomposition loops**
- All loops active
- Interleaved iterations

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ⚠️ Requires Care | Ensure no deadlocks |
| **Efficiency** | ✅ High | Concurrent loops |
| **Maintainability** | ⚠️ Medium | Complex logic |
| **Flexibility** | ✅ High | Easy to add loops |
| **Scalability** | ✅ High | Many loops |

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_interleaved_looping():
    # Create three loops
    loop_a = Operator(Operator.LOOP)
    loop_a.set_do(POWL("Process Order"))
    loop_a.set_exit(POWL("More Orders?"))
    loop_a.set_redo(POWL("Process Order"))
    loop_a.set_exit_success(POWL("Orders Complete"))

    loop_b = Operator(Operator.LOOP)
    loop_b.set_do(POWL("Process Shipment"))
    loop_b.set_exit(POWL("More Shipments?"))
    loop_b.set_redo(POWL("Process Shipment"))
    loop_b.set_exit_success(POWL("Shipments Complete"))

    loop_c = Operator(Operator.LOOP)
    loop_c.set_do(POWL("Process Payment"))
    loop_c.set_exit(POWL("More Payments?"))
    loop_c.set_redo(POWL("Process Payment"))
    loop_c.set_exit_success(POWL("Payments Complete"))

    # Parallel loops
    parallel = Operator(Operator.PARALLEL)
    parallel.add_child(loop_a)
    parallel.add_child(loop_b)
    parallel.add_child(loop_c)

    return parallel

# Visualize
model = create_interleaved_looping()
pm4py.view_powl(model, format='png')
```

## Real-World Examples

1. **Data Pipeline**: Multiple streams processing concurrently
2. **Monitoring**: Multiple monitoring loops
3. **Batch Processing**: Multiple batch jobs

## References
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #23 of 43**
