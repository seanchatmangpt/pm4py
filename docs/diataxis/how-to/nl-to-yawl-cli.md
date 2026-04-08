# Export Process Models from Natural Language to YAWL

> Generate verified, executable YAWL models from plain English descriptions.

---

## Prerequisites

- Python 3.9+ installed
- pm4py library installed: `pip install pm4py`
- Optional: Groq API key for faster generation (uses default free tier otherwise)

---

## Method 1: Using the CLI (Recommended)

### Export from Text Description

```bash
python -m pm4py.cli DiscoverPOWLToYAWL \
  "A customer submits a support ticket. The system categorizes by urgency. High urgency tickets are escalated to senior agents. Low urgency tickets are handled by junior agents." \
  support_process.yawl
```

**Output:**
```
YAWL model (VERIFIED) written to support_process.yawl
```

The CLI automatically:
1. Generates a POWL model from your description using AI
2. Verifies the model is structurally sound (deadlock-free, live, bounded)
3. Converts to YAWL XML format
4. Writes to the specified file

### Export from a File

Put your process description in a text file:

```bash
# process_description.txt
Patients arrive at the emergency department and are triaged by severity.
Critical patients go immediately to treatment.
Serious patients wait for specialist consultation.
Minor patients are routed to general practitioner.
All treated patients are discharged.
```

Then:

```bash
python -m pm4py.cli DiscoverPOWLToYAWL \
  process_description.txt \
  ed_triage.yawl
```

---

## Method 2: Using Python API

### Step-by-Step Export

```python
import pm4py
from pm4py.algo.dspy.powl.natural_language import generate_powl_from_text
from pm4py.objects.powl.parser import parse_powl_model_string

# 1. Generate POWL from natural language
description = """
A loan application is submitted.
The system checks the credit score.
If score > 700, auto-approve.
If score 500-700, manual review.
If score < 500, reject.
"""

result = generate_powl_from_text(description, max_refinements=1)

# 2. Parse the POWL string
powl_model = parse_powl_model_string(result["powl"])

# 3. Convert to YAWL
yawl_spec = pm4py.convert_to_yawl(powl_model)

# 4. Write to file
pm4py.write_yawl(yawl_spec, "loan_approval.yawl")

# 5. Check verification status
status = "VERIFIED" if result["verdict"] else "NOT VERIFIED"
print(f"Model status: {status}")
```

### From Event Log to YAWL

```python
import pm4py

# 1. Discover POWL from event log
log = pm4py.read_xes("running-example.xes")
powl_model = pm4py.discover_powl(log)

# 2. Export to YAWL
pm4py.write_yawl(powl_model, "discovered_process.yawl")
```

---

## Customize Generation Parameters

### Control Refinement Iterations

```python
result = generate_powl_from_text(
    description,
    max_refinements=3  # Allow up to 3 refinement cycles
)
```

### Specify LLM Provider

```python
# Configure before calling generate_powl_from_text
import os
os.environ["GROQ_API_KEY"] = "your-api-key-here"

# Use Groq with Llama 3 70B (fast, free tier)
result = generate_powl_from_text(
    description,
    lm_config="groq/llama-3-70b-8192"
)
```

---

## Verify Model Soundness Before Export

```python
from pm4py.algo.dspy.powl.judge import judge_powl

# Generate POWL model
result = generate_powl_from_text(description, max_refinements=1)
powl_model = parse_powl_model_string(result["powl"])

# Judge before exporting
judgment = judge_powl(powl_model)

print(f"Soundness: {judgment['is_sound']}")
print(f"Reasoning: {judgment['reasoning']}")

# Only export if verified
if judgment['is_sound']:
    pm4py.write_yawl(powl_model, "verified_process.yawl")
```

---

## Common Patterns

### E-Commerce Checkout Flow

```python
description = """
Customer adds items to shopping cart.
Customer proceeds to checkout.
System validates inventory.
If items in stock, process payment.
If items out of stock, notify customer and cancel order.
After payment, ship items and send confirmation.
"""

result = generate_powl_from_text(description, max_refinements=1)
powl_model = parse_powl_model_string(result["powl"])
pm4py.write_yawl(powl_model, "checkout.yawl")
```

### Software Deployment Pipeline

```python
description = """
Developer pushes code to repository.
CI/CD pipeline triggers automatically.
Run unit tests.
If tests pass, run integration tests.
If all tests pass, deploy to staging.
Run smoke tests on staging.
If smoke tests pass, promote to production.
Monitor for issues and rollback if needed.
"""

result = generate_powl_from_text(description, max_refinements=1)
powl_model = parse_powl_model_string(result["powl"])
pm4py.write_yawl(powl_model, "deployment.yawl")
```

### Healthcare Patient Journey

```python
description = """
Patient arrives at hospital reception.
Patient registers and provides insurance information.
Receptionist verifies insurance coverage.
If insurance valid, patient proceeds to triage.
Triage nurse assesses severity and assigns priority.
Patient waits for doctor consultation.
Doctor examines patient and orders treatment if needed.
Treatment is administered and patient is discharged.
If condition worsens, patient is readmitted.
"""

result = generate_powl_from_text(description, max_refinements=1)
powl_model = parse_powl_model_string(result["powl"])
pm4py.write_yawl(powl_model, "patient_journey.yawl")
```

---

## Troubleshooting

### "Model generation failed"

**Problem:** The LLM cannot parse your description.

**Solution:**
- Break down complex processes into simpler descriptions
- Use clear, step-by-step language
- Avoid ambiguous pronouns ("it", "they") - use specific nouns instead
- Specify decision conditions explicitly ("If X, then Y")

Example:
```
Bad: "It checks if they are eligible and then processes."

Good: "The system checks if customer credit score > 700. 
       If score > 700, then process payment."
```

### "Model NOT VERIFIED"

**Problem:** Generated model fails soundness verification.

**Solution:**
- Check the reasoning: `result['reasoning']`
- Common issues: deadlock potential, missing termination
- Add more explicit structure to your description
- Try `max_refinements=2` for more correction cycles

### YAWL file is empty

**Problem:** Export succeeded but file is empty.

**Solution:**
- Check that the POWL model has activities (not all silent transitions)
- Verify the model parses correctly: `print(powl_model)`
- Check file permissions and disk space

---

## Related How-To Guides

- [Export from BPMN to YAWL](bpmn-to-yawl.md)
- [Export from Event Logs to YAWL](logs-to-yawl.md)
- [Import YAWL Files and Verify](import-yawl.md)
