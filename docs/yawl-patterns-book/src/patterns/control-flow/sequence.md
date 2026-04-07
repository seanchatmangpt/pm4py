# Sequence

> **Therefore**: Design processes as a sequence of activities, where each activity completes before the next begins.

---

## Context

You are designing a workflow process. You have two or more activities that must happen one after another, in a specific order. The second activity cannot start until the first has completed.

This is the most fundamental pattern in workflow design. Almost every process contains sequences of activities.

---

## Problem

**How do you model a series of activities that must occur in a specific order, where each activity depends on the completion of the previous one?**

---

## Forces

- Activities have temporal dependencies (A must happen before B)
- Parallel execution is not possible or desirable
- The order is fixed and known at design time
- There is no branching or conditional logic

---

## Solution

Use the **Sequence** pattern: model activities as a chain where the completion of one activity triggers the start of the next.

### POWL v2 Representation

```python
# Sequential process: A → B → C
from pm4py.objects.powl.parser import parse_powl_model_string

model = parse_powl_model_string("SEQ(A, B, C)")
```

Or in POWL string notation:
```
SEQ(A, B, C)
```

### Visual Representation

```
┌───┐    ┌───┐    ┌───┐
│ A │───▶│ B │───▶│ C │
└───┘    └───┘    └───┘
```

---

## Example: Loan Application Submission

**Context**: A customer submits a loan application. The bank must first receive the application, then validate it, then process it.

**POWL Model**:
```python
model = parse_powl_model_string(
    "SEQ(Receive.application(), Validate.application(), Process.application())"
)
```

**Explanation**:
1. **Receive.application()**: Bank receives the loan application
2. **Validate.application()**: Bank validates that all required information is present
3. **Process.application()**: Bank processes the validated application

Each activity depends on the previous one. You cannot validate an application that hasn't been received, and you cannot process an application that hasn't been validated.

---

## When to Use This Pattern

✅ **Use Sequence when**:
- Activities have a clear temporal dependency
- The order is fixed and known
- No parallelism is required
- Activities must complete before the next begins

❌ **Don't use Sequence when**:
- Activities can occur in parallel (use [Parallel Split](./parallel-split.md))
- The order depends on data or conditions (use [Exclusive Choice](./exclusive-choice.md))
- Activities can be skipped (use [Exclusive Choice](./exclusive-choice.md))

---

## Related Patterns

- **[Parallel Split](./parallel-split.md)**: When activities can occur in parallel
- **[Exclusive Choice](./exclusive-choice.md)**: When the next activity depends on a condition
- **[Simple Merge](./simple-merge.md)**: When multiple paths converge into one
- **[Multi-Choice](../advanced-branching/multi-choice.md)**: When splitting into multiple paths

---

## Implementation Notes

### In POWL v2

Sequence is implicit in the POWL string notation. When activities are listed in a sequence, they execute in order:

```
A, B, C  # Implies SEQ(A, B, C)
```

For nested sequences, use explicit SEQ:
```
SEQ(A, SEQ(B, C), D)  # A → (B → C) → D
```

### In BPMN 2.0

Sequence is represented by sequence flows between activities:
```xml
<sequenceFlow sourceRef="A" targetRef="B" />
<sequenceFlow sourceRef="B" targetRef="C" />
```

### In Petri Nets

Sequence is represented by a place between transitions:
```
t_A → p → t_B → p → t_C
```

---

## Quality Attributes

| Attribute | Impact |
|-----------|--------|
| **Simplicity** | High - easy to understand and verify |
| **Performance** | Low - sequential execution is slower than parallel |
| **Maintainability** | High - clear dependencies |
| **Soundness** | Guaranteed - sequences are always sound |

---

## Common Mistakes

1. **Over-sequencing**: Making activities sequential when they could be parallel
   - *Solution*: Review for opportunities to use [Parallel Split](./parallel-split.md)

2. **Hidden conditions**: Using sequence when the next activity depends on data
   - *Solution*: Use [Exclusive Choice](./exclusive-choice.md) to make conditions explicit

3. **Overly long sequences**: Chains of 10+ sequential activities
   - *Solution*: Break into subprocesses with meaningful intermediate states

---

## Pattern Combinations

**Sequence + Exclusive Choice** = Branching workflow:
```
SEQ(A, X(B, C), D)  # A → (B or C) → D
```

**Sequence + Parallel Split** = Fork-join workflow:
```
SEQ(A, PARALLEL(B, C), D)  # A → (B and C in parallel) → D
```

**Sequence + Loop** = Iterative workflow:
```
SEQ(A, *(B, C), D)  # A → (B → C) repeated → D
```

---

## Exercises

1. **Identify sequences**: Look at your current workflow. Where are activities unnecessarily sequential? Could any be parallelized?

2. **Design a sequence**: Model a simple order fulfillment process:
   - Receive order
   - Validate payment
   - Ship goods
   - Send confirmation

3. **Combine patterns**: Design a process that sequences into a choice:
   - Submit application
   - [If approved] → Process → Send approval letter
   - [If rejected] → Archive → Send rejection letter

---

## References

- van der Aalst, W.M.P., et al. (2003). "Workflow Patterns". *Distributed and Parallel Databases*, 14(1), 5-51.
- BPMN 2.0 Specification (OMG, 2011)
- POWL v2: Kourani & van der Aalst (2025)

---

**Next**: Explore how to split execution into parallel paths with [Parallel Split](./parallel-split.md).
