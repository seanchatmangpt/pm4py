"""
Basic Trade Workflow Discovery Example

Demonstrates discovering and visualizing trade workflow models from event logs.
"""

import pm4py
from pm4py.verticals import FinanceVertical


def main():
    print("=" * 60)
    print("Finance Vertical: Basic Trade Workflow Discovery")
    print("=" * 60)

    # Generate demo trade data
    print("\n1. Generating demo trade data...")
    log = FinanceVertical.generate_demo_data(n_trades=500)
    print(f"   Generated {len(log)} events")

    # Initialize the vertical
    print("\n2. Initializing FinanceVertical...")
    vertical = FinanceVertical(log)

    # Discover trade workflow model
    print("\n3. Discovering trade workflow model...")
    model = vertical.discover_trade_workflow()
    print(f"   Model type: {type(model).__name__}")

    # Get model statistics
    print("\n4. Model Statistics:")
    stats = vertical.get_model_statistics()
    for key, value in stats.items():
        print(f"   - {key}: {value}")

    # Visualize the model
    print("\n5. Saving visualization...")
    vertical.save_model_visualization("trade_workflow.png")
    print("   Saved to: trade_workflow.png")

    # Analyze activity frequencies
    print("\n6. Activity Frequencies:")
    freq = vertical.get_activity_frequencies()
    for activity, count in freq.head(10).items():
        print(f"   - {activity}: {count}")

    # Analyze bottlenecks
    print("\n7. Process Bottlenecks:")
    bottlenecks = vertical.analyze_bottlenecks()
    for activity, metrics in bottlenecks[:5].items():
        print(f"   - {activity}: avg {metrics.get('avg_duration', 'N/A')}")

    print("\n" + "=" * 60)
    print("Discovery complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
