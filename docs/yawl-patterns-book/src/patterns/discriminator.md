# Discriminator

> **Therefore**: Proceed after the first N paths complete, ignoring the rest.

---

## Context
You have multiple concurrent paths, but you only need to wait for **some** of them to complete before proceeding—not all.

## Problem
**How do you proceed as soon as a specific number of paths complete?**

Synchronization waits for ALL paths (slowest branch determines pace). Discriminator waits for **N of M** paths—useful when you have redundancy or only need partial results.

## Solution
Merge multiple paths, proceeding as soon as **N** paths complete (where N ≤ M total paths). Remaining paths are cancelled or ignored.

### POWL v2 Representation
```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Discriminator: wait for 2 of 3 paths
model = parse_powl_model_string("""
    sequence(
        operator_parallel(
            'A',
            'B',
            'C'
        ),
        'First Two Completed',  # Proceeds after 2 of 3 complete
        'Continue'
    )
""")

# If A and B complete first → proceed (C ignored or cancelled)
# If B and C complete first → proceed (A ignored or cancelled)
```

## Example
**Quote Comparison Service**: Get quotes from multiple vendors:
1. Vendor A (response time: ~2 seconds)
2. Vendor B (response time: ~3 seconds)
3. Vendor C (response time: ~5 seconds)

Proceed with best quote after receiving **2 of 3** responses:

```python
quote_model = parse_powl_model_string("""
    sequence(
        operator_parallel(
            'Request Quote A',
            'Request Quote B',
            'Request Quote C'
        ),
        'Wait for 2 Responses',  # Discriminator: wait for 2 of 3
        'Select Best Quote',
        'Present to Customer'
    )
""")
```

## When to Use This Pattern
✅ Use when:
- You have redundant paths and only need some to succeed
- Partial results are sufficient
- You want to avoid waiting for slowest path

❌ Don't use when:
- All paths must complete (use Synchronization)
- Only one path executes (use Simple Merge)
- You need results from all paths

## Related Patterns
- [Synchronization](./synchronization.md) - Waits for ALL paths
- [Multi-Merge](./multi-merge.md) - Proceeds on ANY path
- [Synchronizing Merge](./synchronizing-merge.md) - Waits for activated paths
- [Deferred Choice](./deferred-choice.md) - Choice based on first completion

## Implementation Notes

### POWL v2
- Discriminator requires **custom logic** outside POWL core
- Implement via monitoring parallel completion count
- When N paths complete, trigger next activity; cancel others

### BPMN 2.0
- Use **Event-Based Gateway** with multiple **Timer Events**
- Or use **Complex Gateway** with custom expression
- No native discriminator—requires extension

### Petri Nets
- **Transition** with inhibitor arc
- Place counts completed paths; transition fires when count ≥ N
- Requires additional places for counting

### YAWL
- Use **OR-join** with custom predicate
- Predicate: "proceed when 2 of 3 branches complete"
- Requires YAWL extension for dynamic counting

## Quality Attributes

| Attribute | Rating | Notes |
|-----------|--------|-------|
| **Soundness** | ⚠️ Requires Care | Must handle cancelled paths properly |
| **Efficiency** | ✅ Excellent | No waiting for slowest paths |
| **Maintainability** | ⚠️ Medium | Custom logic for counting |
| **Flexibility** | ✅ High | Easy to adjust N of M threshold |
| **Scalability** | ✅ High | Many paths handled efficiently |

## Common Pitfalls

1. **Resource Leaks**: Cancelled paths may hold resources (connections, locks)
2. **Incomplete State**: Proceeding without all data may cause issues downstream
3. **Starvation**: Same paths always complete first, others never used

## Code Example

```python
import pm4py
from pm4py.objects.powl import POWL
from pm4py.objects.powl.operator import Operator

def create_discriminator():
    # Create parallel activities
    quote_a = POWL("Request Quote A")
    quote_b = POWL("Request Quote B")
    quote_c = POWL("Request Quote C")
    select_best = POWL("Select Best Quote")

    # Create parallel split
    parallel = Operator(Operator.PARALLEL)
    parallel.add_child(quote_a)
    parallel.add_child(quote_b)
    parallel.add_child(quote_c)

    # Sequence with discriminator (requires external monitoring)
    sequence = Operator(Operator.SEQUENCE)
    sequence.add_child(parallel)
    sequence.add_child(select_best)

    return sequence

# Visualize
model = create_discriminator()
pm4py.view_powl(model, format='png')

# Note: Discriminator logic must be implemented externally
# e.g., via process engine monitoring completion count
```

## Implementation with External Monitoring

```python
class DiscriminatorMonitor:
    def __init__(self, required_count=2):
        self.required_count = required_count
        self.completed_count = 0
        self.proceeded = False

    def on_complete(self, path_id):
        self.completed_count += 1
        if self.completed_count >= self.required_count and not self.proceeded:
            self.proceeded = True
            return "PROCEED"
        return "WAIT"

    def should_cancel(self, path_id):
        return self.proceeded

# Usage
monitor = DiscriminatorMonitor(required_count=2)
# When each parallel path completes:
# result = monitor.on_complete(path_id)
# if result == "PROCEED": trigger_next_activity()
# if monitor.should_cancel(path_id): cancel_remaining_paths()
```

## Verification Checklist

- [ ] Cancelled paths are properly cleaned up
- [ ] No resource leaks from incomplete paths
- [ ] Downstream activities handle partial data
- [ ] Threshold N is appropriate for business logic

## Real-World Examples

1. **API Redundancy**: Call 3 APIs, use first 2 responses
2. **Content Delivery**: Fetch from 5 CDNs, use first 3 that respond
3. **A/B Testing**: Run 4 variants, stop after 2 reach significance

## References
- van der Aalst, W. M. P., ter Hofstede, A. H. M., Kiepuszewski, B., & Barros, A. P. (2003). "Workflow Patterns". *Distributed and Parallel Databases*, 14(3), 5-51.
- Russell, N., ter Hofstede, A. H. M., van der Aalst, W. M. P., & Mulyar, N. (2006). "Workflow Control-Flow Patterns: A Revised View". *BPM Center Report BPM-06-22*.

---
**Pattern #9 of 43**
