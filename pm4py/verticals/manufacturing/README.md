# PM4Py Manufacturing Vertical

IIoT-ready manufacturing process mining with OEE calculation, quality conformance, and real-time equipment monitoring.

## Overview

The Manufacturing Vertical provides industry-specific templates for analyzing production workflows, calculating Overall Equipment Effectiveness (OEE), monitoring quality conformance, and detecting bottlenecks in manufacturing processes.

### Key Features

- **OEE Calculation & Monitoring**: Track Availability, Performance, and Quality metrics
- **IIoT Integration**: OPC-UA adapter for real-time equipment data ingestion
- **Quality Conformance**: Defect rate analysis, inspection coverage, rework tracking
- **Bottleneck Detection**: Identify equipment and activity constraints
- **Real-time Monitoring**: Equipment status, active orders, and alerts
- **Production Standards**: Cycle time compliance and maintenance tracking

## Installation

```bash
# Basic installation
pip install pm4py

# With OPC-UA support for IIoT integration
pip install pm4py[manufacturing]
```

## Quick Start

### Generate Demo Data

```python
from pm4py.verticals.manufacturing import ManufacturingVertical

# Generate synthetic manufacturing data
log = ManufacturingVertical.generate_demo_data(
    n_orders=500,      # Number of production orders
    n_equipment=15,    # Number of equipment units
    n_products=20,     # Number of product types
)

# Initialize vertical
vertical = ManufacturingVertical(log)
```

### Discover Production Workflow

```python
# Discover the production process model
model = vertical.discover_production_workflow(variant="powl")

# Visualize the workflow
vertical.visualize_production_flow(format="png")
```

### Calculate OEE Metrics

```python
# Get comprehensive OEE analysis
oee_metrics = vertical.calculate_oee_metrics()

print(f"Overall OEE: {oee_metrics['overall_oee']['oee']}%")
print(f"Availability: {oee_metrics['overall_oee']['availability']}%")
print(f"Performance: {oee_metrics['overall_oee']['performance']}%")
print(f"Quality: {oee_metrics['overall_oee']['quality']}%")
```

### Check Conformance

```python
# OEE conformance against threshold
oee_report = vertical.check_oee_conformance(oee_threshold=60.0)
print(f"Status: {oee_report['status']}")
print(f"Violations: {oee_report['summary']['total_violations']}")

# Quality conformance
quality_report = vertical.check_quality_conformance(defect_threshold=5.0)
print(f"Compliant: {quality_report['compliant']}")
```

### Detect Bottlenecks

```python
# Identify process bottlenecks
bottlenecks = vertical.detect_bottlenecks(threshold_percentile=75)

# Activity bottlenecks
for bn in bottlenecks['activity_bottlenecks'][:5]:
    print(f"{bn['activity']}: {bn['avg_duration_seconds']:.1f}s avg")

# Equipment bottlenecks
for bn in bottlenecks['equipment_bottlenecks'][:5]:
    print(f"{bn['equipment']}: {bn['utilization_percent']:.1f}% utilization")
```

## OEE (Overall Equipment Effectiveness)

### OEE Formula

```
OEE = Availability × Performance × Quality

Where:
- Availability = Run Time / Planned Production Time
- Performance = (Total Pieces × Ideal Cycle Time) / Run Time
- Quality = Good Pieces / Total Pieces
```

### OEE Standards

| Metric | World-Class | Acceptable |
|--------|-------------|------------|
| Availability | 90% | 80% |
| Performance | 95% | 85% |
| Quality | 99.9% | 95% |
| **OEE** | **85%** | **60%** |

### Calculate OEE

```python
from pm4py.verticals.manufacturing.schemas import calculate_oee

oee = calculate_oee(
    run_time=450,                    # Actual production time (minutes)
    planned_production_time=480,     # Planned available time (minutes)
    total_pieces=1000,               # Total pieces produced
    good_pieces=985,                 # Good pieces (passed quality)
    ideal_cycle_time=27,             # Ideal cycle time per piece (seconds)
)

print(f"OEE: {oee['oee']}%")  # 81.6%
```

## IIoT Integration with OPC-UA

### Connect to Equipment

```python
from pm4py.verticals.manufacturing.opcua_adapter import (
    OPCUAAdapter,
    OPCUANodeConfig,
    OEEConfig,
)

# Create adapter for OPC-UA server
adapter = OPCUAAdapter("opc.tcp://plc1.company.com:4840")

# Connect to server
if adapter.connect():
    print("Connected to OPC-UA server")
```

### Configure Sensor Nodes

```python
# Define nodes to monitor
nodes = [
    OPCUANodeConfig(
        node_id="ns=2;s=Temperature",
        display_name="Temperature",
        data_type="float",
        unit="°C",
        threshold_max=80,
    ),
    OPCUANodeConfig(
        node_id="ns=2;s=Pressure",
        display_name="Pressure",
        data_type="float",
        unit="bar",
        threshold_min=1,
        threshold_max=100,
    ),
]

adapter.add_node_config(nodes[0])
adapter.add_node_config(nodes[1])
```

### Collect Real-Time Data

```python
# Collect data for 60 seconds
log = adapter.collect_data(
    duration_seconds=60,
    sampling_interval_ms=1000,
    equipment_id="CNC-01",
)

# Process the event log
vertical = ManufacturingVertical(log)
oee_metrics = vertical.calculate_oee_metrics()

adapter.disconnect()
```

### Configure OEE Monitoring

```python
# Set up OEE calculation for equipment
oee_config = OEEConfig(
    equipment_id="CNC-01",
    ideal_cycle_time_seconds=45,
    planned_production_time_minutes=480,
    run_time_node="ns=2;s=RunTime",
    downtime_node="ns=2;s=Downtime",
    total_pieces_node="ns=2;s=TotalPieces",
    good_pieces_node="ns=2;s=GoodPieces",
)

adapter.add_equipment_config(oee_config)

# Get current OEE
oee = adapter.calculate_oee_from_nodes("CNC-01")
print(f"Current OEE: {oee['oee']}%")
```

## Manufacturing Event Schema

### Required Event Attributes

| Attribute | Description | Type |
|-----------|-------------|------|
| `concept:name` | Activity name | string |
| `time:timestamp` | Event timestamp | datetime |
| `case:concept:name` | Production order ID | string |
| `production:order_id` | Production order identifier | string |
| `production:product_id` | Product identifier | string |
| `equipment:id` | Equipment identifier | string |

### OEE Attributes

| Attribute | Description | Type |
|-----------|-------------|------|
| `oee:availability` | Availability percentage | float |
| `oee:performance` | Performance percentage | float |
| `oee:quality` | Quality percentage | float |
| `oee:oee` | Overall OEE | float |
| `oee:run_time` | Actual run time (minutes) | float |
| `oee:downtime` | Unplanned downtime (minutes) | float |
| `oee:total_pieces` | Total pieces produced | integer |
| `oee:good_pieces` | Good pieces | integer |
| `oee:defective_pieces` | Defective pieces | integer |

### Quality Attributes

| Attribute | Description | Type |
|-----------|-------------|------|
| `quality:status` | pass/fail/rework/scrap | string |
| `quality:defect_code` | Defect type | string |
| `quality:inspector` | Inspector ID | string |

### Equipment Attributes

| Attribute | Description | Type |
|-----------|-------------|------|
| `equipment:id` | Equipment identifier | string |
| `equipment:type` | CNC/Robot/Press/etc. | string |
| `equipment:status` | running/idle/maintenance/breakdown | string |
| `equipment:operator` | Operator ID | string |

## Command Line Demo

Run the built-in demo:

```bash
# Full demo with 500 orders
python -m pm4py.verticals.manufacturing

# Custom order count
python -m pm4py.verticals.manufacturing --orders 1000 --equipment 20

# OEE calculation demo only
python -m pm4py.verticals.manufacturing --mode oee

# Benchmark dataset comparison
python -m pm4py.verticals.manufacturing --mode benchmark

# Schema reference
python -m pm4py.verticals.manufacturing --mode schema
```

## Quick Analysis

For rapid comprehensive analysis:

```python
from pm4py.verticals.manufacturing import quick_analyze

results = quick_analyze(log)

# Access all analysis results
print(results['oee_conformance'])
print(results['quality_conformance'])
print(results['bottlenecks'])
print(results['real_time_status'])
```

## Production Reports

Generate various production reports:

```python
# OEE summary report
oee_report = vertical.generate_production_report("oee_summary")

# Quality report
quality_report = vertical.generate_production_report("quality_report")

# Equipment report
equipment_report = vertical.generate_production_report("equipment_report")
```

## Equipment Utilization

Analyze equipment utilization:

```python
utilization = vertical.analyze_equipment_utilization()

for equipment, stats in utilization.items():
    print(f"{equipment}:")
    print(f"  Running: {stats['running_percent']}%")
    print(f"  Orders: {stats['order_count']}")
```

## Real-Time Monitoring

Get current production status:

```python
status = vertical.get_real_time_status()

# Equipment status
print(f"Running: {status['equipment_status']['running']}")
print(f"Breakdown: {status['equipment_status']['breakdown']}")

# Active alerts
for alert in status['quality_alerts']:
    print(f"Quality alert: {alert['type']} - {alert['severity']}")

for alert in status['sensor_alerts']:
    print(f"Sensor alarm: {alert['sensor_id']} = {alert['sensor_value']}")
```

## Benchmark Datasets

Generate datasets for testing:

```python
from pm4py.verticals.manufacturing.demos import generate_benchmark_dataset

# Typical performance
typical_log = generate_benchmark_dataset("typical", n_orders=500)

# World-class OEE
high_oee_log = generate_benchmark_dataset("high_oee", n_orders=500)

# Low OEE with issues
low_oee_log = generate_benchmark_dataset("low_oee", n_orders=500)

# Quality problems
quality_log = generate_benchmark_dataset("quality_issues", n_orders=500)
```

## Manufacturing Activities

Standard activities included in the schema:

**Order Processing:**
- `order_received`, `order_review`, `material_picking`, `material_preparation`

**Setup:**
- `equipment_setup`, `tool_loading`, `program_loading`, `first_piece_inspection`

**Production:**
- `production_start`, `machining`, `assembly`, `welding`, `painting`

**Quality:**
- `testing`, `inspection`, `quality_check`, `dimensional_inspection`

**Material Handling:**
- `material_loading`, `material_unloading`, `workpiece_transfer`

**Maintenance:**
- `preventive_maintenance`, `corrective_maintenance`, `emergency_repair`

**Completion:**
- `packaging`, `order_completion`, `shipping`

## API Reference

### ManufacturingVertical

Main class for manufacturing process mining.

**Methods:**
- `discover_production_workflow(variant="powl")` - Discover process model
- `check_oee_conformance(oee_threshold=60.0)` - OEE conformance check
- `check_quality_conformance(defect_threshold=5.0)` - Quality conformance
- `calculate_oee_metrics()` - Calculate OEE metrics
- `detect_bottlenecks(threshold_percentile=75)` - Detect bottlenecks
- `get_real_time_status()` - Get current status
- `analyze_equipment_utilization()` - Equipment utilization
- `analyze_production_flow()` - Production flow analysis
- `generate_production_report(report_type)` - Generate reports

### OEEDashboard

Generate OEE dashboard data.

**Methods:**
- `generate()` - Generate comprehensive dashboard
- `_get_overview()` - Overview statistics
- `_get_equipment_analysis()` - Equipment-wise OEE
- `_get_downtime_analysis()` - Downtime analysis

### RealTimeMonitor

Real-time monitoring dashboard.

**Methods:**
- `get_status()` - Get monitoring status
- `_get_equipment_status()` - Equipment status
- `_get_quality_alerts()` - Quality alerts
- `_get_sensor_alerts()` - Sensor alarms

### BottleneckAnalyzer

Detect process bottlenecks.

**Methods:**
- `detect(threshold_percentile=75)` - Detect bottlenecks
- `_detect_activity_bottlenecks()` - Activity bottlenecks
- `_detect_equipment_bottlenecks()` - Equipment bottlenecks

## Common Use Cases

### 1. Daily OEE Monitoring

```python
from pm4py.verticals.manufacturing import ManufacturingVertical

# Load today's production data
vertical = ManufacturingVertical(log)

# Get OEE metrics
oee = vertical.calculate_oee_metrics()

# Check if OEE meets target
if oee['overall_oee']['oee'] < 60:
    # Investigate issues
    report = vertical.check_oee_conformance()
    print(report['recommendations'])
```

### 2. Quality Issue Investigation

```python
# Check quality conformance
quality_report = vertical.check_quality_conformance(defect_threshold=5.0)

if not quality_report['compliant']:
    # Filter orders with quality issues
    defect_orders = log[log['quality:status'] == 'fail']

    # Analyze defect patterns
    defect_by_equipment = defect_orders.groupby('equipment:id').size()
    defect_by_type = defect_orders.groupby('quality:defect_code').size()

    print("Defects by equipment:", defect_by_equipment)
    print("Defects by type:", defect_by_type)
```

### 3. Bottleneck Resolution

```python
# Detect bottlenecks
bottlenecks = vertical.detect_bottlenecks()

# Focus on high-utilization equipment
for bn in bottlenecks['equipment_bottlenecks']:
    if bn['utilization_percent'] > 85:
        print(f"Consider adding capacity for: {bn['equipment']}")

# Focus on slow activities
for bn in bottlenecks['activity_bottlenecks']:
    if bn['is_bottleneck']:
        print(f"Optimize activity: {bn['activity']}")
```

### 4. Equipment Performance Comparison

```python
# Compare OEE across equipment
oee_metrics = vertical.calculate_oee_metrics()
equipment_oee = oee_metrics['equipment_analysis']

# Sort by OEE
sorted_equipment = sorted(
    equipment_oee.items(),
    key=lambda x: x[1].get('oee', 0),
    reverse=True
)

for equipment, stats in sorted_equipment:
    print(f"{equipment}: OEE={stats.get('oee', 0):.1f}%")
```

## License

Apache License 2.0 - see LICENSE file for details.

## Support

- Documentation: https://processintelligence.solutions/pm4py/
- Issues: https://github.com/process-intelligence-solutions/pm4py/issues
