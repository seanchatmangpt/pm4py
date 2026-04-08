# Finance Vertical — Examples

This directory contains example scripts demonstrating the Finance vertical's capabilities.

## Quick Start

```python
import pm4py
from pm4py.verticals import FinanceVertical

# Generate demo trade data
log = FinanceVertical.generate_demo_data(n_trades=1000)

# Initialize the vertical
vertical = FinanceVertical(log)

# Discover trade workflow model
model = vertical.discover_trade_workflow()

# Check SOC2 compliance
compliance = vertical.check_soc2_compliance()
print(f"Compliance Score: {compliance['compliance_score']}%")

# Analyze trading risks
risks = vertical.analyze_risks()

# Generate regulatory report
report = vertical.generate_regulatory_report()
```

## Examples

### 1. Basic Trade Discovery (`basic_discovery.py`)
Discover and visualize trade workflow models.

### 2. SOC2 Compliance Check (`soc2_compliance.py`)
Validate SOC2 compliance for trade workflows.

### 3. Regulatory Reporting (`regulatory_reporting.py`)
Generate MiFID II and Reg NMS compliant reports.

### 4. Risk Analysis (`risk_analysis.py`)
Analyze trading patterns and detect risks.

### 5. Compliance Testing (`compliance_testing.py`)
Test with data containing intentional violations.

## Scenarios

The Finance vertical supports several demo scenarios:

- **Normal**: Standard compliant trades
- **High Volume**: Peak trading periods
- **Risky**: Potential compliance issues
- **Cross Border**: Multi-jurisdiction trades
- **Algo Trading**: Algorithmic trading patterns
- **Market Close**: End-of-day rush
- **Compliance Violations**: Intentional violations for testing

## Data Schema

Trade workflow events include:

### Core XES Attributes
- `concept:name`: Activity name
- `time:timestamp`: Event timestamp
- `case:concept:name`: Trade/order ID

### Trade Attributes
- `trade:Id`: Unique trade identifier
- `trade:instrument`: Financial instrument symbol
- `trade:trader`: Trader ID
- `trade:desk`: Trading desk
- `trade:venue`: Execution venue
- `trade:type`: Trade type (Market, Limit, etc.)
- `trade:side`: BUY or SELL
- `trade:price`: Execution price
- `trade:quantity`: Quantity
- `trade:notional`: Notional value
- `trade:asset_class`: Asset class

### SOC2 Attributes
- `soc2:access_control`: Access control mechanism (MFA, RBAC, etc.)
- `soc2:encryption`: Data encryption enabled
- `soc2:audit_log`: Audit trail entries
- `soc2:change_management`: Change management record
- `soc2:data_classification`: Data classification level
- `soc2:compliance_monitoring`: Continuous monitoring enabled

### Regulatory Attributes (MiFID II, Reg NMS)
- `reg:transaction_id`: Unique transaction identifier
- `reg:execution_timestamp`: Execution timestamp
- `reg:venue`: Execution venue
- `reg:revenue`: Transaction revenue
- `reg:best_execution`: Best execution policy followed
