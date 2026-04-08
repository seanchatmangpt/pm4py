# PM4Py SaaS Platform — Quick Start Guide

**Get started with PM4Py process mining in under 5 minutes.**

---

## What is PM4Py SaaS?

PM4Py SaaS is a cloud-native process mining platform that helps you discover, analyze, and improve business processes from your event data.

**Key Features:**
- 🔄 Process discovery from event logs
- 📊 Conformance checking and deviation analysis
- 🚨 Real-time drift detection
- 🤖 AI-assisted process design (describe → execute)
- 🏢 Industry-specific verticals (Finance, Healthcare, Manufacturing)
- 🔒 SOC2-compliant security

---

## 5-Minute Quick Start

### Step 1: Sign Up

1. Go to [app.pm4py.com](https://app.pm4py.com)
2. Click "Start Free Trial"
3. Choose your plan:
   - **Starter** ($49/mo): For individuals and small teams
   - **Professional** ($199/mo): For growing teams
   - **Enterprise** (Custom): For large organizations

### Step 2: Upload Your Data

PM4Py accepts event logs in these formats:

| Format | Extension | Best For |
|--------|-----------|----------|
| XES | `.xes` | Standard event logs |
| CSV | `.csv` | Excel exports |
| Pandas DataFrame | Python | Programmatic access |
| JSON | `.json` | API integrations |

**CSV Format Requirements:**
```csv
case_id,activity,timestamp
order_1,Order Received,2024-01-01 09:00:00
order_1,Payment Verified,2024-01-01 09:05:00
order_1,Order Shipped,2024-01-01 09:30:00
order_2,Order Received,2024-01-01 10:00:00
...
```

### Step 3: Discover Your Process

```python
import pm4py

# Load your event log
log = pm4py.read_csv("my_process.csv")

# Discover the process model
model = pm4py.discover_powl(log)

# Visualize
pm4py.view_powl(model)
```

### Step 4: Analyze

```python
# Check conformance
replay = pm4py.conformance_diagnostics_token_based_replay(log, model)
print(f"Fitness: {replay['average_trace_fitness']}")

# Find bottlenecks
from pm4py.algo.discovery.bubbles import discover_bubbles
bottlenecks = discover_bubbles(log)
```

---

## Onboarding Checklist

- [ ] **Account Setup**: Complete registration
- [ ] **First Upload**: Import your first event log
- [ ] **Process Discovery**: Generate your first process model
- [ ] **Visualization**: Save and share your first visualization
- [ ] **Conformance Check**: Run your first compliance analysis
- [ ] **Team Invite**: Add your team members
- [ ] **API Access**: Generate your API key

---

## Next Steps

### Learn the Basics

- **[Tutorial 1: Process Discovery](tutorial1-discovery.md)** — Learn to discover process models
- **[Tutorial 2: Conformance Checking](tutorial2-conformance.md)** — Validate compliance
- **[Tutorial 3: Bottleneck Analysis](tutorial3-bottlenecks.md)** — Find inefficiencies

### Industry Verticals

- **[Finance Vertical](../verticals/finance/)** — Trade workflows, SOC2 compliance
- **[Healthcare Vertical](../verticals/healthcare/)** — Patient journeys, HIPAA compliance
- **[Manufacturing Vertical](../verticals/manufacturing/)** — OEE analysis, IIoT integration

### Advanced Features

- **[Real-Time Drift Detection](../advanced/drift-detection.md)** — Monitor process changes
- **[AI Process Design](../advanced/ai-design.md)** — Describe workflow, get executable code
- **[API Reference](../api/reference.md)** — Complete API documentation

---

## Getting Help

| Resource | Link |
|----------|------|
| Documentation | docs.pm4py.com |
| Community Discord | discord.gg/pm4py |
| GitHub Issues | github.com/pm4py/pm4py/issues |
| Support Email | support@pm4py.com |
| Status Page | status.pm4py.com |

---

## Pricing

| Plan | Price | Events/Month | Features |
|------|-------|--------------|----------|
| **Starter** | $49/mo | 100K | Basic discovery, visualizations |
| **Professional** | $199/mo | 1M | + Conformance, drift detection, verticals |
| **Enterprise** | Custom | Unlimited | + SOC2, SLA, dedicated support |

See [Pricing](../pricing.md) for details.

---

## Security & Compliance

PM4Py SaaS is SOC2 Type II certified and GDPR compliant.

- **Data Encryption**: All data encrypted at rest and in transit
- **Access Control**: MFA and RBAC required
- **Audit Logging**: Complete audit trail for all actions
- **Data Residency**: EU, US, and APAC regions available

---

**Ready to start?** [Sign up now](https://app.pm4py.com/signup) →
