# PM4Py Finance Vertical

SOC2-ready trade workflow mining with pre-built schemas, regulatory reporting, and risk detection.

## Features

- **Trade Workflow Discovery**: Discover end-to-end trade lifecycles from order to settlement
- **SOC2 Compliance Checking**: Verify compliance with SOC2 Trust Services Criteria
- **Regulatory Reporting**: Validate MiFID II, Reg NMS, and Dodd-Frank reporting requirements
- **Risk Detection**: Identify unusual trading patterns, concentration risk, and operational risks
- **Audit Trail Generation**: Export complete audit trails for regulatory examinations

## Installation

```bash
# Install with finance dependencies
pip install pm4py[finance]

# Or install from source
cd pm4py
pip install -e .
```

## Quick Start

```python
import pm4py
from pm4py.verticals import FinanceVertical

# Generate demo trade data
log = FinanceVertical.generate_demo_data(n_trades=1000)

# Initialize the vertical
vertical = FinanceVertical(log)

# Discover trade workflow
model = vertical.discover_trade_workflow()
vertical.visualize_trade_flow()

# Check SOC2 compliance
compliance = vertical.check_soc2_compliance()
print(f"Compliance Score: {compliance['compliance_score']}%")

# Analyze risks
risks = vertical.analyze_risks()
print(f"High Risk Trades: {risks['high_risk_count']}")

# Generate regulatory report
report = vertical.generate_regulatory_report(report_type="trade_reconstruction")
```

## Event Schema

### Required Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `concept:name` | string | Activity name (see TRADE_ACTIVITIES) |
| `time:timestamp` | datetime | Event timestamp with microsecond precision |
| `case:concept:name` | string | Order/Case ID |
| `trade:Id` | string | Unique trade identifier |
| `trade:instrument` | string | Financial instrument (ticker, ISIN) |

### Trade Activities

**Pre-trade:**
- `order_received` - Order received from client
- `order_validation` - Order validation
- `pre_trade_compliance` - Pre-trade compliance check
- `risk_check` - Risk management check
- `limit_check` - Position limit check
- `credit_check` - Credit check

**Execution:**
- `order_routing` - Order routing to venue
- `order_submission` - Order submission to market
- `execution` - Trade execution
- `partial_fill` - Partial fill
- `fill` - Order fill

**Post-trade:**
- `trade_confirmation` - Trade confirmation
- `post_trade_verification` - Post-trade verification
- `clearing` - Clearing
- `settlement` - Settlement

**Reporting:**
- `trade_reporting` - Regulatory trade reporting
- `client_reporting` - Client reporting

### SOC2 Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `soc2:access_control` | string | Yes | Access control (MFA, RBAC, SAML, LDAP) |
| `soc2:encryption` | boolean | Yes | Data encryption at rest and in transit |
| `soc2:audit_log` | list | Yes | Complete audit trail |
| `soc2:data_classification` | string | Yes | Data classification level |

### Regulatory Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `reg:transaction_id` | string | Yes | Unique transaction identifier (MiFID II) |
| `reg:execution_timestamp` | datetime | Yes | Execution timestamp with microseconds |
| `reg:revenue` | numeric | Yes | Transaction revenue |
| `reg:best_execution` | boolean | Yes | Best execution policy indicator |
| `reg:execution_venue` | string | Yes | Execution venue |
| `reg:short_selling_indicator` | boolean | Yes | Short selling indicator (MiFIR) |

## Usage Examples

### SOC2 Compliance Checking

```python
from pm4py.verticals.finance.conformance import SOC2ConformanceChecker

checker = SOC2ConformanceChecker()
report = checker.check(log, criteria="security")

print(f"Status: {report['status']}")
for violation in report['violations']:
    print(f"  - {violation['description']}")
```

### Trade Reconstruction

```python
# Reconstruct complete trade lifecycle
trades = vertical.reconstruct_trades(trade_ids=["ORDER_00000001"])

for trade in trades:
    print(f"Trade: {trade['trade_id']}")
    print(f"  Duration: {trade['duration_seconds']:.2f} seconds")
    print(f"  Activities: {' → '.join(trade['activities'])}")
```

### Risk Analysis

```python
risks = vertical.analyze_risks(risk_type="all", threshold=0.7)

for alert in risks['alerts']:
    print(f"[{alert['severity']}] {alert['type']}")
    print(f"  {alert['description']}")
    print(f"  Recommendation: {alert['recommendation']}")
```

### Unusual Pattern Detection

```python
anomalies = vertical.detect_unusual_patterns()

for anomaly in anomalies:
    print(f"[{anomaly['severity']}] {anomaly['type']}")
    print(f"  {anomaly['description']}")
```

### Regulatory Report Generation

```python
# Trade reconstruction report
report = vertical.generate_regulatory_report(
    report_type="trade_reconstruction",
    date_range=("2024-01-01", "2024-01-31")
)

# Export for audit
vertical.export_for_audit("audit_export.json", include_phi=False)
```

## Running the Demo

```bash
# Run the finance demo
python -m pm4py.verticals.finance
```

The demo will:
1. Generate 1000 synthetic trades
2. Discover the trade workflow model
3. Run SOC2 compliance checks
4. Analyze trading risks
5. Generate regulatory reports
6. Save visualizations and reports

## Supported Regulations

- **MiFID II**: Markets in Financial Instruments Directive (EU)
- **Reg NMS**: Regulation National Market System (US)
- **Dodd-Frank**: Wall Street Reform and Consumer Protection Act (US)
- **MiFIR**: Markets in Financial Instruments Regulation (EU)
- **MAR**: Market Abuse Regulation (EU)

## Risk Metrics

The finance vertical analyzes the following risk types:

| Risk Type | Description | Threshold |
|-----------|-------------|-----------|
| Market Risk | Value at Risk (VaR) | Daily VaR > 1% of portfolio |
| Concentration Risk | Single position concentration | Position > 10% of portfolio |
| Liquidity Risk | Order size vs average daily volume | Order > 20% of ADV |
| Operational Risk | Failed trades, rapid execution | Failure rate > 1% |
| Compliance Risk | Pre/post-trade check failures | Any failure |

## Data Export

### Audit Export

```python
vertical.export_for_audit(
    output_path="audit_export.json",
    include_phi=False  # Exclude personally identifiable information
)
```

### Regulatory Report

```python
report = vertical.generate_regulatory_report(
    report_type="trade_reconstruction"  # or "audit_trail", "risk_summary"
)
```

## License

Apache License 2.0 - Copyright (C) 2026 Process Intelligence Solutions GmbH

## References

- SOC2 Trust Services Criteria: https://www.aicpa.org/soc4so
- MiFID II: https://www.esma.europa.eu/law/mifid-ii-mifir
- Reg NMS: https://www.sec.gov/rules/final/34-51818.pdf
