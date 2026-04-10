"""
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions UG (haftungsbeschränkt)

Licensed under the GNU AGPL v3.0 - see LICENSE file for details.
"""

"""
Real-World Dataset Examples for POWL 2.0 Choice Graph

Demonstrates Choice Graph discovery on PM4Py's built-in example datasets.
Shows practical application on real process mining data.
"""

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.powl import algorithm as powl_algorithm
from pm4py.algo.discovery.powl.inductive.variants.powl_discovery_varaints import POWLDiscoveryVariant
from pm4py.objects.powl.obj import DecisionGraph
from pm4py.objects.powl.conformance import print_conformance_report
import os


def example_running_example():
    """
    Discover Choice Graph on the classic running-example log.

    This is a simple process with 6 traces showing a sequential
    process with some choices.
    """
    print("=" * 70)
    print("Example 1: Running Example Log")
    print("=" * 70)

    # Import running example log (built into PM4Py)
    log_path = os.path.join("tests", "input_data", "running-example.xes")

    if not os.path.exists(log_path):
        print("⚠️  Running example not found, skipping...")
        return None

    log = xes_importer.apply(log_path)

    print(f"\nEvent Log: {len(log)} traces")
    print(f"Activities: {len(set(e['concept:name'] for t in log for e in t))}")

    # Discover with Choice Graph
    model = powl_algorithm.apply(log, variant=POWLDiscoveryVariant.DECISION_GRAPH_MAX)

    print(f"\nDiscovered model: {type(model).__name__}")

    if isinstance(model, DecisionGraph):
        report = model.get_soundness_report()
        print(f"Soundness: {report['is_sound']}")
        print(f"Nodes: {report['metrics']['num_nodes']}")
        print(f"Edges: {report['metrics']['num_edges']}")

        # Show language size
        language = list(model.language())
        print(f"Model language size: {len(language)} traces")

        # Check conformance
        print("\nConformance Report:")
        print_conformance_report(log, model)

    print("\n" + "=" * 70)
    return model


def example_receipt_log():
    """
    Discover Choice Graph on the receipt log.

    This is a more complex process from financial domain.
    """
    print("\n" + "=" * 70)
    print("Example 2: Receipt Log")
    print("=" * 70)

    # Import receipt log (built into PM4Py)
    log_path = os.path.join("tests", "input_data", "receipt.xes")

    if not os.path.exists(log_path):
        print("⚠️  Receipt log not found, skipping...")
        return None

    log = xes_importer.apply(log_path)

    print(f"\nEvent Log: {len(log)} traces")
    print(f"Activities: {len(set(e['concept:name'] for t in log for e in t))}")

    # Discover with Choice Graph
    model = powl_algorithm.apply(log, variant=POWLDiscoveryVariant.DECISION_GRAPH_MAX)

    print(f"\nDiscovered model: {type(model).__name__}")

    if isinstance(model, DecisionGraph):
        report = model.get_soundness_report()
        print(f"Soundness: {report['is_sound']}")
        print(f"Nodes: {report['metrics']['num_nodes']}")
        print(f"Edges: {report['metrics']['num_edges']}")

        # Show language size (may be large for complex logs)
        language = list(model.language())
        print(f"Model language size: {len(language)} traces")

        # Check fitness
        from pm4py.objects.powl.conformance import check_log_conformance
        result = check_log_conformance(log, model)
        print(f"\nFitness: {result['fitness']:.2%}")
        print(f"Conforming traces: {result['conforming_traces']}/{result['total_traces']}")

    print("\n" + "=" * 70)
    return model


def example_roadtraffic_log():
    """
    Discover Choice Graph on the roadtraffic log.

    This is a larger real-world log from traffic management.
    """
    print("\n" + "=" * 70)
    print("Example 3: Roadtraffic Log")
    print("=" * 70)

    # Import roadtraffic log (built into PM4Py)
    log_path = os.path.join("tests", "input_data", "roadtraffic100.xes")

    if not os.path.exists(log_path):
        print("⚠️  Roadtraffic log not found, skipping...")
        return None

    log = xes_importer.apply(log_path)

    print(f"\nEvent Log: {len(log)} traces")
    print(f"Activities: {len(set(e['concept:name'] for t in log for e in t))}")

    # Discover with Choice Graph
    model = powl_algorithm.apply(log, variant=POWLDiscoveryVariant.DECISION_GRAPH_MAX)

    print(f"\nDiscovered model: {type(model).__name__}")

    if isinstance(model, DecisionGraph):
        report = model.get_soundness_report()
        print(f"Soundness: {report['is_sound']}")
        print(f"Nodes: {report['metrics']['num_nodes']}")
        print(f"Edges: {report['metrics']['num_edges']}")

        # For larger logs, don't compute full language
        print("\nNote: Language computation skipped for large log")

        # Check fitness
        from pm4py.objects.powl.conformance import check_log_conformance
        result = check_log_conformance(log, model)
        print(f"\nFitness: {result['fitness']:.2%}")
        print(f"Conforming traces: {result['conforming_traces']}/{result['total_traces']}")

    print("\n" + "=" * 70)
    return model


def compare_variants_on_real_data():
    """
    Compare all 4 Choice Graph variants on real data.
    """
    print("\n" + "=" * 70)
    print("Comparison: All 4 Choice Graph Variants on Running Example")
    print("=" * 70)

    log_path = os.path.join("tests", "input_data", "running-example.xes")

    if not os.path.exists(log_path):
        print("⚠️  Running example not found, skipping comparison...")
        return

    log = xes_importer.apply(log_path)

    variants = [
        POWLDiscoveryVariant.DECISION_GRAPH_MAX,
        POWLDiscoveryVariant.DECISION_GRAPH_CLUSTERING,
        POWLDiscoveryVariant.DECISION_GRAPH_CYCLIC,
        POWLDiscoveryVariant.DECISION_GRAPH_CYCLIC_STRICT,
    ]

    print(f"\nEvent Log: {len(log)} traces")
    print("\nComparing variants:")
    print("-" * 70)

    for variant in variants:
        model = powl_algorithm.apply(log, variant=variant)

        if isinstance(model, DecisionGraph):
            report = model.get_soundness_report()
            print(f"{variant.name:40} Nodes: {report['metrics']['num_nodes']:2}  "
                  f"Edges: {report['metrics']['num_edges']:2}  "
                  f"Sound: {report['is_sound']}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("POWL 2.0 Choice Graph - Real-World Dataset Examples")
    print("=" * 70)

    # Run examples
    example_running_example()
    example_receipt_log()
    example_roadtraffic_log()
    compare_variants_on_real_data()

    print("\n" + "=" * 70)
    print("All real-world examples completed!")
    print("=" * 70)
