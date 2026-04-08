"""
SOC2 Compliance Checking Example

Demonstrates validating SOC2 compliance for trade workflows.
"""

import pm4py
from pm4py.verticals import FinanceVertical
from pm4py.verticals.finance.generators import generate_compliance_test_data


def main():
    print("=" * 60)
    print("Finance Vertical: SOC2 Compliance Check")
    print("=" * 60)

    # Generate data with compliance issues for testing
    print("\n1. Generating test data (with compliance issues)...")
    log = generate_compliance_test_data()
    print(f"   Generated {len(log)} events")

    # Initialize the vertical
    print("\n2. Initializing FinanceVertical...")
    vertical = FinanceVertical(log)

    # Check SOC2 compliance
    print("\n3. Checking SOC2 compliance...")
    compliance = vertical.check_soc2_compliance(criteria="all", strict_mode=False)

    print(f"\n   Compliance Score: {compliance['compliance_score']}%")
    print(f"   Status: {compliance['status']}")

    # Display violations
    print("\n4. Violations Found:")
    for violation in compliance['violations']:
        print(f"   - [{violation.get('category', 'N/A')}] {violation.get('message', 'No message')}")

    # Display warnings
    print("\n5. Warnings:")
    for warning in compliance['warnings']:
        print(f"   - {warning}")

    # Display recommendations
    print("\n6. Recommendations:")
    for rec in compliance['recommendations']:
        print(f"   - {rec}")

    # Summary
    print("\n7. Summary:")
    summary = compliance['summary']
    print(f"   - Total violations: {summary['total_violations']}")
    print(f"   - Total warnings: {summary['total_warnings']}")
    print(f"   - Attributes checked: {summary['attributes_checked']}")
    print(f"   - Events analyzed: {summary['events_analyzed']}")

    # Check specific criteria
    print("\n8. Criteria-Specific Checks:")
    for criteria in ["security", "availability", "integrity"]:
        result = vertical.check_soc2_compliance(criteria=criteria)
        print(f"   - {criteria.capitalize()}: {result['compliance_score']}% ({result['status']})")

    print("\n" + "=" * 60)
    print("Compliance check complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
