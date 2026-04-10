"""
POWL 2.0 Choice Graph Usage Example

This example demonstrates how to use the Choice Graph (PM×) Inductive Miner
to discover non-block-structured process models from event logs.

Based on:
H Kourani, G Park, WMP van der Aalst. "Unlocking Non-Block-Structured Decisions:
Inductive Mining with Choice Graphs" arXiv:2505.07052.
"""

from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.algo.discovery.powl import algorithm as powl_algorithm
from pm4py.algo.discovery.powl.inductive.variants.powl_discovery_varaints import POWLDiscoveryVariant
from pm4py.objects.powl.obj import DecisionGraph
from pm4py.visualization.powl import visualizer


def create_retailer_log():
    """
    Create a sample retailer process event log.

    This log demonstrates non-block-structured choices:
    - In-stock path: ship or cancel
    - Production path: with or without notify

    Returns:
        EventLog: Sample retailer process log
    """
    log = EventLog()

    # In-stock with shipping
    log.append(Trace([
        Event({'concept:name': 'receive_order'}),
        Event({'concept:name': 'in_stock'}),
        Event({'concept:name': 'ship'}),
    ]))

    # In-stock with cancellation
    log.append(Trace([
        Event({'concept:name': 'receive_order'}),
        Event({'concept:name': 'in_stock'}),
        Event({'concept:name': 'cancel'}),
    ]))

    # Production with notification
    log.append(Trace([
        Event({'concept:name': 'receive_order'}),
        Event({'concept:name': 'production'}),
        Event({'concept:name': 'gather_materials'}),
        Event({'concept:name': 'schedule'}),
        Event({'concept:name': 'notify'}),
        Event({'concept:name': 'execute'}),
    ]))

    # Production without notification (skip notify)
    log.append(Trace([
        Event({'concept:name': 'receive_order'}),
        Event({'concept:name': 'production'}),
        Event({'concept:name': 'gather_materials'}),
        Event({'concept:name': 'schedule'}),
        Event({'concept:name': 'execute'}),
    ]))

    return log


def example_choice_graph_discovery():
    """
    Example: Discover a Choice Graph using the PM× Inductive Miner.
    """
    print("=" * 60)
    print("POWL 2.0 Choice Graph Discovery Example")
    print("=" * 60)

    # Create event log
    log = create_retailer_log()
    print(f"\nEvent log: {len(log)} traces")

    # Discover using Choice Graph variant
    print("\nDiscovering model using DECISION_GRAPH_MAX variant...")
    model = powl_algorithm.apply(
        log,
        variant=POWLDiscoveryVariant.DECISION_GRAPH_MAX
    )

    print(f"Discovered model type: {type(model).__name__}")

    # If it's a DecisionGraph, show soundness validation
    if isinstance(model, DecisionGraph):
        print("\nSoundness Validation:")
        report = model.get_soundness_report()
        print(f"  - Sound: {report['is_sound']}")
        print(f"  - Nodes: {report['metrics']['num_nodes']}")
        print(f"  - Edges: {report['metrics']['num_edges']}")
        print(f"  - Connectivity: {report['metrics']['connectivity']}")
        print(f"  - Acyclicity: {report['metrics']['acyclicity']}")

        # Show model language
        print("\nModel Language (L(G)):")
        language = list(model.language())
        for i, trace in enumerate(language, 1):
            print(f"  Trace {i}: {trace}")

        # Generate visualization
        print("\nGenerating visualization...")
        viz = visualizer.apply(model)
        print(f"Visualization generated: {type(viz).__name__}")
        print("Save with: visualizer.save(model, 'choice_graph.svg')")

    print("\n" + "=" * 60)


def example_all_variants():
    """
    Example: Compare all 4 Choice Graph discovery variants.
    """
    print("=" * 60)
    print("Comparing All Choice Graph Variants")
    print("=" * 60)

    log = create_retailer_log()

    variants = [
        (POWLDiscoveryVariant.DECISION_GRAPH_MAX, "DECISION_GRAPH_MAX"),
        (POWLDiscoveryVariant.DECISION_GRAPH_CLUSTERING, "DECISION_GRAPH_CLUSTERING"),
        (POWLDiscoveryVariant.DECISION_GRAPH_CYCLIC, "DECISION_GRAPH_CYCLIC"),
        (POWLDiscoveryVariant.DECISION_GRAPH_CYCLIC_STRICT, "DECISION_GRAPH_CYCLIC_STRICT"),
    ]

    print("\nDiscovering models with all variants:\n")
    for variant, name in variants:
        model = powl_algorithm.apply(log, variant=variant)
        is_decision_graph = isinstance(model, DecisionGraph)
        print(f"  {name:40} -> {type(model).__name__:20} (DecisionGraph: {is_decision_graph})")

    print("\n" + "=" * 60)


def example_simple_choice():
    """
    Example: Simple choice between two activities.

    This demonstrates the most basic non-block-structured choice:
    Activity 'a' is followed by either 'b' or 'c'.
    """
    print("=" * 60)
    print("Simple Choice Example: a -> (b or c)")
    print("=" * 60)

    # Create simple log
    log = EventLog([
        Trace([Event({'concept:name': 'a'}), Event({'concept:name': 'b'})]),
        Trace([Event({'concept:name': 'a'}), Event({'concept:name': 'c'})]),
    ])

    # Discover model
    model = powl_algorithm.apply(
        log,
        variant=POWLDiscoveryVariant.DECISION_GRAPH_MAX
    )

    print(f"\nDiscovered: {type(model).__name__}")

    if isinstance(model, DecisionGraph):
        # Show soundness
        report = model.get_soundness_report()
        print(f"Sound: {report['is_sound']}")
        print(f"Nodes: {report['metrics']['num_nodes']}")
        print(f"Edges: {report['metrics']['num_edges']}")

        # Show language
        print("\nLanguage:")
        for trace in model.language():
            print(f"  {trace}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Run examples
    example_simple_choice()
    print("\n")
    example_choice_graph_discovery()
    print("\n")
    example_all_variants()
