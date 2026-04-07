# POWL and LLM Integration Documentation

Complete guide to using PM4Py's POWL (Partially Ordered Workflow Language) models with Large Language Models via two approaches: simple abstractions and advanced DSPy pipelines.

---

## Part 1: Tutorials (Learning by Doing)

### Tutorial 1: Your First POWL-LLM Workflow

Learn how to discover a POWL model and explain it using an LLM in 5 minutes.

**Prerequisites:**
- PM4Py installed with LLM connectors: `pip install pm4py anthropic openai google-generativeai`
- An API key (OpenAI, Anthropic, or Google Gemini)
- A process event log in XES format

**Steps:**

1. **Discover a POWL model from your event log**
   ```python
   import pm4py

   # Read an event log
   log = pm4py.read_xes("my_process_log.xes", return_legacy_log_object=True)

   # Discover the POWL model
   powl_model = pm4py.discover_powl(log)
   print(powl_model)
   ```

2. **Abstract the model to natural language**
   ```python
   # Get a text description suitable for LLM input
   powl_text = pm4py.llm.abstract_powl(powl_model)
   print(powl_text)
   ```

3. **Query an LLM about your model**
   ```python
   # Use Anthropic Claude (recommended)
   response = pm4py.llm.anthropic_query(
       prompt=powl_text + "\n\nWhat are the main activities in this process?",
       api_key="your-anthropic-key"
   )
   print(response)
   ```

**What you learned:**
- How to go from event log → POWL model → natural language description
- How to feed process models to LLMs for analysis
- The basic LLM abstraction workflow

---

### Tutorial 2: Advanced Analysis with DSPy

Learn how to use typed LLM signatures and modular reasoning for deeper process insights.

**Prerequisites:**
- All prerequisites from Tutorial 1
- DSPy installed: `pip install dspy-ai`

**Steps:**

1. **Configure DSPy with your LM provider**
   ```python
   import dspy
   import pm4py

   # Set up DSPy to use your preferred LM
   dspy.settings.configure(
       lm=dspy.Anthropic(
           model="claude-3-5-sonnet-20241022",
           api_key="your-anthropic-key"
       )
   )
   ```

2. **Explain a POWL model using Chain-of-Thought reasoning**
   ```python
   log = pm4py.read_xes("my_process_log.xes", return_legacy_log_object=True)
   powl_model = pm4py.discover_powl(log)

   # Generate an explanation with reasoning steps
   explanation = pm4py.llm.explain_powl(powl_model)
   print(explanation)
   ```

3. **Compare two POWL models**
   ```python
   # Discover models with different algorithms
   from pm4py.algo.discovery.powl.inductive.variants.powl_discovery_varaints import POWLDiscoveryVariant

   powl_1 = pm4py.discover_powl(
       log,
       variant=POWLDiscoveryVariant.DYNAMIC_CLUSTERING
   )
   powl_2 = pm4py.discover_powl(
       log,
       variant=POWLDiscoveryVariant.MAXIMAL_ORDER
   )

   # Compare them with structural analysis
   result = pm4py.llm.compare_powl_models(powl_1, powl_2)
   print(f"Comparison:\n{result['comparison']}")
   print(f"Confidence: {result['confidence']}")
   ```

4. **Discover a POWL model from natural language**
   ```python
   # Describe a process in plain English
   description = """
   A purchase request process starts with a request submission.
   The request is then either auto-approved if under $1000 or sent to a manager for review.
   After approval, an order is placed and finally archived.
   """

   # Generate a POWL model string
   powl_string = pm4py.llm.discover_powl_from_description(description)
   print(f"Generated POWL:\n{powl_string}")

   # Parse it back into a POWL object
   powl_model = pm4py.objects.powl.parser.parse_powl_model_string(powl_string)
   ```

**What you learned:**
- How to configure DSPy with different LM providers
- How to use Chain-of-Thought reasoning for process model analysis
- How to compare POWL models structurally
- How to generate POWL models from natural language descriptions

---

## Part 2: How-To Guides (Tasks & Solutions)

### How-To: Explain a Complex POWL Model

**Problem:** You have a discovered POWL model with many nested choice and loop structures, and you need a clear explanation for stakeholders.

**Solution:**
```python
import pm4py
import dspy

# Configure LM
dspy.settings.configure(
    lm=dspy.OpenAI(model="gpt-4", api_key="your-key")
)

# Get your POWL model
powl_model = pm4py.discover_powl(log)

# Generate explanation
explanation = pm4py.llm.explain_powl(powl_model)

# Extract just the model description (without POWL semantics header)
simple_description = pm4py.llm.abstract_powl(
    powl_model,
    response_header=False
)

# Prompt for even more detail
detailed_prompt = f"""
Here is a process model:
{simple_description}

Explain this model to a non-technical business analyst. Focus on:
1. Main activities and their sequence
2. Choice points and their meaning
3. Any loops or repetitions
4. The overall business flow
"""

response = pm4py.llm.openai_query(detailed_prompt, api_key="your-key")
print(response)
```

---

### How-To: Identify Differences Between Two Discovery Methods

**Problem:** Two POWL discovery algorithms produce different models. You want to understand which differences are significant.

**Solution:**
```python
from pm4py.algo.discovery.powl.inductive.variants.powl_discovery_varaints import POWLDiscoveryVariant

# Discover with two methods
powl_brute_force = pm4py.discover_powl(
    log,
    variant=POWLDiscoveryVariant.BRUTE_FORCE
)
powl_maximal = pm4py.discover_powl(
    log,
    variant=POWLDiscoveryVariant.MAXIMAL_ORDER
)

# Compare structurally with DSPy
result = pm4py.llm.compare_powl_models(
    powl_brute_force,
    powl_maximal,
    lm=dspy.settings.lm
)

print("Structural Differences:")
print(result['comparison'])
print(f"\nConfidence: {result['confidence']}")
```

---

### How-To: Build a Process Model from Textual Process Description

**Problem:** You have process documentation in plain English and want to create a formal POWL model.

**Solution:**
```python
# Step 1: Extract process description (e.g., from documentation or interviews)
process_doc = """
When an invoice arrives, it enters the system. The system checks if the amount is below €500.
If yes, it goes directly to payment. If no, it requires manager approval first.
After either path, the invoice is paid and marked as completed.
Invoices over €10,000 also require CFO review before payment.
"""

# Step 2: Generate POWL model string
powl_string = pm4py.llm.discover_powl_from_description(process_doc)
print(f"Generated POWL:\n{powl_string}")

# Step 3: Validate by parsing
try:
    powl_model = pm4py.objects.powl.parser.parse_powl_model_string(powl_string)
    print("✓ POWL model is valid and can be parsed")
    
    # Step 4: Visualize for review
    pm4py.view_powl(powl_model, format="png", variant_str="basic")
except Exception as e:
    print(f"✗ Parse error (ask LLM to fix): {e}")
```

---

### How-To: Batch Process Multiple Logs with LLM Summaries

**Problem:** You have multiple event logs and want an LLM summary of each.

**Solution:**
```python
import os

log_files = [f for f in os.listdir("logs/") if f.endswith(".xes")]

for log_file in log_files:
    # Discover model
    log = pm4py.read_xes(f"logs/{log_file}", return_legacy_log_object=True)
    powl = pm4py.discover_powl(log)
    
    # Get concise summary (truncate to 1000 chars)
    summary = pm4py.llm.abstract_powl(powl, max_len=1000)
    
    # Query LLM
    result = pm4py.llm.anthropic_query(
        prompt=summary + "\n\nSummarize this process in one sentence.",
        api_key="your-key"
    )
    
    print(f"{log_file}: {result}")
```

---

## Part 3: Explanations (Understanding Concepts)

### Understanding POWL

**What is POWL?**

POWL (Partially Ordered Workflow Language) is PM4Py's modern process model that extends traditional workflow networks with:

1. **Transitions** (activities) - labeled nodes representing work
2. **Partial Orders** - flexible sequencing where independent activities can execute in any order
3. **Choice operators** - exclusive choice between alternative paths (XOR)
4. **Loop operators** - iterative execution patterns

**Why POWL over Petri Nets?**

- **More expressive**: Partial orders naturally represent concurrency without requiring complex marking rules
- **Simpler syntax**: `PO=(nodes={A, B, C}, order={A→B})` is easier to understand than place-transition structures
- **LLM-friendly**: String representation is human-readable, making it ideal for feeding to language models

**Example POWL model:**
```
PO=(
  nodes={
    'Submit Request',
    X('Auto-Approve', 'Manager Review'),
    'Process Payment',
    'Archive'
  },
  order={
    'Submit Request' --> 'Auto-Approve',
    'Submit Request' --> 'Manager Review',
    'Auto-Approve' --> 'Process Payment',
    'Manager Review' --> 'Process Payment',
    'Process Payment' --> 'Archive'
  }
)
```

This represents: Submit → (Auto-Approve XOR Manager Review in parallel) → Payment → Archive

---

### Understanding the LLM Abstraction Layer

**Why `abstract_powl()` exists:**

The LLM connectors expect text input. PM4Py's `abstract_*` functions convert structured models into natural language descriptions.

**What `abstract_powl()` includes:**

1. **POWL Semantics Header** (optional) - explains what POWL is and its syntax
2. **Model String** - the `repr()` of the POWL object (parseable format)

**When to use what:**

| Task | Use This |
|------|----------|
| Feed to LLM for analysis | `abstract_powl()` |
| Get just the model syntax | `repr(powl_model)` |
| Feed to LLM with custom prompt | `abstract_powl(response_header=False)` |

---

### Understanding DSPy for Process Mining

**What is DSPy?**

DSPy is a framework for programming with language models using:
- **Signatures** - typed input/output contracts for LLM tasks
- **Modules** - reusable LLM components with internal prompting logic
- **Chain-of-Thought** - multi-step reasoning that shows its work

**Why DSPy for POWL?**

1. **Type Safety** - `ExplainPOWL` signature defines expected inputs and outputs
2. **Composability** - chain multiple LLM steps without manual prompt engineering
3. **Reproducibility** - same signature always produces structured output
4. **Optimizability** - DSPy can optimize prompts automatically

**POWL v2 DSPy modules:**

| Module | Purpose | Input | Output |
|--------|---------|-------|--------|
| `POWLExplainer` | Explain model semantics | POWL text | Natural language explanation |
| `POWLDiscoverer` | Generate POWL from text | Process description | POWL model string |
| `POWLComparator` | Compare model structures | Two POWL texts | Comparison + confidence |

---

### Understanding POWL Discovery vs. Generation

**Discovery (data-driven):**
```
Event Log → Discovery Algorithm → POWL Model
```
- Start with real process execution data
- Algorithm learns the model from observed behavior
- Suitable when you have event logs

**Generation (text-driven):**
```
Process Description → LLM → POWL Model String
```
- Start with documented process procedures
- LLM generates model from natural language
- Suitable when you have documentation

**When to use each:**

- **Discovery**: You have event data and want to learn the actual process
- **Generation**: You have documentation and want a formal model
- **Validation**: Generate from docs, then compare with discovered model to find gaps

---

## Part 4: Reference

### API Reference

#### `pm4py.llm.abstract_powl()`

**Signature:**
```python
abstract_powl(
    powl_model,
    response_header: bool = True,
    max_len: int = constants.OPENAI_MAX_LEN
) -> str
```

**Parameters:**
- `powl_model` (POWL) - The model to abstract
- `response_header` (bool) - Include POWL semantics explanation (default: True)
- `max_len` (int) - Maximum output length in characters (default: 8192)

**Returns:** String description suitable for LLM input

**Example:**
```python
powl_text = pm4py.llm.abstract_powl(powl_model, response_header=False)
```

---

#### `pm4py.llm.explain_powl()`

**Signature:**
```python
explain_powl(
    powl_model,
    lm: Optional[Any] = None
) -> str
```

**Parameters:**
- `powl_model` (POWL) - The model to explain
- `lm` (dspy.LM, optional) - DSPy language model (uses `dspy.settings.lm` if None)

**Returns:** Natural language explanation with reasoning

**Requirements:** DSPy installed, LM configured

**Example:**
```python
import dspy
dspy.settings.configure(lm=dspy.OpenAI(model="gpt-4", api_key="..."))
explanation = pm4py.llm.explain_powl(powl_model)
```

---

#### `pm4py.llm.discover_powl_from_description()`

**Signature:**
```python
discover_powl_from_description(
    process_description: str,
    lm: Optional[Any] = None
) -> str
```

**Parameters:**
- `process_description` (str) - Natural language process description
- `lm` (dspy.LM, optional) - DSPy language model (uses `dspy.settings.lm` if None)

**Returns:** POWL model string (parse with `pm4py.objects.powl.parser.parse_powl_model_string()`)

**Requirements:** DSPy installed, LM configured

**Example:**
```python
powl_str = pm4py.llm.discover_powl_from_description("A process that starts with...")
powl_model = pm4py.objects.powl.parser.parse_powl_model_string(powl_str)
```

---

#### `pm4py.llm.compare_powl_models()`

**Signature:**
```python
compare_powl_models(
    powl_1,
    powl_2,
    lm: Optional[Any] = None
) -> Dict[str, Any]
```

**Parameters:**
- `powl_1` (POWL) - First model
- `powl_2` (POWL) - Second model
- `lm` (dspy.LM, optional) - DSPy language model (uses `dspy.settings.lm` if None)

**Returns:** Dictionary with keys:
- `"comparison"` (str) - Detailed structural comparison
- `"confidence"` (float) - Confidence score (0.0 to 1.0)

**Requirements:** DSPy installed, LM configured

**Example:**
```python
result = pm4py.llm.compare_powl_models(powl_1, powl_2)
print(result["comparison"])
```

---

### POWL String Syntax Reference

**Basic activity:**
```
A
```

**Silent transition (no label):**
```
tau
```

**Choice (exclusive):**
```
X(A, B)  // Either A or B
X(A, B, C)  // Either A, B, or C
```

**Loop:**
```
*(A, B)  // Do A, then loop back and repeat with B, exit when done
```

**Partial order:**
```
PO=(
  nodes={A, B, C},
  order={A-->B, A-->C}
)
```
Meaning: A executes first, then B and C in parallel (independent)

**Nested structures:**
```
PO=(
  nodes={
    A,
    X(B, C),
    *(D, E)
  },
  order={A-->X(B,C), X(B,C)-->*(D,E)}
)
```

---

### Environment Variables & Configuration

**For LLM connectors:**

Set these in your shell or `.env` file:
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="..."
```

**For DSPy configuration:**

```python
import dspy

# OpenAI
dspy.settings.configure(lm=dspy.OpenAI(model="gpt-4", api_key="..."))

# Anthropic
dspy.settings.configure(lm=dspy.Anthropic(model="claude-3-5-sonnet-20241022", api_key="..."))

# Google Gemini
dspy.settings.configure(lm=dspy.GoogleVertexAI(model="gemini-2.5-flash", api_key="..."))
```

---

### Troubleshooting

**Error: ModuleNotFoundError: No module named 'dspy'**

Install DSPy:
```bash
pip install dspy-ai
```

**Error: dspy.settings.lm is not set**

Configure a language model before calling DSPy functions:
```python
import dspy
dspy.settings.configure(lm=dspy.OpenAI(model="gpt-4", api_key="..."))
```

**Error: POWL parse error**

The generated POWL string may have syntax issues. Inspect and fix:
```python
try:
    powl = pm4py.objects.powl.parser.parse_powl_model_string(powl_string)
except Exception as e:
    print(f"Parse error: {e}")
    print(f"String was: {powl_string}")
    # Ask LLM to fix the format
```

**LLM produces incorrect POWL syntax**

Try a more specific prompt:
```python
description = """
Invoice process:
1. Receive invoice
2. Either auto-approve (if <€500) or send to manager
3. Pay invoice
4. Archive

Format as: PO=(nodes={...}, order={...})
Use activity names without spaces.
"""

powl_str = pm4py.llm.discover_powl_from_description(description)
```

---

### Further Reading

- **POWL Discovery**: `pm4py.discover_powl()` with variants (brute force, maximal order, dynamic clustering)
- **POWL Conversion**: Convert to/from Petri nets, process trees
- **POWL Visualization**: `pm4py.view_powl()` with basic and net variants
- **Process Tree Parsing**: `pm4py.objects.process_tree.obj.ProcessTree`
- **DSPy Documentation**: https://github.com/stanfordnlp/dspy (external)

