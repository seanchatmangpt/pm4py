# Business Analyst Guide to Process Discovery

**Describe your workflow, get executable code.**

This guide shows you how to turn plain English process descriptions into working workflows—no data science required.

---

## What is Process Discovery?

Process discovery is the art of understanding how work gets done in your organization and capturing it in a format that computers can execute.

**Before:** "We handle customer orders by checking inventory, picking items, and shipping them."

**After:** An executable workflow that your team can run automatically.

---

## The Simple Way: Describe and Generate

### Step 1: Describe Your Process

Write down how your process works in plain English. Be specific about:

1. **What happens first?** (e.g., "Customer submits an order")
2. **What happens next?** (e.g., "Check if items are in stock")
3. **Are there decisions?** (e.g., "If in stock, pick items. If out of stock, notify customer.")
4. **Are there loops?** (e.g., "If documents are incomplete, request more and resubmit.")
5. **What happens last?** (e.g., "Archive the order record.")

### Step 2: Run the Discovery

```python
import pm4py

# Your process description
description = """
A bank processes loan applications. The customer submits an application.
A clerk reviews the documents. If the documents are incomplete, the clerk
requests additional documents and the customer resubmits. Once documents
are complete, the clerk forwards to an underwriter. The underwriter either
approves or rejects the loan. If approved, funds are disbursed and the
case is closed. If rejected, a rejection letter is sent and the case is closed.
"""

# Generate the workflow
result = pm4py.discover_from_text(description)

# Check if it's valid
if result['verdict']:
    print("✓ Process model is valid!")
    print(f"POWL Model: {result['powl']}")
else:
    print(f"✗ Issues found: {result['reasoning']}")
```

### Step 3: Get Executable Code

```python
# Generate code for your favorite platform
from pm4py.algo.dspy.powl import generate_from_text

code_result = generate_from_text(
    description,
    workflow_name="Loan Approval",
    formats=['n8n', 'temporal', 'bpmn', 'yawl']
)

# Access generated code
print("n8n workflow:", code_result.n8n_json)
print("Temporal Go code:", code_result.temporal_go)
print("BPMN XML:", code_result.camunda_bpmn)
```

---

## Before and After Examples

### Example 1: Employee Onboarding

**Before (Plain English):**
> "New employees fill out paperwork while IT sets up their accounts. They complete tax forms, go through security training, then receive their badge access."

**After (Executable POWL):**
```
PO=( nodes={
  'Accept Offer',
  'Prepare Paperwork',
  'Setup IT Accounts',
  'Complete I-9',
  'Security Training',
  'Get Badge'
}, order={
  'Accept Offer' --> 'Prepare Paperwork',
  'Accept Offer' --> 'Setup IT Accounts',
  'Prepare Paperwork' --> 'Complete I-9',
  'Setup IT Accounts' --> 'Security Training',
  'Security Training' --> 'Get Badge'
})
```

**After (n8n Workflow JSON):**
```json
{
  "name": "Employee Onboarding",
  "nodes": [
    {"id": "start", "name": "Start", "type": "manualTrigger"},
    {"id": "paperwork", "name": "Prepare Paperwork", "type": "manualTrigger"},
    {"id": "it", "name": "Setup IT Accounts", "type": "manualTrigger"},
    ...
  ]
}
```

---

### Example 2: Customer Support Tickets

**Before (Plain English):**
> "Customers submit support tickets. We categorize them as billing, technical, or general issues. The specialist tries to resolve on first contact. If resolved, we close and survey the customer. If not resolved, we escalate to tier 2 support."

**After (Executable Process):**
- Clear routing based on ticket category
- First contact resolution attempt
- Escalation path for unresolved issues
- Closure and customer feedback loop

---

## Understanding the Generated Model

Your process gets converted to POWL (Partially Ordered Workflow Language)—a simple but powerful notation:

| Symbol | Meaning | Example |
|--------|---------|--------|
| `'Activity Name'` | A single step | `'Submit Application'` |
| `X(A, B)` | **Either A OR B** (exclusive choice) | `X('Approve', 'Reject')` |
| `*(A, B)` | **Do A, then possibly B** (loop) | `*('Process', 'Retry')` |
| `PO=(nodes={A, B}, order={A-->B})` | **A and B** with A before B (sequence) | Parallel tasks with ordering |

---

## Common Patterns

### Pattern 1: Approval Workflow

```
Submit → Review → X(Approve, Reject) → X(Disburse, Notify) → Close
```

**Use for:** Expense reports, purchase orders, time-off requests

### Pattern 2: Retry Loop

```
Submit → Check → X(Pass, *('Request Fix', Check)) → Complete
```

**Use for:** Document validation, quality checks, data entry

### Pattern 3: Parallel Activities

```
Start → Task A → Join → End
       ↘ Task B ↗
```

**Use for:** Multi-department approvals, simultaneous reviews

### Pattern 4: Multi-Level Escalation

```
Tier 1 → X(Resolve, Escalate) → Tier 2 → X(Resolve, Escalate) → Tier 3
```

**Use for:** Support tickets, incident management, compliance reviews

---

## Export Formats

### n8n JSON
- **Best for:** No-code/low-code automation
- **Import to:** n8n.io workflow automation
- **Output:** JSON file ready for import

### Temporal Go Code
- **Best for:** Production microservices orchestration
- **Import to:** Go applications using Temporal
- **Output:** Go source code with workflow definitions

### Camunda BPMN
- **Best for:** Business process management platforms
- **Import to:** Camunda, Signavio, Bizagi
- **Output:** BPMN 2.0 XML file

### YAWL XML
- **Best for:** Complex workflow patterns
- **Import to:** YAWL engine, academic research tools
- **Output:** YAWL specification XML

---

## Tips for Better Results

### 1. Be Specific About Activities

❌ "Then someone reviews it"
✅ "A manager reviews the documents"

### 2. Clearly State Decision Points

❌ "Depending on the outcome..."
✅ "If approved, proceed to payment. If rejected, send rejection letter."

### 3. Mention All Possible Endings

❌ "Then we're done"
✅ "The process ends when either approved (close case) or rejected (close case)."

### 4. Describe Loops Explicitly

❌ "This might repeat"
✅ "If documents are incomplete, request additional documents and customer resubmits."

---

## Quick Reference Commands

```python
# Basic discovery
import pm4py
result = pm4py.discover_from_text("Your process description here")

# With specific model (faster)
result = pm4py.discover_from_text(description, model="groq/openai/gpt-oss-20b")

# Generate specific format only
code = pm4py.algo.dspy.powl.generate_from_text(
    description,
    formats=['n8n']  # or ['temporal'], ['bpmn'], ['yawl']
)

# Save n8n workflow
import json
with open('workflow.json', 'w') as f:
    json.dump(code.n8n_json, f, indent=2)

# Save BPMN
with open('process.bpmn', 'w') as f:
    f.write(code.camunda_bpmn)
```

---

## Troubleshooting

### "My process wasn't captured correctly"

**Solution:** Add more detail about the problematic step. Instead of "Then it gets approved," say "The manager reviews and either approves or rejects."

### "I got an error about dead ends"

**Solution:** Make sure every branch of your process has an ending. If you have an "if rejected" branch, explain what happens after rejection.

### "The loop isn't working"

**Solution:** Explicitly mention what causes repetition. Use phrases like "If X fails, retry X up to 3 times."

### "I want parallel activities"

**Solution:** Use "while" or "simultaneously" language. "While A prepares paperwork, B sets up accounts."

---

## Getting Help

- **Documentation:** https://processintelligence.solutions
- **GitHub:** https://github.com/process-intelligence/pm4py
- **Community:** Join the pm4py Discord for questions

---

**Remember:** The system learns from examples. The more clearly you describe your process, the better the generated workflow will be!
