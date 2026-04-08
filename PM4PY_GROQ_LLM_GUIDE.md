# PM4Py + Groq LLM Integration Guide

## Overview

PM4Py has **comprehensive built-in LLM support** through `pm4py.llm`. This guide shows how to use Groq's fast inference with PM4Py.

## PM4Py LLM Architecture

```
pm4py.llm
├── connectors/          # LLM provider integrations
│   ├── openai.py       # OpenAI/GPT-compatible
│   ├── anthropic.py    # Claude
│   ├── google.py       # Gemini
│   └── groq.py         # Groq (NEW!)
├── abstractions/       # Convert PM data to LLM prompts
│   ├── log_to_dfg_descr.py      # Event log → DFG text
│   ├── log_to_variants_descr.py # Event log → variants text
│   ├── log_to_cols_descr.py     # Event log → schema text
│   └── ocel_*.py                # OCEL abstractions
└── injection/          # Inject PM knowledge into prompts
    ├── pm_knowledge/    # Process mining domain knowledge
    └── db_knowledge/    # Database schema knowledge
```

## Quick Start

### 1. Basic Groq Query

```python
import pm4py

# Simple query
response = pm4py.llm.groq_query("What is process mining?")
print(response)

# With specific model
response = pm4py.llm.groq_query(
    "Explain token-based replay",
    model="gpt-oss-20b"  # Fast & best value
)
```

### 2. Process Abstraction + Analysis

```python
import pm4py

# Load event log
log = pm4py.read_xes("running-example.xes")

# Abstract process to text
dfg_text = pm4py.llm.abstract_dfg(log)

# Query Groq with process context
prompt = f"Analyze this process:\n\n{dfg_text}\n\nWhat are the bottlenecks?"
response = pm4py.llm.groq_query(prompt)
print(response)
```

### 3. LLM-Powered Clustering

```python
# Automatic trace clustering
clusters = pm4py.llm.clustering(
    log,
    executor=pm4py.llm.groq_query
)

for name, df in clusters:
    print(f"{name}: {len(df)} cases")
```

### 4. Using GPT-OSS-20B (Best Value!)

```python
response = pm4py.llm.groq_query(
    "Explain conformance checking",
    model="openai/gpt-oss-20b",
    custom_llm_provider="groq"  # Required for openai/* models
)
```

## Groq Models Comparison

| Model | TPS | Input Cost | Output Cost | Best For |
|-------|-----|-----------|-------------|----------|
| **GPT-OSS-20B** | 1000 | $0.075/M | $0.30/M | **Best value** (recommended) |
| **GPT-OSS-120B** | 500 | $0.15/M | $0.60/M | High quality |
| **GPT-OSS Safeguard 20B** | 1000 | $0.075/M | $0.30/M | Safety-focused |

## Available PM4Py LLM Functions

### Query Functions
- `pm4py.llm.groq_query(prompt, model, api_key)` - Direct Groq query
- `pm4py.llm.openai_query(prompt, model, api_key)` - OpenAI query
- `pm4py.llm.anthropic_query(prompt, model, api_key)` - Claude query
- `pm4py.llm.google_query(prompt, model, api_key)` - Gemini query

### Abstraction Functions
- `abstract_dfg(log)` - Convert log to DFG description
- `abstract_variants(log)` - Convert log to variants description
- `abstract_ocel(ocel)` - Convert OCEL to text
- `abstract_log_attributes(log)` - Get log schema
- `abstract_petri_net(net, im, fm)` - Describe Petri net

### Analysis Functions
- `clustering(log, executor)` - LLM-based trace clustering
- `automated_hypotheses_formulation(log, executor)` - Generate hypotheses
- `nlp_to_log_query(log, query, executor)` - Natural language to SQL
- `explain_visualization(vis_func, ...)` - Explain graphs

## Example: End-to-End Workflow

```python
import pm4py

# 1. Load data
log = pm4py.read_xes("running-example.xes")

# 2. Discover process model
net, im, fm = pm4py.discover_petri_net_inductive(log)

# 3. Abstract for LLM
process_desc = pm4py.llm.abstract_petri_net(net, im, fm)

# 4. Query Groq for insights
response = pm4py.llm.groq_query(
    f"Analyze this process model and suggest improvements:\n\n{process_desc}",
    model="openai/gpt-oss-20b",
    custom_llm_provider="groq"
)

print(response)
```

## Environment Setup

```bash
# Set your Groq API key
export GROQ_API_KEY="gsk_..."

# Install PM4Py with dependencies
pip install pm4py

# Or use the virtual environment we created
source .venv/bin/activate
```

## Files Added

| File | Purpose |
|------|---------|
| `pm4py/algo/querying/llm/connectors/groq.py` | Groq connector |
| `pm4py/llm.py` | Added `groq_query()` function |
| `test_pm4py_groq.py` | Integration tests |

## Test Results

```
✅ Test 1: Basic Groq Query - PASSED
✅ Test 2: Groq with Process Abstraction - PASSED
✅ Test 3: Groq-based Clustering - PASSED (4 clusters found)
✅ Test 4: GPT-OSS-20B Integration - PASSED
```

## Key Benefits

1. **Fast Inference** - Groq's speed (up to 1000 TPS)
2. **Cost Effective** - GPT-OSS-20B: $0.075/M input tokens
3. **Native Integration** - Works with PM4Py's abstractions
4. **Flexible** - Use any Groq model via `model` parameter

## References

- [PM4Py Documentation](https://pm4py.fit.fraunhofer.de/)
- [Groq Documentation](https://console.groq.com/docs)
- [Process Mining Book](https://www.processmining.org/)
