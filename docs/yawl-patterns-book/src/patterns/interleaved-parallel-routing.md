# Interleaved Parallel Routing

> **Therefore**: Execute multiple paths concurrently but in any order.

---

## Context
You have multiple activities that need to be executed, but their order doesn't matter—they can interleave in any way.

## Problem
**How do you execute multiple activities concurrently without enforcing a specific order?**

Parallel split (Pattern 3) executes activities truly simultaneously. Interleaved parallel routing allows activities to execute in any interleaved order—like A, B, A, C, B, C—while ensuring all activities complete.

## Solution
Execute multiple paths concurrently where the execution order is unspecified—activities can interleave in any pattern, but all must complete.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Interleaved parallel: order doesn't matter
model = parse_powl_model_string("""
    operator_parallel(
        'A',
        'B',
        'C'
    )
""")

# Execution could be: A → B → C, or B → A → C, or A → B → A → C...
# All must complete, but order is unspecified
```

## Example
**Document Review**: Three reviewers read a document:
1. Reviewer A
2. Reviewer B
3. Reviewer C

They can review in any order, but all must complete before proceeding.

```python
review_model = parse_powl_model_string("""
    sequence(
        'Distribute Document',
        operator_parallel(
            'Reviewer A',
            'Reviewer B',
            'Reviewer C'
        ),
        'Collect All Reviews'
    )
""")
```

## When to Use This Pattern
✅ Use when:
- Multiple independent activities must all complete
- Order of execution doesn't matter
- Activities can run truly concurrently or sequentially

❌ Don't use when:
- Order matters (use Sequence)
- Only one path needed (use Exclusive Choice)
- Activities must execute simultaneously (use Parallel Split)

## Related Patterns
- [Parallel Split](./parallel-split.md) - True simultaneous execution
- [Arbitrary Interleaving](./arbitrary-interleaving.md) - More flexible interleaving
- [Multi-Choice](./multi-choice.md) - Conditional paths

## Implementation Notes

### POWL v2
- Use `operator_parallel()` for interleaved execution
- No order constraints between parallel branches
- All branches must complete before parent completes

### BPMN 2.0
- Use **Parallel Gateway** split/merge
- All outgoing flows are enabled simultaneously
- Order of execution is unspecified

### Petri Nets
- **Transition** with multiple output places
- Tokens flow to all places
- No order constraint between places

### YAWL
- Use **AND-split** for divergence
- All tasks enabled simultaneously
- Order of execution is unspecified

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ✅ Guaranteed | No deadlock if activities independent |
| **Efficiency** | ✅ Excellent | Maximum concurrency |
| **Maintainability** | ✅ High | Clear independence |
| **Flexibility** | ✅ High | Easy to add/remove activities |
| **Scalability** | ✅ High | Many activities handled efficiently |

## Common Pitfalls

1. **Hidden Dependencies**: Activities assumed independent but aren't
2. **Resource Contention**: Activities compete for same resources
3. **Order Assumptions**: Downstream code assumes specific order

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_interleaved_parallel():
    # Create independent activities
    reviewer_a = POWL("Reviewer A")
    reviewer_b = POWL("Reviewer B")
    reviewer_c = POWL("Reviewer C")
    collect = POWL("Collect All Reviews")

    # Create interleaved parallel execution
    parallel = Operator(Operator.PARALLEL)
    parallel.add_child(reviewer_a)
    parallel.add_child(reviewer_b)
    parallel.add_child(reviewer_c)

    # Sequence: distribute → parallel → collect
    main = Operator(Operator.SEQUENCE)
    main.add_child(POWL("Distribute Document"))
    main.add_child(parallel)
    main.add_child(collect)

    return main

# Visualize
model = create_interleaved_parallel()
pm4py.view_powl(model, format='png')

# Note: Order of reviewer execution is unspecified
# All must complete before "Collect All Reviews"
```

## Interleaving vs. True Parallel

```python
# True parallel: all activities start simultaneously
true_parallel = Operator(Operator.PARALLEL)
true_parallel.add_child(POWL("A"))
true_parallel.add_child(POWL("B"))
true_parallel.add_child(POWL("C"))

# Interleaved: activities can execute in any order
# Could be: A → B → C, or B → A → C, or A → B → A → C...
# Both use POWL operator_parallel() - difference is in execution engine
```

## Verification Checklist

- [ ] Activities are truly independent (no shared state)
- [ ] No hidden dependencies between activities
- [ ] Downstream activities handle any order
- [ ] Resource conflicts are resolved

## Real-World Examples

1. **Code Review**: Multiple reviewers review same PR (any order)
2. **Data Validation**: Multiple validation rules run (any order)
3. **Background Jobs**: Multiple independent jobs run (any order)

## References
- van der Aalst, W. M. P., ter Hofstede, A. H. M., Kiepuszewski, B., & Barros, A. P. (2003). "Workflow Patterns". *Distributed and Parallel Databases*, 14(3), 5-51.
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #13 of 43**
