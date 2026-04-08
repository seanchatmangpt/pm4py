# Export BPMN Models to YAWL Format

> Convert existing BPMN diagrams to YAWL XML format for pattern validation and research reproducibility.

---

## Use Cases

- **Validate BPMN models** against the 43 workflow patterns
- **Export to YAWL engine** for execution testing
- **Round-trip verification**: BPMN → POWL → YAWL → POWL → BPMN
- **Academic reproducibility**: Share models in YAWL format for research validation

---

## Prerequisites

- Python 3.9+ installed
- pm4py library installed: `pip install pm4py`
- Existing BPMN 2.0 XML file (`.bpmn`)

---

## Method 1: Direct BPMN to YAWL

```python
import pm4py

# Read BPMN file
bpmn_graph = pm4py.read_bpmn("loan_process.bpmn")

# Convert to YAWL
yawl_spec = pm4py.convert_to_yawl(bpmn_graph)

# Write to YAWL file
pm4py.write_yawl(yawl_spec, "loan_process.yawl")
```

**Note:** BPMN → YAWL conversion goes through POWL as intermediate:
```
BPMN → POWL → YAWL
```

---

## Method 2: With POWL Intermediate (For Inspection)

If you want to inspect or modify the POWL model before YAWL export:

```python
import pm4py

# Read BPMN
bpmn_graph = pm4py.read_bpmn("loan_process.bpmn")

# Convert to POWL first
powl_model = pm4py.convert_to_powl(bpmn_graph)

# Optionally inspect or modify the POWL model
print(f"POWL model: {powl_model}")

# Then convert to YAWL
yawl_spec = pm4py.convert_to_yawl(powl_model)
pm4py.write_yawl(yawl_spec, "loan_process.yawl")
```

---

## Validate Pattern Coverage

After exporting to YAWL, verify which of the 43 workflow patterns are present:

```python
from pm4py.objects.powl.parser import parse_powl_model_string

# Read BPMN and convert to POWL
bpmn_graph = pm4py.read_bpmn("complex_process.bpmn")
powl_model = pm4py.convert_to_powl(bpmn_graph)

# Check for operators
from pm4py.objects.process_tree.obj import Operator
from pm4py.objects.powl.obj import OperatorPOWL, StrictPartialOrder

def count_operators(model):
    """Count operator types in POWL model."""
    counts = {
        "XOR": 0,
        "LOOP": 0,
        "PARTIAL_ORDER": 0,
        "TRANSITION": 0
    }
    
    if isinstance(model, OperatorPOWL):
        if model.operator == Operator.XOR:
            counts["XOR"] += 1
        elif model.operator == Operator.LOOP:
            counts["LOOP"] += 1
        # Check children recursively
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

operator_counts = count_operators(powl_model)
print("Pattern coverage:")
for pattern, count in operator_counts.items():
    print(f"  {pattern}: {count}")
```

---

## Convert Specific BPMN Gateway Types

### Exclusive Gateway (XOR) to YAWL

BPMN exclusive gateway (diamond with "X"):
```xml
<exclusiveGateway id="gateway1" name="Check Credit"/>
```

Converts to YAWL tasks with `join type="xor"` and `split type="xor"`.

### Parallel Gateway (AND) to YAWL

BPMN parallel gateway (diamond with "+"):
```xml
<parallelGateway id="gateway2" name="Process in Parallel"/>
```

Converts to YAWL tasks with `join type="and"` and `split type="and"`.

### Inclusive Gateway (OR) to YAWL

BPMN inclusive gateway (diamond with "○"):
```xml
<inclusiveGateway id="gateway3" name="Multiple Options"/>
```

Converts to YAWL tasks with `join type="or"` and `split type="or"`.

---

## Batch Convert Multiple BPMN Files

```python
import pm4py
import os
from pathlib import Path

# Directory containing BPMN files
bpmn_dir = Path("bpmn_models")
yawl_dir = Path("yawl_models")
yawl_dir.mkdir(exist_ok=True)

# Convert all .bpmn files to .yawl
for bpmn_file in bpmn_dir.glob("*.bpmn"):
    try:
        # Read BPMN
        bpmn_graph = pm4py.read_bpmn(str(bpmn_file))
        
        # Convert to YAWL
        yawl_spec = pm4py.convert_to_yawl(bpmn_graph)
        
        # Write YAWL
        yawl_file = yawl_dir / (bpmn_file.stem + ".yawl")
        pm4py.write_yawl(yawl_spec, str(yawl_file))
        
        print(f"✓ Converted {bpmn_file.name} → {yawl_file.name}")
    except Exception as e:
        print(f"✗ Failed to convert {bpmn_file.name}: {e}")
```

---

## Handle BPMN with Pools/lanes

### Convert Single Pool

```python
import pm4py

bpmn_graph = pm4py.read_bpmn("process_with_pool.bpmn")

# Convert to YAWL (pools are preserved as metadata)
yawl_spec = pm4py.convert_to_yawl(bpmn_graph)
pm4py.write_yawl(yawl_spec, "process_with_pool.yawl")
```

### Convert All Pools Individually

```python
import pm4py
from pm4py.objects.bpmn.obj import BPMN

bpmn_graph = pm4py.read_bpmn("multi_pool_process.bpmn")

# Each participant pool becomes a separate YAWL file
for participant in bpmn_graph.participants:
    # Extract subprocess for this participant
    subprocess = bpmn_graph.get_participant_subprocess(participant)
    
    # Convert to YAWL
    yawl_spec = pm4py.convert_to_yawl(subprocess)
    
    # Write to participant-specific file
    filename = f"process_{participant.id}.yawl"
    pm4py.write_yawl(yawl_spec, filename)
    
    print(f"Exported participant: {participant.id}")
```

---

## Verify YAWL Output

After conversion, validate the YAWL file structure:

```python
from pm4py.objects.yawl.obj import YAWLSpecification
from pm4py.objects.yawl.exporter.exporter import serialize

# Export to YAWL (in-memory)
yawl_spec = pm4py.convert_to_yawl(bpmn_graph)
xml_str = serialize(yawl_spec)

# Validate XML structure
if "<specification" in xml_str:
    print("✓ Valid YAWL XML structure")
else:
    print("✗ Invalid YAWL XML")

# Check for required elements
checks = {
    "decomposition": "<decomposition" in xml_str,
    "task": "<task" in xml_str,
    "flow": "<flow" in xml_str,
    "inputCondition": "<inputCondition" in xml_str,
    "outputCondition": "<outputCondition" in xml_str,
}

for element, found in checks.items():
    status = "✓" if found else "✗"
    print(f"{status} {element}")
```

---

## Common Issues

### "Conversion failed: Unsupported BPMN element"

**Problem:** The BPMN file contains elements not mappable to YAWL.

**Solution:**
- YAWL does not support message flows, event-based gateways, or complex event sub-processes
- Simplify the BPMN model to basic gateways and tasks
- Use BPMN → POWL → YAWL conversion and inspect the intermediate POWL model

### "YAWL file is missing tasks"

**Problem:** Export succeeded but tasks are empty.

**Solution:**
- Check that BPMN activities have labels: `task.get_name()` should not be empty
- Verify BPMN is connected (all tasks have incoming/outgoing sequence flows)
- BPMN models with only events (no tasks) cannot be converted

### "Loop structure converted incorrectly"

**Problem:** BPMN loop pattern doesn't match YAWL semantics.

**Solution:**
- YAWL handles loops via explicit back-edge flows
- Check that your BPMN uses sequence flows correctly
- Consider restructuring the BPMN model to use explicit loop markers

---

## Advanced: Custom YAWL Metadata

Add custom metadata to exported YAWL files:

```python
import pm4py
from pm4py.objects.yawl.obj import create_specification

# Convert to YAWL
yawl_spec = pm4py.convert_to_yawl(bpmn_graph)

# Customize metadata
yawl_spec.metadata.title = "Custom Title"
yawl_spec.metadata.description = "Process exported from BPMN on 2026-04-07"
yawl_spec.metadata.author = "Your Name"
yawl_spec.metadata.version = "2.0"

# Write with custom metadata
pm4py.write_yawl(yawl_spec, "custom_metadata.yawl")
```

---

## Related Guides

- [Export from Natural Language to YAWL](nl-to-yawl-cli.md)
- [Export Event Logs to YAWL](logs-to-yawl.md)
- [Import and Verify YAWL Files](import-yawl.md)
