'''
PM4Py – Finance Vertical Example
Copyright (C) 2026 Process Intelligence Solutions GmbH

Example: End-to-end trade workflow analysis with SOC2 compliance checking.
'''

import pandas as pd
from pm4py.verticals import FinanceVertical
from pm4py.verticals.finance.rules.risk_detection import check_all_risk_rules
from pm4py.verticals.finance.conformance import SOC2ConformanceChecker


def main():
    """Run the finance vertical example."""
    print("=" * 70)
    print("PM4Py Finance Vertical Example")
    print("Trade Workflow Analysis with SOC2 Compliance")
    print("=" * 70)
    print()

    # Step 1: Generate synthetic trade data
    print("[Step 1] Generating synthetic trade data...")
    log = FinanceVertical.generate_demo_data(
        n_trades=500,
        n_traders=10,
        n_instruments=25,
    )
    print(f"  Generated {len(log)} events across {log['case:concept:name'].nunique()} trades")
    print()

    # Step 2: Initialize the finance vertical
    print("[Step 2] Initializing FinanceVertical...")
    vertical = FinanceVertical(log)
    print()

    # Step 3: Discover trade workflow
    print("[Step 3] Discovering trade workflow...")
    model = vertical.discover_trade_workflow(variant="powl")
    print(f"  Model type: {type(model).__name__}")
    print()

    # Step 4: Check SOC2 compliance
    print("[Step 4] Checking SOC2 compliance...")
    soc2_checker = SOC2ConformanceChecker()
    soc2_report = soc2_checker.check(log, criteria="security")
    print(f"  SOC2 Compliance Score: {soc2_report['compliance_score']}%")
    print(f"  Status: {soc2_report['status']}")
    print(f"  Violations: {soc2_report['summary']['total_violations']}")
    print(f"  Warnings: {soc2_report['summary']['total_warnings']}")
    print()

    # Step 5: Run risk detection rules
    print("[Step 5] Running risk detection rules...")
    risk_alerts = check_all_risk_rules(log)
    print(f"  Total Risk Alerts: {len(risk_alerts)}")

    high_severity = [a for a in risk_alerts if a.severity == "HIGH"]
    print(f"  High Severity: {len(high_severity)}")

    if high_severity:
        print("  Top High Severity Alerts:")
        for alert in high_severity[:3]:
            print(f"    - [{alert.risk_type}] {alert.description}")
    print()

    # Step 6: Analyze trader performance
    print("[Step 6] Analyzing trader performance...")
    trader_stats = vertical.get_trader_statistics()

    if trader_stats and "error" not in trader_stats:
        print(f"  Active Traders: {len(trader_stats)}")
        for trader, stats in list(trader_stats.items())[:3]:
            print(f"    {trader}: {stats['trade_count']} trades, "
                  f"{stats['avg_trade_duration']:.2f}s avg duration")
    print()

    # Step 7: Detect unusual patterns
    print("[Step 7] Detecting unusual trading patterns...")
    anomalies = vertical.detect_unusual_patterns()
    print(f"  Anomalies Detected: {len(anomalies)}")

    for anomaly in anomalies:
        print(f"    - [{anomaly['type']}] {anomaly['description']}")
    print()

    # Step 8: Generate regulatory report
    print("[Step 8] Generating regulatory report...")
    report = vertical.generate_regulatory_report(report_type="trade_reconstruction")
    print(f"  Total Trades: {report['total_trades']}")
    print(f"  Avg Duration: {report['summary']['avg_trade_duration_seconds']:.2f} seconds")
    print(f"  Unique Instruments: {report['summary']['unique_instruments']}")
    print()

    # Step 9: Trade reconstruction example
    print("[Step 9] Trade reconstruction example...")
    trades = vertical.reconstruct_trades(trade_ids=[log['case:concept:name'].iloc[0]])

    if trades:
        trade = trades[0]
        print(f"  Trade ID: {trade['trade_id']}")
        print(f"  Activities: {' → '.join(trade['activities'])}")
        print(f"  Duration: {trade['duration_seconds']:.2f} seconds")
    print()

    # Summary
    print("=" * 70)
    print("Analysis Summary")
    print("=" * 70)
    print(f"  Events Processed: {len(log)}")
    print(f"  Trades Analyzed: {log['case:concept:name'].nunique()}")
    print(f"  SOC2 Compliant: {soc2_report['compliance_score'] >= 95}")
    print(f"  Risk Alerts: {len(risk_alerts)}")
    print(f"  High Risk: {len(high_severity)}")
    print()


def example_soc2_audit():
    """Example: SOC2 audit preparation."""
    print("\n" + "=" * 70)
    print("SOC2 Audit Preparation Example")
    print("=" * 70)
    print()

    # Generate demo data
    log = FinanceVertical.generate_demo_data(n_trades=100)
    vertical = FinanceVertical(log)

    # Check all SOC2 criteria
    print("Checking SOC2 criteria:")
    criteria = ["security", "availability", "integrity", "confidentiality"]

    for criterion in criteria:
        report = vertical.check_soc2_compliance(criteria=criterion)
        status_icon = "✓" if report["status"] == "COMPLIANT" else "✗"
        print(f"  {status_icon} {criterion.capitalize()}: {report['compliance_score']}%")

    print()

    # Export for audit
    print("Exporting audit package...")
    vertical.export_for_audit("soc2_audit_export.json", include_phi=False)
    print("  Saved to: soc2_audit_export.json")
    print()


def example_risk_analysis():
    """Example: Comprehensive risk analysis."""
    print("\n" + "=" * 70)
    print("Risk Analysis Example")
    print("=" * 70)
    print()

    # Generate demo data with some risk factors
    log = FinanceVertical.generate_demo_data(n_trades=200)
    vertical = FinanceVertical(log)

    # Run comprehensive risk analysis
    print("Running risk analysis...")

    risk_types = ["market", "concentration", "liquidity", "operational", "compliance"]

    for risk_type in risk_types:
        analysis = vertical.analyze_risks(risk_type=risk_type, threshold=0.6)
        print(f"\n{risk_type.capitalize()} Risk:")
        print(f"  Total Risks: {analysis['total_risks']}")
        print(f"  High Risk: {analysis['high_risk_count']}")

        if analysis['alerts']:
            print(f"  Alerts: {len(analysis['alerts'])}")
            for alert in analysis['alerts'][:2]:
                print(f"    - {alert['description']}")

    print()


if __name__ == "__main__":
    main()
    example_soc2_audit()
    example_risk_analysis()

    print("=" * 70)
    print("Example completed successfully!")
    print("=" * 70)
