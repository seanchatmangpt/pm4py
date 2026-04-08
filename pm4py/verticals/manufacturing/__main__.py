'''
PM4Py – Manufacturing Vertical Demo
Copyright (C) 2026 Process Intelligence Solutions GmbH

Run with: python -m pm4py.verticals.manufacturing
'''

import sys
import argparse
from datetime import datetime

from pm4py.verticals.manufacturing import (
    ManufacturingVertical,
    quick_analyze,
)
from pm4py.verticals.manufacturing.demos import (
    generate_synthetic_manufacturing_data,
    generate_benchmark_dataset,
)
from pm4py.verticals.manufacturing.schemas import (
    EquipmentType,
    ProductType,
    MANUFACTURING_WORKFLOW_SCHEMA,
    OEE_CALCULATION_STANDARDS,
    calculate_oee,
)


def print_header(title: str):
    """Print section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def print_metric(label: str, value, indent: int = 2):
    """Print metric with formatting."""
    prefix = " " * indent
    if isinstance(value, float):
        print(f"{prefix}{label}: {value:.2f}")
    elif isinstance(value, dict):
        print(f"{prefix}{label}:")
        for k, v in value.items():
            print_metric(k, v, indent + 2)
    else:
        print(f"{prefix}{label}: {value}")


def run_full_demo(
    n_orders: int = 500,
    n_equipment: int = 15,
    generate_visualizations: bool = False,
):
    """Run full manufacturing vertical demo."""
    print_header("PM4Py Manufacturing Vertical Demo")

    print(f"\nConfiguration:")
    print(f"  Orders: {n_orders}")
    print(f"  Equipment: {n_equipment}")
    print(f"  Visualizations: {generate_visualizations}")

    # Generate synthetic data
    print_header("1. Generating Synthetic Manufacturing Data")

    print("  Creating realistic manufacturing workflow with:")
    print("    - Production order lifecycle")
    print("    - Equipment operations (CNC, robots, assembly)")
    print("    - Quality inspections")
    print("    - Maintenance events")
    print("    - OEE attributes")
    print("    - IIoT sensor data")

    log = generate_synthetic_manufacturing_data(
        n_orders=n_orders,
        n_equipment=n_equipment,
        return_dataframe=True,
    )

    print(f"\n  Generated event log:")
    print(f"    Total events: {len(log)}")
    print(f"    Total orders: {log['case:concept:name'].nunique()}")
    print(f"    Unique activities: {log['concept:name'].nunique()}")

    # Show sample events
    print(f"\n  Sample events:")
    for idx, row in log.head(3).iterrows():
        print(f"    - {row['concept:name']} (Order: {row['case:concept:name']})")

    # Initialize vertical
    print_header("2. Initializing Manufacturing Vertical")

    vertical = ManufacturingVertical(log)
    print("  Vertical initialized with:")
    print("    - OEE Conformance Checker")
    print("    - Quality Conformance Checker")
    print("    - Production Standards Checker")
    print("    - OEE Dashboard")
    print("    - Real-time Monitor")
    print("    - Bottleneck Analyzer")

    # Discover production workflow
    print_header("3. Discovering Production Workflow")

    model = vertical.discover_production_workflow(variant="powl")
    print(f"  POWL model discovered:")
    print(f"    Activities: {len(getattr(model, 'nodes', []))}")
    print(f"    Control flow structure detected")

    # Calculate OEE metrics
    print_header("4. Calculating OEE Metrics")

    oee_metrics = vertical.calculate_oee_metrics()
    print("  Overall OEE:")
    print_metric("Overall OEE", oee_metrics["overall_oee"].get("oee", 0))
    print_metric("  Availability", oee_metrics["overall_oee"].get("availability", 0))
    print_metric("  Performance", oee_metrics["overall_oee"].get("performance", 0))
    print_metric("  Quality", oee_metrics["overall_oee"].get("quality", 0))

    print("\n  OEE Standards:")
    for component, standards in OEE_CALCULATION_STANDARDS.items():
        if component != "oee":
            print(f"    {component.capitalize()}:")
            print(f"      World-class: {standards['world_class']}%")
            print(f"      Acceptable: {standards['acceptable']}%")
    print(f"    OEE:")
    print(f"      World-class: {OEE_CALCULATION_STANDARDS['oee']['world_class']}%")
    print(f"      Acceptable: {OEE_CALCULATION_STANDARDS['oee']['acceptable']}%")

    # Equipment-wise OEE
    print("\n  Equipment OEE (Top 5):")
    equipment_analysis = oee_metrics.get("equipment_analysis", {})
    for i, (equipment, stats) in enumerate(list(equipment_analysis.items())[:5]):
        if isinstance(stats, dict) and "oee" in stats:
            print(f"    {i+1}. {equipment}: OEE={stats['oee']:.1f}%")

    # Check OEE conformance
    print_header("5. OEE Conformance Check")

    oee_conformance = vertical.check_oee_conformance(oee_threshold=60.0)
    print(f"  Status: {oee_conformance['status']}")
    print(f"  Conformance Score: {oee_conformance['conformance_score']:.1f}%")
    print(f"  Violations: {oee_conformance['summary']['total_violations']}")
    print(f"  Warnings: {oee_conformance['summary']['total_warnings']}")

    if oee_conformance['violations']:
        print("\n  Top Violations:")
        for violation in oee_conformance['violations'][:5]:
            print(f"    - [{violation['severity']}] {violation['description']}")

    if oee_conformance['recommendations']:
        print("\n  Recommendations:")
        for rec in oee_conformance['recommendations'][:3]:
            print(f"    - {rec}")

    # Quality conformance
    print_header("6. Quality Conformance Check")

    quality_conformance = vertical.check_quality_conformance(defect_threshold=5.0)
    print(f"  Compliant: {quality_conformance['compliant']}")
    print(f"  High Severity: {quality_conformance['summary']['high_severity']}")
    print(f"  Medium Severity: {quality_conformance['summary']['medium_severity']}")

    if quality_conformance['violations']:
        print("\n  Quality Issues:")
        for violation in quality_conformance['violations'][:5]:
            print(f"    - [{violation['severity']}] {violation['description']}")

    # Bottleneck detection
    print_header("7. Bottleneck Detection")

    bottlenecks = vertical.detect_bottlenecks(threshold_percentile=75)

    print("  Activity Bottlenecks:")
    activity_bottlenecks = bottlenecks.get("activity_bottlenecks", [])[:5]
    for i, bn in enumerate(activity_bottlenecks):
        is_bottleneck = " ⚠️" if bn.get("is_bottleneck") else ""
        print(f"    {i+1}. {bn['activity']}: {bn['avg_duration_seconds']:.1f}s avg{is_bottleneck}")

    print("\n  Equipment Bottlenecks:")
    equipment_bottlenecks = bottlenecks.get("equipment_bottlenecks", [])[:5]
    for i, bn in enumerate(equipment_bottlenecks):
        is_bottleneck = " ⚠️" if bn.get("is_bottleneck") else ""
        print(f"    {i+1}. {bn['equipment']}: {bn['utilization_percent']:.1f}% utilization{is_bottleneck}")

    # Equipment utilization
    print_header("8. Equipment Utilization")

    utilization = vertical.analyze_equipment_utilization()
    print("  Equipment Status Summary:")

    running_count = sum(1 for e in utilization.values() if isinstance(e, dict))
    print(f"    Equipment analyzed: {running_count}")

    if running_count > 0:
        avg_running = sum(
            e.get('running_percent', 0) for e in utilization.values()
            if isinstance(e, dict)
        ) / running_count
        print(f"    Average running: {avg_running:.1f}%")

    # Production flow analysis
    print_header("9. Production Flow Analysis")

    flow_analysis = vertical.analyze_production_flow()
    print(f"  Total variants: {flow_analysis['total_variants']}")
    print(f"  Average flow time: {flow_analysis['avg_flow_time_seconds']:.1f}s")
    print(f"  Median flow time: {flow_analysis['median_flow_time_seconds']:.1f}s")
    print(f"  P95 flow time: {flow_analysis['p95_flow_time_seconds']:.1f}s")

    # Real-time status
    print_header("10. Real-Time Monitoring Status")

    status = vertical.get_real_time_status()
    print(f"  Equipment Status:")
    equipment_status = status.get("equipment_status", {})
    if isinstance(equipment_status, dict) and "total_equipment" in equipment_status:
        print(f"    Total equipment: {equipment_status['total_equipment']}")
        print(f"    Running: {equipment_status.get('running', 0)}")
        print(f"    Idle: {equipment_status.get('idle', 0)}")
        print(f"    Maintenance: {equipment_status.get('maintenance', 0)}")
        print(f"    Breakdown: {equipment_status.get('breakdown', 0)}")

    quality_alerts = status.get("quality_alerts", [])
    sensor_alerts = status.get("sensor_alerts", [])

    print(f"\n  Active Alerts:")
    print(f"    Quality issues: {len(quality_alerts)}")
    print(f"    Sensor alarms: {len(sensor_alerts)}")

    # Generate reports
    print_header("11. Production Reports")

    oee_report = vertical.generate_production_report("oee_summary")
    print(f"  OEE Summary Report:")
    print(f"    Report Type: {oee_report['report_type']}")
    print(f"    Timestamp: {oee_report['report_timestamp']}")
    print(f"    Overall OEE: {oee_report['overall_oee'].get('oee', 'N/A')}")

    # Quick analyze summary
    print_header("12. Quick Analysis Summary")

    print("\n  Use quick_analyze() for comprehensive analysis:")
    print("    >>> from pm4py.verticals.manufacturing import quick_analyze")
    print("    >>> results = quick_analyze(log)")
    print("    >>> print(results['oee_conformance'])")
    print("    >>> print(results['bottlenecks'])")

    # Completion
    print_header("Demo Complete!")

    print("\n  Next Steps:")
    print("    1. Load your own manufacturing data")
    print("    2. Connect to OPC-UA servers for real-time data")
    print("    3. Configure equipment-specific OEE targets")
    print("    4. Set up automated conformance monitoring")
    print("    5. Export reports to your BI system")

    print("\n  Documentation: pm4py/verticals/manufacturing/README.md")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return vertical


def run_oee_demo():
    """Run OEE calculation demo."""
    print_header("OEE Calculation Demo")

    print("\nOEE Formula: OEE = Availability × Performance × Quality")

    # Example 1: World-class OEE
    print("\n1. World-Class Performance:")
    oee1 = calculate_oee(
        run_time=450,
        planned_production_time=480,
        total_pieces=1000,
        good_pieces=998,
        ideal_cycle_time=27,
    )
    print(f"   Run Time: 450 min | Planned: 480 min")
    print(f"   Total: 1000 pcs | Good: 998 pcs | Ideal Cycle: 27s")
    print_metric("   Availability", oee1['availability'])
    print_metric("   Performance", oee1['performance'])
    print_metric("   Quality", oee1['quality'])
    print_metric("   OEE", oee1['oee'])
    print(f"   → World-class! (≥85%)")

    # Example 2: Acceptable OEE
    print("\n2. Acceptable Performance:")
    oee2 = calculate_oee(
        run_time=400,
        planned_production_time=480,
        total_pieces=900,
        good_pieces=855,
        ideal_cycle_time=27,
    )
    print(f"   Run Time: 400 min | Planned: 480 min")
    print(f"   Total: 900 pcs | Good: 855 pcs | Ideal Cycle: 27s")
    print_metric("   Availability", oee2['availability'])
    print_metric("   Performance", oee2['performance'])
    print_metric("   Quality", oee2['quality'])
    print_metric("   OEE", oee2['oee'])
    print(f"   → Acceptable (≥60%)")

    # Example 3: Needs improvement
    print("\n3. Needs Improvement:")
    oee3 = calculate_oee(
        run_time=300,
        planned_production_time=480,
        total_pieces=600,
        good_pieces=540,
        ideal_cycle_time=27,
    )
    print(f"   Run Time: 300 min | Planned: 480 min")
    print(f"   Total: 600 pcs | Good: 540 pcs | Ideal Cycle: 27s")
    print_metric("   Availability", oee3['availability'])
    print_metric("   Performance", oee3['performance'])
    print_metric("   Quality", oee3['quality'])
    print_metric("   OEE", oee3['oee'])
    print(f"   → Below acceptable (<60%)")


def run_benchmark_demo():
    """Run benchmark dataset comparison."""
    print_header("Benchmark Dataset Comparison")

    variants = ["typical", "high_oee", "low_oee", "quality_issues"]

    for variant in variants:
        print(f"\n{variant.upper().replace('_', ' ')} Dataset:")

        log = generate_benchmark_dataset(variant=variant, n_orders=100)

        # Calculate OEE
        if "oee:oee" in log.columns:
            avg_oee = log["oee:oee"].mean()
            print(f"  Average OEE: {avg_oee:.1f}%")

        # Calculate quality rate
        if "quality:status" in log.columns:
            pass_rate = (log["quality:status"] == "pass").sum() / log["quality:status"].notna().sum() * 100
            print(f"  Pass Rate: {pass_rate:.1f}%")

        # Calculate downtime
        if "oee:downtime" in log.columns:
            avg_downtime = log["oee:downtime"].mean()
            print(f"  Avg Downtime: {avg_downtime:.1f} min")


def run_schema_demo():
    """Run manufacturing schema demo."""
    print_header("Manufacturing Schema Reference")

    print("\nEvent Level Attributes:")
    event_level = MANUFACTURING_WORKFLOW_SCHEMA.get("event_level", {})

    categories = {}
    for attr_name, attr_def in event_level.items():
        category = attr_name.split(":")[0] if ":" in attr_name else "other"
        if category not in categories:
            categories[category] = []
        categories[category].append((attr_name, attr_def))

    for category, attrs in sorted(categories.items()):
        print(f"\n  {category.upper()}:")
        for attr_name, attr_def in attrs[:5]:
            required = "REQUIRED" if attr_def.get("required") else "optional"
            print(f"    {attr_name}: {required}")
            if attr_def.get("description"):
                print(f"      {attr_def['description']}")

    print("\n\nTrace Level Attributes:")
    trace_level = MANUFACTURING_WORKFLOW_SCHEMA.get("trace_level", {})

    for attr_name, attr_def in trace_level.items():
        required = "REQUIRED" if attr_def.get("required") else "optional"
        print(f"  {attr_name}: {required}")
        if attr_def.get("description"):
            print(f"    {attr_def['description']}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="PM4Py Manufacturing Vertical Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m pm4py.verticals.manufacturing
  python -m pm4py.verticals.manufacturing --orders 1000 --equipment 20
  python -m pm4py.verticals.manufacturing --mode oee
  python -m pm4py.verticals.manufacturing --mode benchmark
  python -m pm4py.verticals.manufacturing --mode schema
        """
    )

    parser.add_argument(
        "--mode",
        choices=["full", "oee", "benchmark", "schema"],
        default="full",
        help="Demo mode to run"
    )

    parser.add_argument(
        "--orders",
        type=int,
        default=500,
        help="Number of production orders to generate"
    )

    parser.add_argument(
        "--equipment",
        type=int,
        default=15,
        help="Number of equipment units"
    )

    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Generate visualizations"
    )

    parser.add_argument(
        "--output",
        type=str,
        help="Output file path for generated data"
    )

    args = parser.parse_args()

    try:
        if args.mode == "full":
            vertical = run_full_demo(
                n_orders=args.orders,
                n_equipment=args.equipment,
                generate_visualizations=args.visualize,
            )

            if args.output:
                log = vertical.log
                if args.output.endswith(".csv"):
                    log.to_csv(args.output, index=False)
                elif args.output.endswith(".xes"):
                    from pm4py import write_xes
                    write_xes(log, args.output)
                print(f"\nData saved to: {args.output}")

        elif args.mode == "oee":
            run_oee_demo()

        elif args.mode == "benchmark":
            run_benchmark_demo()

        elif args.mode == "schema":
            run_schema_demo()

        return 0

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
