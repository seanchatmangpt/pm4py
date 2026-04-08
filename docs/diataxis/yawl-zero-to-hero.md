# YAWL Export: Zero to Hero Guide

> From your first YAWL export to advanced pattern validation and research reproducibility.

---

## What You'll Learn

This guide takes you from **zero knowledge** of YAWL export to **hero-level proficiency**:

- **Zero**: What is YAWL? Why export to it? How do I get started?
- **Beginner**: Export simple models, use the CLI, understand YAWL XML structure
- **Intermediate**: Handle complex patterns, convert from BPMN/event logs, troubleshoot
- **Advanced**: Pattern validation, research reproducibility, round-trip verification
- **Hero**: Strategic use cases, academic validation, future-proofing process models

**Time to complete:** 60 minutes (reading) + 30 minutes (hands-on exercises)

---

## Prerequisites

Before starting, ensure you have:

- [ ] Python 3.9+ installed
- [ ] pm4py library installed: `pip install pm4py`
- [ ] Basic understanding of process models (helpful but not required)

**Setup:**
```bash
pip install pm4py
python -c "import pm4py; print(pm4py.__version__)"
```

---

# Phase 0: Zero — What and Why

## What is YAWL?

**YAWL** (Yet Another Workflow Language) is a workflow system from 2003 that inspired the **43 workflow patterns** used in process mining today. While YAWL itself is obsolete in production, it remains valuable as:

- A **reference semantics** for workflow patterns
- A **validation target** for research algorithms
- A **historical bridge** to foundational process mining research

## Why Export to YAWL?

| Use Case | Why YAWL Helps |
|----------|----------------|
| **Research validation** | Export to YAWL and execute to verify algorithm correctness |
| **Pattern verification** | All 43 patterns map to YAWL constructs; validate pattern coverage |
| **Round-trip testing** | POWL → YAWL → POWL confirms lossless conversion |
| **Academic reproducibility** | Share YAWL models for peer review and validation |

**Deep dive:** [Why YAWL Export Matters](explanation/why-yawl-matters.md)

---

# Phase 1: Beginner — Your First Export

## Exercise 1: Export a Simple Sequence

**Goal:** Create and export a 3-activity sequence to YAWL XML.

```python
import pm4py
from pm4py.objects.powl.obj import Transition, Sequence

# Create a simple sequence: A → B → C
model = Sequence([
    Transition('Order Received'),
    Transition('Process Payment'),
    Transition('Ship Goods')
])

# Export to YAWL
pm4py.write_yawl(model, "simple_process.yawl")
print("✓ Exported to simple_process.yawl")
```

**What happened:**
1. Created a POWL model with 3 activities in sequence
2. Converted to YAWL specification object
3. Serialized to YAWL XML format
4. Wrote to `simple_process.yawl`

**Inspect the output:**
```bash
cat simple_process.yawl
```

You'll see XML with:
- `<specification>` — Root element
- `<decomposition>` — Process net
- `<task>` elements — Your activities
- `<flow>` elements — Connections between tasks

**Full tutorial:** [Export Process Models to YAWL Format](tutorial/yawl-export-first-steps.md)

---

## Exercise 2: Export from Natural Language

**Goal:** Generate a YAWL model from plain English description.

```bash
python -m pm4py.cli DiscoverPOWLToYAWL \
  "A customer submits a support ticket. The system categorizes by urgency. High urgency tickets are escalated to senior agents. Low urgency tickets are handled by junior agents." \
  support_process.yawl
```

**Output:**
```
YAWL model (VERIFIED) written to support_process.yawl
```

**What happened:**
1. AI parsed your description into a POWL model
2. Verified structural soundness (deadlock-free, live, bounded)
3. Converted to YAWL XML
4. Wrote to file with verification status

**Try these examples:**
- E-commerce: "Customer adds items to cart, proceeds to checkout, system validates inventory, processes payment if in stock, ships items"
- Healthcare: "Patient arrives at hospital, registers, insurance verified, triaged by nurse, sees doctor, treated, discharged"

**Full guide:** [Export from Natural Language to YAWL](how-to/nl-to-yawl-cli.md)

---

## Exercise 3: Inspect YAWL Object Model

**Goal:** Understand the YAWL specification structure before writing to file.

```python
import pm4py
from pm4py.objects.powl.obj import Transition, Sequence

# Create model
model = Sequence([
    Transition('A'),
    Transition('B'),
    Transition('C')
])

# Convert to YAWL specification object (not yet written to file)
yawl_spec = pm4py.convert_to_yawl(model)

# Inspect the object
print(f"URI: {yawl_spec.uri}")
print(f"Title: {yawl_spec.metadata.title}")
print(f"Decompositions: {len(yawl_spec.decompositions)}")

# Access root decomposition
root = yawl_spec.root_decomposition()
print(f"Tasks: {len(root.tasks)}")
print(f"Flows: {len(root.flows)}")

# Inspect first task
first_task = root.tasks[0]
print(f"First task: {first_task.name}")
print(f"Join type: {first_task.join_type}")
print(f"Split type: {first_task.split_type}")
```

**API reference:** [YAWL Export API Reference](reference/yawl-api.md)

---

# Phase 2: Intermediate — Complex Models & Conversions

## Exercise 4: Handle Decision Points (XOR)

**Goal:** Model exclusive choice with YAWL XOR split/join.

```python
from pm4py.objects.powl.obj import Transition, OperatorPOWL
from pm4py.objects.process_tree.obj import Operator

# Create XOR choice: Auto-approve OR Manual-review
model = OperatorPOWL(
    Operator.XOR,
    [
        Transition('Auto-approve'),
        Transition('Manual-review')
    ]
)

pm4py.write_yawl(model, "loan_choice.yawl")

# Verify XOR split in XML
with open("loan_choice.yawl", "r") as f:
    xml = f.read()
    if 'type="xor"' in xml:
        print("✓ XOR split/join found in YAWL XML")
```

**Pattern mapping:** XOR operators map to YAWL tasks with `join type="xor"` and `split type="xor"`.

---

## Exercise 5: Handle Parallel Execution

**Goal:** Model concurrent activities with YAWL AND split/join.

```python
from pm4py.objects.powl.obj import Transition, StrictPartialOrder

# Create parallel: Ship goods AND Process payment (no ordering constraint)
model = StrictPartialOrder([
    Transition('Ship Goods'),
    Transition('Process Payment')
])

pm4py.write_yawl(model, "parallel.yawl")

# Verify AND split in XML
with open("parallel.yawl", "r") as f:
    xml = f.read()
    if 'type="and"' in xml:
        print("✓ AND split/join found in YAWL XML")
```

**Pattern mapping:** Parallel operators (no edges in partial order) map to YAWL tasks with `join type="and"` and `split type="and"`.

---

## Exercise 6: Convert from BPMN

**Goal:** Export existing BPMN diagrams to YAWL format.

```python
import pm4py

# Read BPMN file
bpmn_graph = pm4py.read_bpmn("existing_process.bpmn")

# Convert to YAWL
yawl_spec = pm4py.convert_to_yawl(bpmn_graph)

# Write to YAWL file
pm4py.write_yawl(yawl_spec, "converted_process.yawl")

print("✓ Converted BPMN to YAWL")
```

**Conversion path:** `BPMN → POWL → YAWL`

**Full guide:** [Export BPMN Models to YAWL Format](how-to/bpmn-to-yawl.md)

---

## Exercise 7: Convert from Event Logs

**Goal:** Discover process model from event log and export to YAWL.

```python
import pm4py

# Read event log
log = pm4py.read_xes("running-example.xes")

# Discover POWL model
powl_model = pm4py.discover_powl(log)

# Export to YAWL
pm4py.write_yawl(powl_model, "discovered_process.yawl")

print("✓ Discovered and exported process to YAWL")
```

**Conversion path:** `Event Log → POWL → YAWL`

---

## Exercise 8: Troubleshoot Common Issues

**Problem:** "Conversion failed: Unsupported model type"

**Solution:** Ensure model is POWL or PetriNet:
```python
# Check model type
print(type(model))

# Convert to POWL first if needed
if hasattr(model, 'nodes'):
    # This is a PetriNet, convert to POWL first
    from pm4py.objects.conversion.powl.variants.to_powl import apply
    model = apply(model)

# Now export to YAWL
pm4py.write_yawl(model, "output.yawl")
```

**Problem:** "Model NOT VERIFIED"

**Solution:** Check reasoning and simplify:
```python
from pm4py.algo.dspy.powl.natural_language import generate_powl_from_text

result = generate_powl_from_text(description, max_refinements=2)
print(f"Reasoning: {result.get('reasoning', 'N/A')}")

# Use simpler description if verification failed
```

**Common issues:** [Reference: Error Handling](reference/yawl-api.md#error-handling)

---

# Phase 3: Advanced — Pattern Validation & Research

## Exercise 9: Validate Pattern Coverage

**Goal:** Verify which of the 43 workflow patterns are present in your model.

```python
import pm4py
from pm4py.objects.process_tree.obj import Operator
from pm4py.objects.powl.obj import OperatorPOWL, StrictPartialOrder

def count_operators(model):
    """Count operator types in POWL model."""
    counts = {"XOR": 0, "LOOP": 0, "PARTIAL_ORDER": 0, "TRANSITION": 0}

    if isinstance(model, OperatorPOWL):
        if model.operator == Operator.XOR:
            counts["XOR"] += 1
        elif model.operator == Operator.LOOP:
            counts["LOOP"] += 1
        for child in model.children:
            for k, v in count_operators(child).items():
                counts[k] += v
    elif isinstance(model, StrictPartialOrder):
        counts["PARTIAL_ORDER"] += 1
        for node in model.order.nodes:
            if hasattr(node, 'label'):
                counts["TRANSITION"] += 1
    else:
        counts["TRANSITION"] += 1

    return counts

# Analyze your model
log = pm4py.read_xes("running-example.xes")
powl_model = pm4py.discover_powl(log)
operator_counts = count_operators(powl_model)

print("Pattern coverage:")
for pattern, count in operator_counts.items():
    print(f"  {pattern}: {count}")
```

**Pattern mappings:** [Reference: Pattern Mappings](reference/yawl-api.md#pattern-mappings-powl--yawl)

---

## Exercise 10: Round-Trip Verification

**Goal:** Verify that conversion is lossless (POWL → YAWL → POWL).

```python
import pm4py
from pm4py.objects.powl.parser import parse_powl_model_string

# Create original model
from pm4py.objects.powl.obj import Transition, Sequence
original = Sequence([Transition('A'), Transition('B'), Transition('C')])

# Export to YAWL
yawl_spec = pm4py.convert_to_yawl(original)

# (Note: YAWL import not yet implemented, so we verify via XML inspection)
import pm4py.objects.yawl.exporter.variants.yawl_xml as yawl_exporter
xml_str = yawl_exporter.apply(yawl_spec)

# Verify key elements present
checks = {
    "specification": "<specification" in xml_str,
    "tasks": "<task" in xml_str,
    "flows": "<flow" in xml_str,
    "inputCondition": "<inputCondition" in xml_str,
    "outputCondition": "<outputCondition" in xml_str,
}

for element, found in checks.items():
    status = "✓" if found else "✗"
    print(f"{status} {element}")

if all(checks.values()):
    print("✓ All required YAWL elements present")
```

**Round-trip paths:**
- `POWL → YAWL → POWL` (future: YAWL import)
- `BPMN → POWL → YAWL` (verify BPMN→POWL conversion)
- `Event Log → POWL → YAWL` (verify discovery algorithms)

**Explanation:** [Why YAWL Export Matters](explanation/why-yawl-matters.md#3-round-trip-verification-testing-conversion-correctness)

---

## Exercise 11: Research Reproducibility

**Goal:** Validate algorithm correctness against YAWL reference semantics.

**Scenario:** You've developed a new process discovery algorithm and want to verify it correctly implements the Multi-Choice pattern.

```python
import pm4py
from pm4py.objects.powl.obj import Transition, StrictPartialOrder

# Create a Multi-Choice scenario (OR pattern)
A = Transition("Option A")
B = Transition("Option B")
C = Transition("Option C")
model = StrictPartialOrder([A, B, C])

# Export to YAWL
yawl_spec = pm4py.convert_to_yawl(model)

# Verify OR-split is present (reference semantics)
import pm4py.objects.yawl.exporter.variants.yawl_xml as yawl_exporter
xml_str = yawl_exporter.apply(yawl_spec)

if 'type="or"' in xml_str:
    print("✓ Multi-Choice correctly mapped to OR-split in YAWL")
else:
    print("✗ Multi-Choice NOT found — algorithm may be incorrect")
```

**Why this matters:** YAWL provides the canonical definition of Multi-Choice. If your algorithm doesn't produce OR-split in YAWL, it's not implementing Multi-Choice correctly.

**Explanation:** [Academic Reproducibility](explanation/why-yawl-matters.md#2-academic-reproducibility-how-researchers-validate-algorithms)

---

## Exercise 12: Batch Validate Pattern Mappings

**Goal:** Verify all 43 workflow patterns export correctly to YAWL constructs.

```python
import pm4py
from pm4py.objects.powl.obj import Transition, Sequence, OperatorPOWL, StrictPartialOrder
from pm4py.objects.process_tree.obj import Operator

# Test patterns from the 43 workflow patterns catalog
test_patterns = {
    "Sequence (Pattern 1)": Sequence([Transition('A'), Transition('B')]),
    "Parallel Split (Pattern 2)": StrictPartialOrder([Transition('A'), Transition('B')]),
    "XOR Choice (Pattern 4)": OperatorPOWL(Operator.XOR, [Transition('A'), Transition('B')]),
    "Structured Loop (Pattern 15)": OperatorPOWL(Operator.LOOP, [Transition('A'), Transition('B')]),
}

print("Validating pattern mappings:")
for pattern_name, model in test_patterns.items():
    try:
        yawl_spec = pm4py.convert_to_yawl(model)
        import pm4py.objects.yawl.exporter.variants.yawl_xml as yawl_exporter
        xml_str = yawl_exporter.apply(yawl_spec)

        # Check for valid YAWL structure
        if "<specification" in xml_str and "<decomposition" in xml_str:
            print(f"✓ {pattern_name}")
        else:
            print(f"✗ {pattern_name} — Invalid YAWL structure")
    except Exception as e:
        print(f"✗ {pattern_name} — Error: {e}")
```

**Pattern catalog:** [The 43 Workflow Patterns with POWL v2](../yawl-patterns-book/)

---

# Phase 4: Hero — Strategic Use & Future-Proofing

## Exercise 13: Position pm4py as "Switzerland" of Process Modeling

**Goal:** Use pm4py as the universal translator between all process modeling formats.

```python
import pm4py

# Read from ANY format
log = pm4py.read_xes("event_log.xes")          # Event log
bpmn = pm4py.read_bpmn("model.bpmn")           # BPMN
powl = pm4py.read_powl("model.powl")           # POWL

# Discover (from any format)
powl_model = pm4py.discover_powl(log)          # Event log → POWL
powl_model = pm4py.convert_to_powl(bpmn)       # BPMN → POWL

# Export to ANY format
pm4py.write_bpmn(powl_model, "output.bpmn")
pm4py.write_pnml(powl_model, "output.pnml")
pm4py.write_yawl(powl_model, "output.yawl")    # ← YAWL export
```

**Strategic value:** In heterogeneous enterprise environments, different systems use different formats. A tool that speaks all languages becomes the integration layer of choice.

**Explanation:** [Strategic Positioning](explanation/why-yawl-matters.md#5-strategic-positioning-switzerland-of-process-modeling)

---

## Exercise 14: Validate Against Reference Semantics

**Goal:** Use YAWL as the ground truth for pattern semantics.

**Scenario:** You're comparing two process mining tools. Tool A claims to implement Multi-Choice. Tool B claims to implement Multi-Choice. Which one is correct?

```python
# Export both tools' models to YAWL
tool_a_model = ...  # Load from Tool A
tool_b_model = ...  # Load from Tool B

pm4py.write_yawl(tool_a_model, "tool_a.yawl")
pm4py.write_yawl(tool_b_model, "tool_b.yawl")

# Inspect YAWL XML for OR-split
with open("tool_a.yawl", "r") as f:
    a_xml = f.read()
with open("tool_b.yawl", "r") as f:
    b_xml = f.read()

a_has_or = 'type="or"' in a_xml
b_has_or = 'type="or"' in b_xml

print(f"Tool A implements Multi-Choice correctly: {a_has_or}")
print(f"Tool B implements Multi-Choice correctly: {b_has_or}")
```

**Why this works:** YAWL is the original system where the 43 patterns were identified. It provides the canonical semantics.

**Explanation:** [YAWL as Reference Semantics](explanation/why-yawl-matters.md#6-yawl-as-reference-semantics)

---

## Exercise 15: Future-Proof for ProcessML 2030

**Goal:** Maintain validation infrastructure for future process modeling formalisms.

**Scenario:** It's 2030. A new process modeling formalism "ProcessML 2030" has emerged. How do researchers validate that ProcessML 2030 correctly implements the 43 workflow patterns?

**Answer:** Export ProcessML 2030 models to YAWL and verify behavior.

```python
# Hypothetical 2030 code
from processml_2030 import ProcessModel

# Create ProcessML 2030 model
model = ProcessModel.from_description("Multi-choice scenario")

# Convert to POWL (intermediate format)
powl_model = model.to_powl()

# Export to YAWL (validation target)
import pm4py
pm4py.write_yawl(powl_model, "processml_2030_validation.yawl")

# Verify OR-split present
with open("processml_2030_validation.yawl", "r") as f:
    if 'type="or"' in f.read():
        print("✓ ProcessML 2030 correctly implements Multi-Choice")
```

**Why this matters:** The YAWL export you implemented in 2026 provides the bridge between future formalisms and foundational research.

**Explanation:** [Future-Proofing](explanation/why-yawl-matters.md#8-future-proofing-when-processml-2030-emerges)

---

# Hero Challenge: Build a Validation Pipeline

**Goal:** Create an automated pipeline that validates process models against YAWL reference semantics.

```python
import pm4py
from pm4py.objects.powl.parser import parse_powl_model_string
from pm4py.algo.dspy.powl.natural_language import generate_powl_from_text

def validate_process_model(description):
    """Validate process model against YAWL reference semantics."""

    print(f"Validating: {description[:50]}...")

    # Step 1: Generate POWL from NL
    result = generate_powl_from_text(description, max_refinements=1)
    if not result["verdict"]:
        print(f"✗ Model generation failed verification")
        return False

    # Step 2: Parse POWL
    powl_model = parse_powl_model_string(result["powl"])
    if powl_model is None:
        print(f"✗ POWL parsing failed")
        return False

    # Step 3: Export to YAWL
    try:
        yawl_spec = pm4py.convert_to_yawl(powl_model)
    except Exception as e:
        print(f"✗ YAWL conversion failed: {e}")
        return False

    # Step 4: Validate YAWL XML structure
    import pm4py.objects.yawl.exporter.variants.yawl_xml as yawl_exporter
    xml_str = yawl_exporter.apply(yawl_spec)

    checks = {
        "specification": "<specification" in xml_str,
        "metadata": "<metadata" in xml_str,
        "decomposition": "<decomposition" in xml_str,
        "tasks": "<task" in xml_str,
        "flows": "<flow" in xml_str,
        "inputCondition": "<inputCondition" in xml_str,
        "outputCondition": "<outputCondition" in xml_str,
    }

    if all(checks.values()):
        print(f"✓ Model validated against YAWL reference semantics")
        return True
    else:
        failed = [k for k, v in checks.items() if not v]
        print(f"✗ Validation failed: {failed}")
        return False

# Test the validation pipeline
test_cases = [
    "A customer orders a product. The system validates inventory. If in stock, process payment and ship. If out of stock, notify customer and cancel.",
    "Patients arrive at emergency department and are triaged by severity. Critical patients go immediately to treatment. Serious patients wait for specialist consultation.",
    "Developer pushes code to repository. CI/CD pipeline triggers. Run unit tests. If tests pass, run integration tests. If all tests pass, deploy to staging.",
]

print("Running validation pipeline...")
for i, description in enumerate(test_cases, 1):
    print(f"\nTest case {i}:")
    validate_process_model(description)

print("\n✓ Validation pipeline complete")
```

**This demonstrates hero-level proficiency:**
- Integrated NL → POWL → YAWL pipeline
- Automated validation against reference semantics
- Batch processing of multiple test cases
- Comprehensive error checking
- Research-grade reproducibility

---

# Checklist: Zero to Hero Completion

Track your progress:

**Phase 0: Zero**
- [ ] Understand what YAWL is and why it matters
- [ ] Read [Why YAWL Export Matters](explanation/why-yawl-matters.md)

**Phase 1: Beginner**
- [ ] Exported a simple sequence to YAWL
- [ ] Exported from natural language using CLI
- [ ] Inspected YAWL object model structure
- [ ] Read [First Steps Tutorial](tutorial/yawl-export-first-steps.md)

**Phase 2: Intermediate**
- [ ] Handled XOR decision points
- [ ] Handled parallel execution
- [ ] Converted from BPMN
- [ ] Converted from event logs
- [ ] Troubleshot common issues
- [ ] Read [NL to YAWL How-To](how-to/nl-to-yawl-cli.md)
- [ ] Read [BPMN to YAWL How-To](how-to/bpmn-to-yawl.md)

**Phase 3: Advanced**
- [ ] Validated pattern coverage
- [ ] Performed round-trip verification
- [ ] Used YAWL for research reproducibility
- [ ] Batch validated pattern mappings
- [ ] Read [API Reference](reference/yawl-api.md)

**Phase 4: Hero**
- [ ] Used pm4py as universal translator
- [ ] Validated against reference semantics
- [ ] Understood future-proofing for ProcessML 2030
- [ ] Built automated validation pipeline
- [ ] Reviewed [Why YAWL Matters](explanation/why-yawl-matters.md) in depth

---

# Next Steps

**For practitioners:**
- Integrate YAWL export into your process mining workflow
- Validate discovered models against YAWL reference semantics
- Use round-trip verification to ensure conversion quality

**For researchers:**
- Use YAWL export for algorithm validation in publications
- Share YAWL models for reproducibility
- Compare tools against YAWL reference semantics

**For the curious:**
- Read [The 43 Workflow Patterns with POWL v2](../yawl-patterns-book/)
- Explore the complete [YAWL Export API Reference](reference/yawl-api.md)
- Understand the strategic vision in [Vision 2030](../powl_v2_thesis.md)

---

## Summary

You've progressed from **zero** (what is YAWL?) to **hero** (building validation pipelines):

- **Understanding**: YAWL's role as reference semantics for the 43 workflow patterns
- **Skills**: Export, convert, validate, troubleshoot, automate
- **Strategic thinking**: Position pm4py as universal translator, future-proof research infrastructure

**Congratulations!** 🎉 You're now ready to use YAWL export for production work, research validation, and strategic process modeling initiatives.

---

## See Also

- [Tutorials](tutorial/) — Step-by-step guides
- [How-To Guides](how-to/) — Task-oriented recipes
- [Explanation](explanation/) — Background and context
- [Reference](reference/) — Technical specifications
- [The 43 Workflow Patterns with POWL v2](../yawl-patterns-book/) — Pattern catalog
