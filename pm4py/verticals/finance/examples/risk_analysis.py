"""
Trading Risk Analysis Example

Demonstrates analyzing trading patterns and detecting potential risks.
"""

import pm4py
from pm4py.verticals import FinanceVertical
from pm4py.verticals.finance.generators import generate_trade_workflow, ScenarioType, GeneratorConfig


def main():
    print("=" * 60)
    print("Finance Vertical: Trading Risk Analysis")
    print("=" * 60)

    # Generate normal trading data
    print("\n1. Generating normal trading data...")
    config = GeneratorConfig(n_trades=1000, seed=42)
    log = generate_trade_workflow(config=config, scenario=ScenarioType.NORMAL)
    print(f"   Generated {len(log)} events")

    # Initialize the vertical
    print("\n2. Initializing FinanceVertical...")
    vertical = FinanceVertical(log)

    # Analyze risks
    print("\n3. Analyzing trading risks...")
    risks = vertical.analyze_risks()

    print("\n4. Risk Summary:")
    print(f"   - Overall Risk Score: {risks.get('overall_risk_score', 'N/A')}")
    print(f"   - Risk Level: {risks.get('risk_level', 'N/A')}")

    # Display risk categories
    print("\n5. Risk Categories:")
    for category, details in risks.get('risk_categories', {}).items():
        print(f"   - {category}: {details.get('score', 'N/A')} ({details.get('level', 'N/A')})")

    # Display high-risk trades
    print("\n6. High-Risk Trades:")
    high_risk_trades = risks.get('high_risk_trades', [])
    for trade in high_risk_trades[:5]:
        print(f"   - {trade.get('trade_id', 'N/A')}: {trade.get('reason', 'No reason')}")

    # Display unusual patterns
    print("\n7. Unusual Patterns:")
    patterns = risks.get('unusual_patterns', [])
    for pattern in patterns[:5]:
        print(f"   - {pattern.get('type', 'N/A')}: {pattern.get('description', 'No description')}")

    # Compare with risky scenario
    print("\n8. Comparing with risky scenario...")
    risky_config = GeneratorConfig(n_trades=1000, include_compliance_violations=True)
    risky_log = generate_trade_workflow(
        config=risky_config,
        scenario=ScenarioType.RISKY
    )
    risky_vertical = FinanceVertical(risky_log)
    risky_risks = risky_vertical.analyze_risks()

    print(f"   - Normal scenario risk: {risks.get('overall_risk_score', 'N/A')}")
    print(f"   - Risky scenario risk: {risky_risks.get('overall_risk_score', 'N/A')}")

    # Trader risk analysis
    print("\n9. Trader Risk Analysis:")
    trader_risks = vertical.analyze_trader_risks()
    for trader, risk_score in list(trader_risks.items())[:5]:
        print(f"   - {trader}: {risk_score}")

    # Instrument risk analysis
    print("\n10. Instrument Risk Analysis:")
    instrument_risks = vertical.analyze_instrument_risks()
    for instrument, risk_score in list(instrument_risks.items())[:5]:
        print(f"   - {instrument}: {risk_score}")

    print("\n" + "=" * 60)
    print("Risk analysis complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
