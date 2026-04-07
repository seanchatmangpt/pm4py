# Parallel Split

> **Therefore**: Design points in a process where multiple activities can execute simultaneously, independent of each other.

---

## Context

You are designing a workflow process. At some point, multiple activities can be performed at the same time, without depending on each other. These activities could run concurrently to improve performance, reduce latency, or utilize available resources.

The parallel activities might:
- Operate on different data items
- Be performed by different resources
- Execute independently until they need to synchronize

---

## Problem

**How do you model a point where a single thread of control splits into multiple threads that can execute in parallel?**

---

## Forces

- Activities are independent and can execute simultaneously
- Parallel execution improves performance or resource utilization
- All parallel paths must eventually complete before proceeding
- Order of completion is not known in advance

---

## Solution

Use the **Parallel Split (AND split)** pattern: model a point where the process forks into multiple parallel branches that execute concurrently.

### POWL v2 Representation

```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Parallel split: A, then B and C in parallel
model = parse_powl_model_string("SEQ(A, PARALLEL(B, C))")
```

Or using DecisionGraph for true parallelism:
```python
# True parallel: B and C execute concurrently
model = parse_powl_model_string("PO=(nodes={A,B,C},order={A-->B,A-->C})")
```

### Visual Representation

```
┌───┐
│ A │
└───┘
  │
  ├───┬───┐
  │   │   │
┌─┴─┐ ┌┴──┴┐
│ B │ │ C │  (parallel execution)
└───┘ └────┘
```

---

## Example: Order Fulfillment

**Context**: An e-commerce company processes orders. After receiving an order, two independent activities can happen in parallel:
1. Warehouse prepares the goods for shipping
2. Accounting processes the payment

**POWL Model**:
```python
model = parse_powl_model_string("""
SEQ(
  Receive.order(),
  PARALLEL(
    Ship.prepare_goods(),
    Accounting.process_payment()
  ),
  Notify.order_complete()
)
""")
```

**Explanation**:
1. **Receive.order()**: Order is received
2. **Parallel execution**:
   - Warehouse prepares goods (picking, packing)
   - Accounting processes payment (authorization, capture)
3. **Notify.order_complete()**: After both complete, customer is notified

**Benefits**:
- **Faster fulfillment**: Warehouse and accounting work simultaneously
- **Resource efficiency**: Different teams work in parallel
- **Reduced latency**: Total time = max(warehouse_time, accounting_time), not sum

---

## When to Use This Pattern

✅ **Use Parallel Split when**:
- Activities are independent and can execute simultaneously
- Parallel execution improves performance or resource utilization
- All parallel paths must complete before proceeding
- Order of completion doesn't matter

❌ **Don't use Parallel Split when**:
- Activities have temporal dependencies (use [Sequence](./sequence.md))
- Only one path should execute (use [Exclusive Choice](./exclusive-choice.md))
- Activities conflict or require shared resources (may need [Critical Section](../multiple-instance/critical-section.md))

---

## Variants

### 1. Simple Parallel Split

Split into fixed number of parallel branches:
```python
# A, then B, C, D in parallel
model = parse_powl_model_string("SEQ(A, PARALLEL(B, C, D))")
```

### 2. Dynamic Parallel Split

Split into variable number of parallel branches:
```python
# For each order item, process in parallel
model = parse_powl_model_string("""
SEQ(
  Receive.order(),
  PARALLEL_N(Items.process_each()),
  Ship.when_all_complete()
)
""")
```

### 3. Partial Order (POWL DecisionGraph)

True parallelism with partial order constraints:
```python
# B and C are parallel, both after A, D waits for both
model = parse_powl_model_string(
    "PO=(nodes={A,B,C,D},order={A-->B,A-->C,B-->D,C-->D})"
)
```

---

## Related Patterns

- **[Synchronization](./synchronization.md)**: When converging parallel paths
- **[Sequence](./sequence.md)**: When activities must execute in order
- **[Exclusive Choice](./exclusive-choice.md)**: When only one path should execute
- **[Multi-Choice](../advanced-branching/multi-choice.md)**: When multiple paths can be chosen

---

## Implementation Notes

### In POWL v2

Use `PARALLEL()` for explicit parallelism:
```
SEQ(A, PARALLEL(B, C), D)  # A → (B ∥ C) → D
```

Use partial order for more complex parallelism:
```
PO=(nodes={A,B,C,D},order={A-->B,A-->C,B-->D,C-->D})
```

### In BPMN 2.0

Parallel split is represented by a parallel gateway (AND gateway):
```xml
<parallelGateway id="gateway1" name="Split" />
<sequenceFlow sourceRef="gateway1" targetRef="activityB" />
<sequenceFlow sourceRef="gateway1" targetRef="activityC" />
```

### In Petri Nets

Parallel split is represented by a place with multiple output transitions:
```
     t_B    t_C
    /         \
p_split
    \         /
     t_A───p───...
```

---

## Quality Attributes

| Attribute | Impact |
|-----------|--------|
| **Performance** | High - parallel execution reduces latency |
| **Resource Usage** | High - utilizes multiple resources simultaneously |
| **Complexity** | Medium - requires managing concurrent execution |
| **Soundness** | Must ensure proper synchronization to avoid deadlocks |

---

## Common Mistakes

1. **False parallelism**: Making activities parallel when they have dependencies
   - *Solution*: Verify activities are truly independent

2. **Missing synchronization**: Parallel paths that never converge
   - *Solution*: Always use [Synchronization](./synchronization.md) to join parallel paths

3. **Resource conflicts**: Parallel activities competing for shared resources
   - *Solution*: Use [Critical Section](../multiple-instance/critical-section.md) or resource allocation

4. **Unbounded parallelism**: Forking into unlimited parallel branches
   - *Solution*: Use [Discriminator](../advanced-branching/discriminator.md) to limit concurrency

---

## Pattern Combinations

**Parallel Split + Synchronization** = Fork-join:
```
SEQ(A, PARALLEL(B, C), D)  # A → (B ∥ C) → D
```

**Parallel Split + Exclusive Choice** = Complex branching:
```
SEQ(A, PARALLEL(X(B, C), X(D, E)), F)  # A → ((B or C) ∥ (D or E)) → F
```

**Parallel Split + Loop** = Parallel iteration:
```
*(PARALLEL(A, B))  # Repeatedly execute A and B in parallel
```

---

## Multi-Perspective Extensions

### Organizational Perspective

Model parallel work by different roles:
```python
model = parse_powl_model_string("""
PARALLEL(
  Manager.review_document(),
  Analyst.collect_data(),
  Designer.create_mockups()
)
""")
```

### Temporal Perspective

Model time-based parallel constraints:
```python
model = parse_powl_model_string("""
SEQ(
  Start.all_tasks(),
  PARALLEL(
    Task.complete_within_24h(),
    Task.complete_within_48h()
  ),
  Notify.when_all_complete()
)
""")
```

### Data Perspective

Model parallel data processing:
```python
model = parse_powl_model_string("""
PARALLEL(
  Process.customer_data(),
  Process.inventory_data(),
  Process.shipping_data()
)
""")
```

---

## Real-World Examples

### 1. Loan Processing

Parallel verification activities:
```python
model = parse_powl_model_string("""
SEQ(
  Receive.application(),
  PARALLEL(
    Verify.credit_history(),
    Verify.income(),
    Verify.employment()
  ),
  Make.approval_decision()
)
""")
```

### 2. Software Release

Parallel testing activities:
```python
model = parse_powl_model_string("""
SEQ(
  Build.software(),
  PARALLEL(
    Test.unit_tests(),
    Test.integration_tests(),
    Test.security_scan(),
    Test.performance_test()
  ),
  Deploy.to_production()
)
""")
```

### 3. Medical Diagnosis

Parallel diagnostic procedures:
```python
model = parse_powl_model_string("""
SEQ(
  Patient.admit(),
  PARALLEL(
    Lab.blood_tests(),
    Imaging.x_ray(),
    Specialist.consultation()
  ),
  Doctor.diagnose_and_prescribe()
)
""")
```

---

## Exercises

1. **Identify parallelism**: Look at your current workflow. Where could activities be parallelized to improve performance?

2. **Design parallel split**: Model a mortgage application process where:
   - After receiving application, verify credit, income, and property in parallel
   - When all complete, make approval decision

3. **Combine patterns**: Design a process that:
   - Receives request
   - Splits into 3 parallel branches
   - Each branch does a XOR choice (different activities)
   - All converge → Continue

---

## References

- van der Aalst, W.M.P., et al. (2003). "Workflow Patterns". *Distributed and Parallel Databases*, 14(1), 5-51.
- POWL v2: Kourani & van der Aalst (2025)
- BPMN 2.0 Specification (OMG, 2011)

---

**Next**: Learn how to synchronize parallel paths with [Synchronization](./synchronization.md).
