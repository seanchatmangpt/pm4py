# Export Process Models to YAWL Format

> Export your first process model to YAWL XML format in 5 minutes.

---

## What You'll Learn

In this tutorial, you will:
- Export a simple process model to YAWL XML format
- Inspect the generated YAWL file
- Understand the basic structure of YAWL XML
- Use the CLI to export from natural language to YAWL

## Prerequisites

- Python 3.9+ installed
- pm4py library installed: `pip install pm4py`
- Basic understanding of process models (optional)

---

## Part 1: Export a Simple Process Model

Let's start with a basic sequence of three activities: **Order Received → Process Payment → Ship Goods**.

### Step 1: Create a POWL Model

```python
import pm4py
from pm4py.objects.powl.obj import Transition, Sequence

# Create a simple sequence: A → B → C
A = Transition('Order Received')
B = Transition('Process Payment')
C = Transition('Ship Goods')
model = Sequence([A, B, C])

print(f"Created model: {model}")
```

Output:
```
Created model: SEQ(
  Order Received,
  Process Payment,
  Ship Goods
)
```

### Step 2: Convert to YAWL Specification

```python
# Convert POWL to YAWL
yawl_spec = pm4py.convert_to_yawl(model)

print(f"YAWL specification created with {len(yawl_spec.decompositions)} decomposition(s)")
```

Output:
```
YAWL specification created with 1 decomposition(s)
```

### Step 3: Export to YAWL File

```python
# Write to YAWL XML file
pm4py.write_yawl(model, "simple_process.yawl")
print("YAWL file written: simple_process.yawl")
```

### Step 4: Inspect the Generated File

Open `simple_process.yawl` in your text editor:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<specification xmlns="http://www.yawlfoundation.org/yawlschema" version="2.0">
  <specificationSet>
    <specification uri="pm4py-...">
      <metadata>
        <title>POWL to YAWL: SEQ(</title>
        <version>1.0</version>
        <author>pm4py</author>
        <created>2026-04-07T...</created>
      </metadata>

      <decomposition id="root" isRootNet="true">
        <inputCondition id="input"/>
        <outputCondition id="output"/>

        <task id="t_Order_Received_0">
          <name>Order Received</name>
          <join type="xor"/>
          <split type="xor"/>
        </task>

        <task id="t_Process_Payment_1">
          <name>Process Payment</name>
          <join type="xor"/>
          <split type="xor"/>
        </task>

        <task id="t_Ship_Goods_2">
          <name>Ship Goods</name>
          <join type="xor"/>
          <split type="xor"/>
        </task>

        <flow source="input" target="t_Order_Received_0"/>
        <flow source="t_Order_Received_0" target="t_Process_Payment_1"/>
        <flow source="t_Process_Payment_1" target="t_Ship_Goods_2"/>
        <flow source="t_Ship_Goods_2" target="output"/>
      </decomposition>
    </specification>
  </specificationSet>
</specification>
```

**Key YAWL Elements:**
- `<specification>` - Root element with namespace
- `<decomposition>` - Process net containing tasks and flows
- `<task>` - Activity with join/split types
- `<flow>` - Directed edge connecting tasks
- `<inputCondition>` / `<outputCondition>` - Start/end markers

---

## Part 2: Export from Natural Language

You can also generate YAWL directly from a text description:

```bash
python -m pm4py.cli DiscoverPOWLToYAWL \
  "A customer orders a product. The system validates the order. If valid, process payment and ship. If invalid, reject." \
  order_process.yawl
```

Output:
```
YAWL model (VERIFIED) written to order_process.yawl
```

This one command:
1. Parses your natural language description
2. Generates a POWL model using AI
3. Verifies the model is sound (deadlock-free, live, bounded)
4. Converts to YAWL XML
5. Writes to `order_process.yawl`

---

## Part 3: Export with Choice (XOR)

Real processes have decisions. Let's model a loan approval with two branches:

```python
from pm4py.objects.powl.obj import Transition, OperatorPOWL
from pm4py.objects.process_tree.obj import Operator

# Create XOR choice: Auto-approve OR Manual-review
A = Transition('Auto-approve')
B = Transition('Manual-review')
model = OperatorPOWL(Operator.XOR, [A, B])

# Export to YAWL
pm4py.write_yawl(model, "loan_choice.yawl")
```

The generated YAWL XML will have:
- Tasks with `join type="xor"` and `split type="xor"`
- Two parallel flows from input
- Both flows merge at output

---

## Part 4: Export with Parallel Execution

For concurrent activities, use a partial order (no edges = parallel):

```python
from pm4py.objects.powl.obj import Transition, StrictPartialOrder

# Create parallel: Ship goods AND Process payment
A = Transition('Ship Goods')
B = Transition('Process Payment')
model = StrictPartialOrder([A, B])

pm4py.write_yawl(model, "parallel.yawl")
```

In YAWL XML:
- Both tasks connect from `inputCondition`
- Both tasks connect to `outputCondition`
- Tasks execute concurrently (no ordering constraint)

---

## Summary

You've learned:

1. **POWL models** can be exported to YAWL using `pm4py.convert_to_yawl()`
2. **YAWL files** contain XML with `<specification>`, `<decomposition>`, `<task>`, and `<flow>` elements
3. **CLI shortcut**: `python -m pm4py.cli DiscoverPOWLToYAWL` for natural language input
4. **Pattern mappings**:
   - Sequence → sequential flows
   - XOR → XOR split/join (exclusive choice)
   - Parallel (no edges) → concurrent execution

## Next Steps

- **Tutorial:** [Import and Export Event Logs](../how-to/import-export-logs.md)
- **How-to:** [Export from BPMN to YAWL](../how-to/bpmn-to-yawl.md)
- **Reference:** [YAWL Export API](../reference/yawl-api.md)
- **Explanation:** [Why YAWL Export Matters](../explanation/why-yawl-matters.md)
