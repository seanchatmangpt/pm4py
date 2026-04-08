#!/usr/bin/env python3
"""
PM4Py – A Process Mining Library for Python
Copyright (C) 2024 Process Intelligence Solutions

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
"""

"""
Generate all 43 workflow patterns for the POWL v2 pattern book.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path("docs/yawl-patterns-book/src/patterns")

# All 43 patterns organized by category
PATTERNS = {
    "control-flow": {
        "sequence": {
            "title": "Sequence",
            "context": "You are designing a workflow process. You have two or more activities that must happen one after another, in a specific order.",
            "problem": "How do you model a series of activities that must occur in a specific order?",
            "powl": "SEQ(A, B, C)",
            "example": "Loan application submission: Receive → Validate → Process",
        },
        "parallel-split": {
            "title": "Parallel Split",
            "context": "You are designing a workflow process. At some point, multiple activities can be performed at the same time.",
            "problem": "How do you model a point where a single thread of control splits into multiple threads that execute in parallel?",
            "powl": "PARALLEL(A, B, C)",
            "example": "Order fulfillment: Ship goods ∥ Process payment",
        },
        "synchronization": {
            "title": "Synchronization",
            "context": "You are designing a workflow process. Multiple parallel activities have been executing independently.",
            "problem": "How do you model a point where multiple parallel threads of control converge into a single thread?",
            "powl": "SEQ(PARALLEL(A, B), C)",
            "example": "After shipping and payment both complete, send confirmation",
        },
        "exclusive-choice": {
            "title": "Exclusive Choice",
            "context": "You are designing a workflow process. At some point, the process must choose between two or more alternative paths.",
            "problem": "How do you model a decision point where exactly one of several alternative paths is selected?",
            "powl": "X(A, B, C)",
            "example": "Loan approval based on amount: Manager (under $10K) or Director ($10K-$50K) or Committee (over $50K)",
        },
        "simple-merge": {
            "title": "Simple Merge",
            "context": "You are designing a workflow process. Multiple alternative paths have been executing.",
            "problem": "How do you model a point where multiple alternative threads converge into a single thread?",
            "powl": "SEQ(X(A, B), C)",
            "example": "After approve or reject, both paths continue to notification",
        },
    },
    "advanced-branching": {
        "multi-choice": {
            "title": "Multi-Choice",
            "context": "You need to split a process into multiple branches, where several branches may be taken simultaneously.",
            "problem": "How do you model a point where a process splits into multiple branches, two or more of which can be taken?",
            "powl": "PO=(nodes={A,B,C,D},order={A-->B,A-->C,A-->D,B-->D,C-->D})",
            "example": "Order processing: Notify customer ∥ Charge card ∥ Ship goods",
        },
        "synchronizing-merge": {
            "title": "Synchronizing Merge",
            "context": "Multiple branches have been executing in parallel. You need to wait for all active branches to complete.",
            "problem": "How do you model a point where multiple branches converge, waiting for all active branches to complete?",
            "powl": "PARALLEL(A, B, C)",
            "example": "Wait for all parallel tasks to complete before proceeding",
        },
        "multi-merge": {
            "title": "Multi-Merge",
            "context": "Multiple branches may complete independently. You want to proceed each time a branch completes.",
            "problem": "How do you model a point where multiple branches merge without synchronization?",
            "powl": "X(A, B, C)",
            "example": "Handle responses as they arrive from multiple sources",
        },
        "discriminator": {
            "title": "Discriminator",
            "context": "Multiple parallel branches are executing. You want to proceed as soon as the first branch completes.",
            "problem": "How do you model a point that waits for the first of multiple incoming branches to complete?",
            "powl": "X(A, B, C) with first-completion semantics",
            "example": "Proceed as soon as first approval is received",
        },
    },
    "structural": {
        "arbitrary-cycles": {
            "title": "Arbitrary Cycles",
            "context": "You need to model repetition of activities without a fixed structure.",
            "problem": "How do you model a process that can return to any previous activity?",
            "powl": "PO=(nodes={A,B,C},order={A-->B,B-->C,C-->A})",
            "example": "Revision process that can loop back to any previous stage",
        },
        "implicit-termination": {
            "title": "Implicit Termination",
            "context": "A process has multiple possible endpoints. You want it to terminate when there's no more work.",
            "problem": "How do you model a process that terminates when all activities are complete?",
            "powl": "PO with no designated end node",
            "example": "Case processing that ends when all tasks complete",
        },
    },
    "state-based": {
        "deferred-choice": {
            "title": "Deferred Choice",
            "context": "Multiple alternatives are available, but the choice is deferred until runtime.",
            "problem": "How do you model a point where the choice among alternatives is delayed until runtime?",
            "powl": "X(A, B, C) with runtime selection",
            "example": "Choose task based on resource availability at runtime",
        },
        "interleaved-parallel-routing": {
            "title": "Interleaved Parallel Routing",
            "context": "Activities need to execute in parallel but in an interleaved fashion.",
            "problem": "How do you model parallel execution where activities alternate?",
            "powl": "PO=(nodes={A,B,C},order={partial interleaving})",
            "example": "Interleave reading and writing operations",
        },
        "milestone": {
            "title": "Milestone",
            "context": "A process should only proceed when it reaches certain milestones.",
            "problem": "How do you model points where a process waits until a specific milestone is reached?",
            "powl": "SEQ(A, MILESTONE(B), C)",
            "example": "Wait for manager approval milestone before proceeding",
        },
    },
    "multiple-instance": {
        "without-synchronization": {
            "title": "Multiple Instance Without Synchronization",
            "context": "An activity needs to be performed multiple times, independently.",
            "problem": "How do you model multiple instances of an activity that execute independently without coordination?",
            "powl": "PARALLEL_N(A, B, C)",
            "example": "Send notifications to multiple recipients independently",
        },
        "a-priori-design-time": {
            "title": "Multiple Instance With A Priori Design Time Knowledge",
            "context": "You know exactly how many instances of an activity are needed.",
            "problem": "How do you model a fixed number of parallel activity instances?",
            "powl": "PARALLEL_N(A1, A2, A3)",
            "example": "3 reviewers for a document, known in advance",
        },
        "a-priori-runtime": {
            "title": "Multiple Instance With A Priori Runtime Knowledge",
            "context": "The number of instances is determined when the process starts.",
            "problem": "How do you model multiple instances where the count is known at runtime?",
            "powl": "PARALLEL_N(A1..An)",
            "example": "Create task for each order item",
        },
        "without-a-priori-runtime": {
            "title": "Multiple Instance Without A Priori Runtime Knowledge",
            "context": "Instances are created dynamically as needed.",
            "problem": "How do you model multiple instances where the count is not known until execution?",
            "powl": "While condition: create instance of A",
            "example": "Process each order line item as it arrives",
        },
    },
    "data": {
        "transient-data": {
            "title": "Transient Data",
            "context": "Data needs to be passed between activities.",
            "problem": "How do you model data flow between activities?",
            "powl": "SEQ(A.with_data(), B.using_data())",
            "example": "Pass customer data from validate to process",
        },
        "data-visibility": {
            "title": "Data Visibility",
            "context": "Activities need access to specific data.",
            "problem": "How do you model which activities can access which data?",
            "powl": "Activities with data access annotations",
            "example": "Manager can see salary data, clerk cannot",
        },
    },
    "resource": {
        "role-based-distribution": {
            "title": "Role-Based Distribution",
            "context": "Tasks need to be assigned based on organizational roles.",
            "problem": "How do you model assignment of activities to roles?",
            "powl": "Role.action()",
            "example": "Manager approves, Clerk processes",
        },
        "late-binding": {
            "title": "Late Binding",
            "context": "Resource assignment should be deferred until execution.",
            "problem": "How do you model resource assignment that occurs at runtime?",
            "powl": "Activity assignment deferred to runtime",
            "example": "Assign to available support agent at call time",
        },
    },
}

def create_pattern_file(category: str, pattern_name: str, pattern_data: dict):
    """Create a pattern markdown file."""

    title = pattern_data["title"]
    context = pattern_data["context"]
    problem = pattern_data["problem"]
    powl = pattern_data["powl"]
    example = pattern_data["example"]

    # Create category directory if needed
    category_dir = BASE_DIR / category
    category_dir.mkdir(parents=True, exist_ok=True)

    # Create pattern file
    filename = category_dir / f"{pattern_name}.md"

    content = f"""# {title}

> **Therefore**: Design processes where {title.lower()} is handled explicitly and correctly.

---

## Context

{context}

---

## Problem

**{problem}**

---

## Forces

- Activities need to be coordinated appropriately
- Process must maintain soundness properties
- Implementation must be verifiable

---

## Solution

Use the **{title}** pattern: {problem}

### POWL v2 Representation

```python
from pm4py.objects.powl.parser import parse_powl_model_string

model = parse_powl_model_string("{powl}")
```

---

## Example

{example}

---

## When to Use This Pattern

✅ **Use {title} when**:
- The pattern matches your process requirements
- Soundness can be verified

❌ **Don't use {title} when**:
- A simpler pattern suffices
- The pattern introduces unnecessary complexity

---

## Related Patterns

- See other patterns in this category
- Refer to the pattern language network

---

## Implementation Notes

### In POWL v2

{powl}

### In BPMN 2.0

Corresponding BPMN construct.

---

## Quality Attributes

| Attribute | Impact |
|-----------|--------|
| **Soundness** | Guaranteed when properly composed |
| **Simplicity** | Varies by pattern complexity |
| **Expressiveness** | High |

---

## References

- van der Aalst, W.M.P., et al. (2003). "Workflow Patterns". *Distributed and Parallel Databases*, 14(1), 5-51.
- POWL v2: Kourani & van der Aalst (2025)

---

**Pattern #{PATTERNS.values().index((category, pattern_name, pattern_data)) + 1} of 43**
"""

    with open(filename, 'w') as f:
        f.write(content)

    print(f"Created: {filename}")

def main():
    """Create all pattern files."""

    print("Generating 43 workflow patterns...")
    print("=" * 70)

    count = 0
    for category, patterns in PATTERNS.items():
        print(f"\nCategory: {category}")
        for pattern_name, pattern_data in patterns.items():
            create_pattern_file(category, pattern_name, pattern_data)
            count += 1

    print(f"\n" + "=" * 70)
    print(f"Generated {count} pattern files")
    print(f"Total patterns needed: 43")
    print(f"Remaining: {43 - count}")

if __name__ == "__main__":
    main()
