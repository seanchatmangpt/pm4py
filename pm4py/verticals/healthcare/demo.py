"""
PM4Py – Healthcare Vertical Demo
Copyright (C) 2026 Process Intelligence Solutions GmbH

Demonstrates patient journey mining, HIPAA compliance checking,
wait time analysis, and bottleneck detection.
"""

import sys
import os


def main():
    """Run healthcare vertical demo."""
    print("=" * 70)
    print("PM4Py Healthcare Vertical Demo")
    print("=" * 70)
    print()

    # Import healthcare vertical
    from pm4py.verticals import HealthcareVertical

    # Generate demo data
    print("1. Generating synthetic patient journey data...")
    log = HealthcareVertical.generate_demo_data(n_patients=100)
    print(f"   Generated {len(log)} events across {log['case:concept:name'].nunique()} patient encounters")
    print()

    # Initialize vertical
    print("2. Initializing healthcare vertical...")
    vertical = HealthcareVertical(log)
    print("   Healthcare vertical initialized")
    print()

    # Discover patient journey
    print("3. Discovering patient journey process model...")
    model = vertical.discover_journey(variant="powl")
    print(f"   Process model discovered: {type(model).__name__}")
    print()

    # Check HIPAA compliance
    print("4. Checking HIPAA compliance...")
    compliance = vertical.check_hipaa_compliance()
    print(f"   Compliance Score: {compliance['compliance_score']}%")
    print(f"   Status: {compliance['status']}")
    print(f"   Violations: {compliance['summary']['total_violations']}")
    print(f"   Warnings: {compliance['summary']['total_warnings']}")
    if compliance['violations']:
        print("   Violations:")
        for v in compliance['violations'][:3]:
            print(f"     - [{v['severity']}] {v['description']}")
    if compliance['warnings']:
        print("   Warnings:")
        for w in compliance['warnings'][:3]:
            print(f"     - [{w['severity']}] {w['description']}")
    print()

    # Check consent tracking
    print("5. Checking consent tracking...")
    consent = vertical.check_consent_tracking()
    print(f"   Completeness Score: {consent['completeness_score']}%")
    print(f"   Status: {consent['status']}")
    print(f"   Consents Present: {consent['summary']['consents_present']}/{consent['summary']['consents_required']}")
    print()

    # Analyze wait times
    print("6. Analyzing wait times...")
    wait_analysis = vertical.analyze_wait_times()
    print(f"   Mean Wait: {wait_analysis['mean_wait_minutes']} minutes")
    print(f"   Median Wait: {wait_analysis['median_wait_minutes']} minutes")
    print(f"   P95 Wait: {wait_analysis['p95_wait_minutes']} minutes")
    print(f"   Max Wait: {wait_analysis['max_wait_minutes']} minutes")
    print(f"   Breach Rate (30min threshold): {wait_analysis['breach_rate_percent']}%")
    print()

    # Detect bottlenecks
    print("7. Detecting bottlenecks...")
    bottlenecks = vertical.detect_bottlenecks(threshold_percentile=75)
    if bottlenecks:
        print(f"   Found {len(bottlenecks)} bottlenecks:")
        for b in bottlenecks[:5]:
            print(f"     - [{b['severity']}] {b['type']}: {b['name']}")
            if b['type'] == 'activity':
                print(f"       P95 Wait: {b['p95_wait_minutes']} min")
            else:
                print(f"       P95 Duration: {b['p95_duration_hours']} hrs")
            print(f"       Recommendation: {b['recommendation']}")
    else:
        print("   No bottlenecks detected")
    print()

    # Get clinical pathways
    print("8. Analyzing clinical pathways...")
    pathways = vertical.get_clinical_pathways()
    print(f"   Found {len(pathways)} unique pathways")
    print("   Top 5 pathways:")
    for pathway in pathways[:5]:
        activities = pathway['pathway'] if isinstance(pathway['pathway'], str) else ' -> '.join(pathway['pathway'])
        if len(activities) > 60:
            activities = activities[:57] + "..."
        print(f"     {pathway['percentage']:.1f}%: {activities}")
    print()

    # Get department statistics
    print("9. Department statistics...")
    dept_stats = vertical.get_department_statistics()
    for dept, stats in list(dept_stats.items())[:5]:
        print(f"   {dept}:")
        print(f"     Cases: {stats['case_count']}")
        print(f"     Events: {stats['event_count']}")
        print(f"     Activities: {stats['activities']}")
        if stats['avg_duration']:
            print(f"     Avg Duration: {stats['avg_duration']}")
    print()

    # Generate dashboard
    print("10. Generating dashboard data...")
    dashboard = vertical.generate_dashboard()
    print(f"   Overview:")
    print(f"     Total Patients: {dashboard['overview']['total_patients']}")
    print(f"     Date Range: {dashboard['overview']['date_range_days']} days")
    print(f"     Avg Cases/Day: {dashboard['overview']['avg_cases_per_day']}")
    print()

    # Export compliance audit
    print("11. Exporting compliance audit...")
    audit_path = "/tmp/healthcare_hipaa_audit.json"
    try:
        vertical.export_for_compliance_audit(audit_path)
        print(f"   Audit export saved to: {audit_path}")
    except Exception as e:
        print(f"   Note: Could not save audit file: {e}")
    print()

    # Summary
    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print()
    print("Key Findings:")
    print(f"  - Process Model: {type(model).__name__} discovered successfully")
    print(f"  - HIPAA Compliance: {compliance['compliance_score']}% ({compliance['status']})")
    print(f"  - Consent Tracking: {consent['completeness_score']}% ({consent['status']})")
    print(f"  - Average Wait Time: {wait_analysis['mean_wait_minutes']} minutes")
    print(f"  - Bottlenecks Found: {len(bottlenecks)}")
    print(f"  - Unique Pathways: {len(pathways)}")
    print()
    print("Next Steps:")
    print("  1. Load your own patient journey data")
    print("  2. Map your event schema to the healthcare schema")
    print("  3. Run compliance checks before analysis")
    print("  4. Use bottleneck detection to identify improvement opportunities")
    print("  5. Export visualizations for stakeholder presentations")
    print()


if __name__ == "__main__":
    main()
