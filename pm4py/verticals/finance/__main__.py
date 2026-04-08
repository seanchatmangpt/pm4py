'''
PM4Py – Finance Vertical Demo
Copyright (C) 2026 Process Intelligence Solutions GmbH

Demonstrates SOC2-ready trade workflow mining.
'''

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd

from pm4py.verticals import FinanceVertical


def run_demo(
    n_trades: int = 1000,
    n_traders: int = 20,
    n_instruments: int = 50,
    output_dir: str = ".",
    visualize: bool = False,
):
    """
    Run the finance vertical demo.

    :param n_trades: Number of trades to generate
    :param n_traders: Number of traders
    :param n_instruments: Number of instruments
    :param output_dir: Output directory for reports
    :param visualize: Whether to generate visualizations
    """
    print("=" * 70)
    print("PM4Py Finance Vertical Demo")
    print("=" * 70)
    print()

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Step 1: Generate demo data
    print(f"[1/6] Generating {n_trades} synthetic trades...")
    log = FinanceVertical.generate_demo_data(
        n_trades=n_trades,
        n_traders=n_traders,
        n_instruments=n_instruments,
        return_dataframe=True,
    )
    print(f"      Generated {len(log)} events across {log['case:concept:name'].nunique()} trades")
    print()

    # Initialize vertical
    vertical = FinanceVertical(log)

    # Step 2: Discover trade workflow
    print("[2/6] Discovering trade workflow model...")
    model = vertical.discover_trade_workflow(variant="powl")
    print(f"      Model type: {type(model).__name__}")

    if visualize:
        viz_path = output_path / "trade_workflow.png"
        vertical.visualize_trade_flow(format="png", output_path=str(viz_path))
        print(f"      Saved visualization to: {viz_path}")
    print()

    # Step 3: Check SOC2 compliance
    print("[3/6] Checking SOC2 compliance...")
    soc2_compliance = vertical.check_soc2_compliance()
    print(f"      Compliance Score: {soc2_compliance['compliance_score']}%")
    print(f"      Status: {soc2_compliance['status']}")

    if soc2_compliance['violations']:
        print(f"      Violations: {len(soc2_compliance['violations'])}")
        for v in soc2_compliance['violations'][:3]:
            print(f"        - {v['description']}")
    print()

    # Step 4: Check trade compliance
    print("[4/6] Checking trade compliance...")
    trade_compliance = vertical.check_trade_compliance()
    print(f"      Compliant: {trade_compliance['compliant']}")
    print(f"      Violations: {trade_compliance['summary']['total_violations']}")
    print(f"      High Severity: {trade_compliance['summary']['high_severity']}")
    print()

    # Step 5: Analyze risks
    print("[5/6] Analyzing trading risks...")
    risk_analysis = vertical.analyze_risks(risk_type="all", threshold=0.7)
    print(f"      Total Risks Detected: {risk_analysis['total_risks']}")
    print(f"      High Risk Count: {risk_analysis['high_risk_count']}")
    print(f"      Alerts: {len(risk_analysis['alerts'])}")

    if risk_analysis['alerts']:
        print("      Top Alerts:")
        for alert in risk_analysis['alerts'][:5]:
            print(f"        [{alert['severity']}] {alert['type']}: {alert['description']}")
    print()

    # Step 6: Generate regulatory report
    print("[6/6] Generating regulatory report...")
    report = vertical.generate_regulatory_report(report_type="trade_reconstruction")

    # Save reports
    reports_dir = output_path / "finance_reports"
    reports_dir.mkdir(exist_ok=True)

    # Save full report
    report_path = reports_dir / "regulatory_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"      Saved regulatory report to: {report_path}")

    # Save SOC2 compliance report
    soc2_path = reports_dir / "soc2_compliance.json"
    with open(soc2_path, 'w') as f:
        json.dump(soc2_compliance, f, indent=2, default=str)
    print(f"      Saved SOC2 compliance to: {soc2_path}")

    # Save risk analysis
    risk_path = reports_dir / "risk_analysis.json"
    with open(risk_path, 'w') as f:
        json.dump(risk_analysis, f, indent=2, default=str)
    print(f"      Saved risk analysis to: {risk_path}")

    # Save audit export
    audit_path = reports_dir / "audit_export.json"
    vertical.export_for_audit(str(audit_path), include_phi=False)
    print(f"      Saved audit export to: {audit_path}")
    print()

    # Summary
    print("=" * 70)
    print("Demo Summary")
    print("=" * 70)
    print(f"  Trades Analyzed: {report['summary']['unique_traders']}")
    print(f"  Unique Instruments: {report['summary']['unique_instruments']}")
    print(f"  Unique Traders: {report['summary']['unique_traders']}")
    print(f"  Avg Trade Duration: {report['summary']['avg_trade_duration_seconds']:.2f} seconds")
    print(f"  SOC2 Compliance: {soc2_compliance['compliance_score']}%")
    print(f"  High Risk Trades: {risk_analysis['high_risk_count']}")
    print()
    print(f"Reports saved to: {reports_dir}")
    print("=" * 70)

    return {
        "model": model,
        "soc2_compliance": soc2_compliance,
        "trade_compliance": trade_compliance,
        "risk_analysis": risk_analysis,
        "regulatory_report": report,
    }


def run_benchmark(variant: str = "typical", output_dir: str = "."):
    """
    Run benchmark analysis on different datasets.

    :param variant: Dataset variant ('typical', 'high_volume', 'high_risk', 'compliant')
    :param output_dir: Output directory
    """
    from pm4py.verticals.finance.demos import generate_benchmark_dataset

    print(f"Running benchmark: {variant}")

    log = generate_benchmark_dataset(variant=variant, n_trades=1000)
    vertical = FinanceVertical(log)

    results = {
        "variant": variant,
        "soc2_compliance": vertical.check_soc2_compliance(),
        "trade_compliance": vertical.check_trade_compliance(),
        "risks": vertical.analyze_risks(),
    }

    # Save results
    output_path = Path(output_dir) / f"benchmark_{variant}.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"Benchmark results saved to: {output_path}")
    print(f"  SOC2 Compliance: {results['soc2_compliance']['compliance_score']}%")
    print(f"  High Risk Count: {results['risks']['high_risk_count']}")

    return results


def main():
    """Main entry point for the finance vertical demo."""
    parser = argparse.ArgumentParser(
        description="PM4Py Finance Vertical - SOC2-ready trade workflow mining"
    )
    parser.add_argument(
        "--trades",
        type=int,
        default=1000,
        help="Number of trades to generate (default: 1000)",
    )
    parser.add_argument(
        "--traders",
        type=int,
        default=20,
        help="Number of traders (default: 20)",
    )
    parser.add_argument(
        "--instruments",
        type=int,
        default=50,
        help="Number of instruments (default: 50)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=".",
        help="Output directory for reports (default: current directory)",
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Generate visualizations",
    )
    parser.add_argument(
        "--benchmark",
        type=str,
        choices=["typical", "high_volume", "high_risk", "compliant"],
        help="Run benchmark on specific dataset variant",
    )

    args = parser.parse_args()

    try:
        if args.benchmark:
            run_benchmark(variant=args.benchmark, output_dir=args.output)
        else:
            run_demo(
                n_trades=args.trades,
                n_traders=args.traders,
                n_instruments=args.instruments,
                output_dir=args.output,
                visualize=args.visualize,
            )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
