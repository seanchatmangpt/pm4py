# YAWL Export API Reference

> Complete API documentation for exporting process models to YAWL format.

---

## Core Functions

### `pm4py.convert_to_yawl(model)`

Convert a process model to YAWL specification object.

**Parameters:**
- `model` (POWL or PetriNet): Process model to convert
  - `POWL` object: Direct conversion (recommended)
  - `(PetriNet, Marking, final_marking)` tuple: Converts via POWL intermediate
- **Returns:** `YAWLSpecification` object

**Example:**
```python
import pm4py
from pm4py.objects.powl.obj import Transition, Sequence

# Create sequence
model = Sequence([
    Transition('Order Received'),
    Transition('Process Payment'),
    Transition('Ship Goods')
])

# Convert to YAWL
yawl_spec = pm4py.convert_to_yawl(model)
print(f"Decompositions: {len(yawl_spec.decompositions)}")
```

---

### `pm4py.write_yawl(model, file_path)`

Export a process model to YAWL XML file.

**Parameters:**
- `model`: Process model to export (POWL, PetriNet, or YAWLSpecification)
- `file_path` (str): Output file path (`.yawl` extension added automatically if missing)

**Returns:** `None` (writes to disk)

**Example:**
```python
import pm4py

# Export POWL model directly
pm4py.write_yawl(model, "process.yawl")

# Auto-converts PetriNet or BPMN to YAWL if needed
```

**File Extension Behavior:**
- `write_yawl(model, "process")` → creates `process.yawl`
- `write_yawl(model, "process.xml")` → creates `process.xml.yawl`

---

### `pm4py.objects.conversion.yawl.converter.apply(model, parameters)`

Low-level conversion function (direct import path).

**Parameters:**
- `model`: POWL model to convert
- `parameters`: Conversion parameters (optional)

**Returns:** `YAWLSpecification` object

**Example:**
```python
from pm4py.objects.conversion.yawl.converter import apply

yawl_spec = apply(model, parameters=None)
```

---

### `pm4py.objects.yawl.exporter.exporter.serialize(model, parameters)`

Serialize YAWL specification to XML string (in-memory).

**Parameters:**
- `model`: `YAWLSpecification` object
- `parameters`: Export parameters (optional)
  - `pretty_print` (bool): Pretty-print XML with indentation (default: `True`)
  - `indent` (str): Indentation string (default: `"  "`)

**Returns:** `str` - XML string

**Example:**
```python
from pm4py.objects.yawl.exporter.exporter import serialize

xml_str = serialize(yawl_spec, parameters={"pretty_print": True})
print(xml_str)
```

---

## Data Classes

### `YAWLSpecification`

Root container for YAWL specification.

**Attributes:**
- `uri` (str): Unique specification identifier
- `metadata` (`YAWLMetadata`): Specification metadata
- `decompositions` (List[`YAWLDecomposition`]): Process nets

**Methods:**
- `root_decomposition()`: Returns the root decomposition (main process net)

**Example:**
```python
from pm4py.objects.yawl.obj import YAWLSpecification

spec = YAWLSpecification(
    uri="my-spec",
    metadata=YAWLMetadata(title="My Process")
)
# Decompositions are created automatically
```

---

### `YAWLMetadata`

Metadata for YAWL specification.

**Attributes:**
- `title` (str): Specification title
- `description` (str): Description (optional)
- `version` (str): Version string (default: `"1.0"`)
- `author` (str): Author/creator (default: `"pm4py"`)
- `created` (str): ISO timestamp (auto-generated)

---

### `YAWLDecomposition`

Process net containing tasks and flows.

**Attributes:**
- `id` (str): Decomposition identifier
- `is_root_net` (bool): Whether this is the root/main process
- `input_condition` (str): Input condition ID (default: `"input"`)
- `output_condition` (str): Output condition ID (default: `"output"`)
- `tasks` (List[`YAWLTask`]): Tasks in this decomposition
- `flows` (List[`YAWLFlow`]): Flow edges

---

### `YAWLTask`

Atomic or composite task.

**Attributes:**
- `id` (str): Unique task identifier
- `name` (str): Human-readable label
- `join_type` (str): Join type - `"xor"`, `"and"`, or `"or"`
- `split_type` (str): Split type - `"xor"`, `"and"`, or `"or"`
- `decomposition_id` (Optional[str]): Reference to subprocess decomposition

**Split/Join Types:**
| Type | Meaning |
|------|---------|
| `xor` | Exclusive: exactly one path executes |
| `and` | Parallel: all paths execute simultaneously |
| `or` | Inclusive: multiple paths may execute |

---

### `YAWLFlow`

Directed edge between nodes.

**Attributes:**
- `source` (str): Source node ID (task or condition)
- `target` (str): Target node ID (task or condition)

---

## CLI Commands

### `DiscoverPOWLToYAWL`

Generate YAWL model from natural language description.

**Usage:**
```bash
python -m pm4py.cli DiscoverPOWLToYAWL \
  "Process description here..." \
  output.yawl
```

**Input:**
- Natural language description (text file path or inline string)
- Process description in free text

**Output:**
- YAWL XML file (`.yawl`)
- Console output shows verification status: `(VERIFIED)` or `(NOT VERIFIED)`

**Example:**
```bash
python -m pm4py.cli DiscoverPOWLToYAWL \
  "A customer orders a product. The system validates inventory. If in stock, process payment and ship. If out of stock, notify customer and cancel." \
  order_process.yawl
```

---

## Pattern Mappings: POWL → YAWL

| POWL Type | YAWL Construct | Pattern |
|-----------|---------------|---------|
| `Transition` | Atomic task | All activities |
| `Operator.SEQUENCE` (via `Sequence`) | Sequential flows | Pattern 1: Sequence |
| `Operator.XOR` | XOR-split + XOR-join | Pattern 4: Exclusive Choice, Pattern 5: Simple Merge |
| `Operator.PARALLEL` (via `StrictPartialOrder` with no edges) | AND-split + AND-join | Pattern 2: Parallel Split, Pattern 3: Synchronization |
| `Operator.LOOP` | Decomposition loop with back-edge | Pattern 15: Structured Loop, Pattern 10: Arbitrary Cycles |
| `StrictPartialOrder` | Multiple tasks + flows | Pattern 16: Arbitrary Interleaving, Pattern 22: Interleaved Routing |
| `DecisionGraph` | OR-split + OR-join with predicates | Pattern 6: Multi-Choice, Pattern 7: Synchronizing Merge |

---

## Examples

### Example 1: Export Simple Sequence

```python
import pm4py
from pm4py.objects.powl.obj import Transition, Sequence

# Create model
model = Sequence([
    Transition('Submit Application'),
    Transition('Review Application'),
    Transition('Approve Application')
])

# Export to YAWL
pm4py.write_yawl(model, "approval_process.yawl")
```

### Example 2: Export XOR Choice

```python
from pm4py.objects.powl.obj import Transition, OperatorPOWL
from pm4py.objects.process_tree.obj import Operator

# Create XOR: Auto-approve OR Manual-review
model = OperatorPOWL(
    Operator.XOR,
    [
        Transition('Auto-approve'),
        Transition('Manual-review')
    ]
)

pm4py.write_yawl(model, "loan_choice.yawl")
```

### Example 3: Export Parallel Execution

```python
from pm4py.objects.powl.obj import Transition, StrictPartialOrder

# Create parallel: Ship goods AND Process payment
model = StrictPartialOrder([
    Transition('Ship Goods'),
    Transition('Process Payment')
])

pm4py.write_yawl(model, "parallel.yawl")
```

### Example 4: Inspect YAWL Object Before Writing

```python
from pm4py.objects.yawl.obj import create_specification

# Create specification with custom metadata
spec = create_specification(
    title="Custom Process",
    description="E-commerce checkout flow"
)

# Add decomposition (manual construction)
from pm4py.objects.yawl.obj import YAWLTask, YAWLFlow
decomp = spec.decompositions[0]  # Get root decomposition

# Add task
task = YAWLTask(
    id="t1",
    name="Process Order",
    join_type="xor",
    split_type="xor"
)
decomp.tasks.append(task)

# Add flow
decomp.flows.append(YAWLFlow(source="input", target="t1"))
decomp.flows.append(YAWLFlow(source="t1", target="output"))

# Write to file
pm4py.write_yawl(spec, "manual_process.yawl")
```

---

## Error Handling

### Common Exceptions

| Exception | Cause | Solution |
|----------|--------|----------|
| `AttributeError: module 'pm4py' has no attribute 'convert_to_yawl'` | pm4py not imported | Install pm4py or update to latest version |
| `Exception: "Unsupported conversion"` | Model type not supported | Ensure model is POWL or PetriNet |
| `FileNotFoundError` | Invalid file path | Check file path is correct and directory exists |
| `ValueError: "Generated POWL could not be parsed"` | LLM generation failed | Try `max_refinements=2` or simplify description |

---

## Performance Considerations

### Conversion Complexity

| Model Type | Time Complexity | Space Complexity |
|------------|-----------------|------------------|
| Single Transition | O(1) | O(1) |
| Sequence (N activities) | O(N) | O(N) |
| XOR (N branches) | O(N) | O(N) |
| Parallel (N activities) | O(N²) | O(N²) for edges |
| Loop | O(N) | O(N) |

For large models (>1000 activities), consider:
- Exporting specific subprocesses separately
- Using streaming/chunked export
- Simplifying model structure before export

### Memory Usage

YAWL XML serialization loads the entire model into memory before writing. For very large models (>10MB YAWL XML), consider:
- Exporting subsets of the model
- Using direct file writing instead of string serialization
- Processing in batches

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-04-07 | Initial YAWL export support in pm4py |
| | | - POWL → YAWL conversion (via from_powl.py) |
| | | - YAWL XML serialization (via yawl_xml.py) |
| | | - CLI integration (DiscoverPOWLToYAWL) |
| | | - Public API (convert_to_yawl, write_yawl) |
| | | - 17 unit tests, all passing |

---

## See Also

- [Tutorials](../../diataxis/tutorial/) - Step-by-step guides
- [How-To Guides](../../diataxis/how-to/) - Task-oriented recipes
- [Explanation: Why YAWL Matters](../../diataxis/explanation/why-yawl-matters.md) - Strategic justification
- [The 43 Workflow Patterns with POWL v2](../../yawl-patterns-book/) - Pattern catalog with YAWL mappings
