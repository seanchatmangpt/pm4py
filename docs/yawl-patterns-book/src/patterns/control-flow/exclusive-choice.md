# Exclusive Choice

> **Therefore**: Design decision points where exactly one of several alternative paths is chosen, based on data or conditions.

---

## Context

You are designing a workflow process. At some point, the process must choose between two or more alternative paths. Only one of these paths should be executed—the choice is mutually exclusive.

The choice may depend on:
- Data values (e.g., loan amount)
- External events (e.g., approval received)
- User decisions (e.g., customer accepts offer)
- System conditions (e.g., inventory available)

---

## Problem

**How do you model a decision point where exactly one of several alternative paths is selected and executed, based on runtime conditions?**

---

## Forces

- Multiple alternative paths exist, but only one should be taken
- The choice depends on data, events, or conditions known at runtime
- The paths are mutually exclusive (executing one precludes others)
- After the chosen path completes, the process continues

---

## Solution

Use the **Exclusive Choice (XOR split)** pattern: model a decision point where exactly one of several alternative branches is selected and executed.

### POWL v2 Representation

```python
from pm4py.objects.powl.parser import parse_powl_model_string

# XOR split: choose one of A, B, or C based on condition
model = parse_powl_model_string("X(A, B, C)")
```

Or in POWL string notation:
```
X(A, B, C)
```

### Visual Representation

```
         ┌───┐
         │ A │
      /─┴───┴─\
      │   X   │
      \─┬───┬─/
         │   │
        ┌┴┐ ┌┴┐
        │B│ │C│
        └┘ └┘
```

---

## Example: Loan Approval

**Context**: A bank processes loan applications. The approval decision depends on the loan amount:
- Loans under $10K: Manager approves
- Loans $10K-$50K: Director approves
- Loans over $50K: Committee approves

**POWL Model**:
```python
model = parse_powl_model_string("""
X(
  Manager.approve_under_10k(),
  Director.approve_10k_to_50k(),
  Committee.approve_over_50k()
)
""")
```

**Explanation**:
The system evaluates the loan amount and routes to exactly one approval path:
- Small loans → Manager (fast, local decision)
- Medium loans → Director (higher authority)
- Large loans → Committee (collective decision, slower)

**Multi-Perspective Representation**:
- **Control flow**: XOR choice based on loan amount
- **Organizational**: Different roles for different thresholds
- **Data**: Decision based on `loan_amount` attribute

---

## When to Use This Pattern

✅ **Use Exclusive Choice when**:
- Exactly one of several alternatives must be chosen
- The choice depends on data or conditions
- Paths are mutually exclusive
- Only one path should be executed

❌ **Don't use Exclusive Choice when**:
- Multiple paths should execute in parallel (use [Parallel Split](./parallel-split.md))
- The choice is deferred until runtime (use [Deferred Choice](../advanced-branching/deferred-choice.md))
- Multiple paths can be taken (use [Multi-Choice](../advanced-branching/multi-choice.md))

---

## Variants

### 1. Data-Based Choice

Choice based on data attributes:
```python
# If loan_amount < 10000: A, elif < 50000: B, else: C
model = parse_powl_model_string("X(A, B, C)")
# Condition encoded in activity labels:
# A = "Process if amount < 10k"
# B = "Process if amount 10k-50k"
# C = "Process if amount > 50k"
```

### 2. Event-Based Choice

Choice based on which event occurs first:
```python
# Timeout or approval
model = parse_powl_model_string("X(Timer.timeout(), Manager.approve())")
```

### 3. Role-Based Choice

Choice based on organizational role:
```python
# Different handlers based on customer tier
model = parse_powl_model_string("""
X(
  Platinum.handle(),
  Gold.handle(),
  Silver.handle(),
  Standard.handle()
)
""")
```

---

## Related Patterns

- **[Parallel Split](./parallel-split.md)**: When all paths should execute in parallel
- **[Simple Merge](./simple-merge.md)**: When converging exclusive paths
- **[Multi-Choice](../advanced-branching/multi-choice.md)**: When multiple paths can be chosen
- **[Deferred Choice](../advanced-branching/deferred-choice.md)**: When choice is deferred to runtime

---

## Implementation Notes

### In POWL v2

The XOR operator `X()` represents exclusive choice. Each child is an alternative:
```
X(A, B, C)  # Choose one of A, B, or C
```

For conditional routing, encode conditions in activity labels:
```
X(
  If.approved_then_process(),
  If.rejected_then_notify(),
  If.pending_then_wait()
)
```

### In BPMN 2.0

Exclusive choice is represented by an exclusive gateway (XOR gateway):
```xml
<exclusiveGateway id="gateway1" name="Approval Decision" />
<sequenceFlow sourceRef="gateway1" targetRef="approve" />
<sequenceFlow sourceRef="gateway1" targetRef="reject" />
<conditionExpression>${approved == true}</conditionExpression>
```

### In Petri Nets

Exclusive choice is represented by a place with multiple output transitions, where exactly one fires:
```
      t_A
     /
p_decision
     \
      t_B
```

---

## Quality Attributes

| Attribute | Impact |
|-----------|--------|
| **Flexibility** | High - supports multiple alternatives |
| **Determinism** | High - exactly one path chosen |
| **Performance** | Medium - only one path executes |
| **Maintainability** | Medium - requires managing multiple paths |

---

## Common Mistakes

1. **Missing conditions**: XOR choices without clear decision criteria
   - *Solution*: Document the condition for each branch

2. **Overlapping conditions**: Multiple branches could be true
   - *Solution*: Ensure conditions are mutually exclusive

3. **Incomplete alternatives**: Missing edge cases
   - *Solution*: Include an "else" or "default" branch

4. **Deep nesting**: Many levels of XOR choices
   - *Solution*: Flatten into a single XOR with more options

---

## Pattern Combinations

**Exclusive Choice + Simple Merge** = Decision and converge:
```
X(A, B, C) → merge → D  # Choose one of A/B/C, then continue to D
```

**Exclusive Choice + Loop** = Retry with decision:
```
X(A, *(B, C))  # A, or (B → C) repeated
```

**Exclusive Choice + Sequence** = Conditional workflow:
```
SEQ(A, X(B, C), D)  # A → (B or C) → D
```

---

## Multi-Perspective Extensions

### Organizational Perspective

Model role-based routing:
```python
model = parse_powl_model_string("""
X(
  Manager.approve_small_loans(),
  Director.approve_medium_loans(),
  Committee.approve_large_loans()
)
""")
```

### Temporal Perspective

Model time-based choices:
```python
model = parse_powl_model_string("""
X(
  Process.within_24h(),
  Escalate.after_timeout()
)
""")
```

### Data Perspective

Model data-driven choices:
```python
model = parse_powl_model_string("""
X(
  If.high_value_then_review(),
  If.medium_value_then_auto_approve(),
  If.low_value_then_fast_track()
)
""")
```

---

## Exercises

1. **Identify XOR choices**: Look at your current workflow. Where are there implicit decision points that should be explicit XOR choices?

2. **Design a choice**: Model a customer support process:
   - If customer is platinum → Premium support
   - If customer is gold → Standard support
   - If customer is silver → Basic support

3. **Combine patterns**: Design a process that:
   - Receives application
   - Choice: Validate if complete, or Return if incomplete
   - If validated → Choice: Approve or Reject
   - Converge → Send notification

---

## References

- van der Aalst, W.M.P., et al. (2003). "Workflow Patterns". *Distributed and Parallel Databases*, 14(1), 5-51.
- Russell, N., et al. (2006). "Workflow Control-Flow Patterns". *BPM Center Report*

---

**Next**: Learn how to execute multiple paths in parallel with [Parallel Split](./parallel-split.md).
