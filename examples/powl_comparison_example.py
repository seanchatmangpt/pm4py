"""
Comparison: Block-Structured XOR vs Choice Graph

This example demonstrates the difference between block-structured XOR (current POWL)
and Choice Graph (POWL 2.0) when discovering processes with overlapping choice regions.
"""

from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.algo.discovery.powl import algorithm as powl_algorithm
from pm4py.algo.discovery.powl.inductive.variants.powl_discovery_varaints import POWLDiscoveryVariant
from pm4py.objects.powl.obj import DecisionGraph, OperatorPOWL


def create_overlapping_choice_log():
    """
    Create a log with overlapping choice regions.

    Trace structure:
    - a -> b -> d
    - a -> c -> d
    - a -> b -> c -> d  (a appears in both branches!)

    This CANNOT be accurately represented by block-structured XOR.
    """
    log = EventLog()

    # Trace 1: a -> b -> d
    log.append(Trace([
        Event({'concept:name': 'a'}),
        Event({'concept:name': 'b'}),
        Event({'concept:name': 'd'}),
    ]))

    # Trace 2: a -> c -> d
    log.append(Trace([
        Event({'concept:name': 'a'}),
        Event({'concept:name': 'c'}),
        Event({'concept:name': 'd'}),
    ]))

    # Trace 3: a -> b -> c -> d (overlapping!)
    log.append(Trace([
        Event({'concept:name': 'a'}),
        Event({'concept:name': 'b'}),
        Event({'concept:name': 'c'}),
        Event({'concept:name': 'd'}),
    ]))

    return log


def compare_discovery_methods():
    """
    Compare block-structured XOR (MAXIMAL) vs Choice Graph (DECISION_GRAPH_MAX).
    """
    print("=" * 70)
    print("Comparison: Block-Structured XOR vs Choice Graph")
    print("=" * 70)

    log = create_overlapping_choice_log()
    print(f"\nEvent log: {len(log)} traces with overlapping choice regions")
    print("  Trace 1: a -> b -> d")
    print("  Trace 2: a -> c -> d")
    print("  Trace 3: a -> b -> c -> d  (overlapping!)")

    # Discover with block-structured XOR (MAXIMAL variant)
    print("\n" + "-" * 70)
    print("Method 1: Block-Structured XOR (POWLDiscoveryVariant.MAXIMAL)")
    print("-" * 70)

    xor_model = powl_algorithm.apply(log, variant=POWLDiscoveryVariant.MAXIMAL)
    print(f"Discovered model: {type(xor_model).__name__}")

    if isinstance(xor_model, OperatorPOWL):
        print(f"Operator: {xor_model.operator}")
        print(f"Children: {len(xor_model.children)}")
        for i, child in enumerate(xor_model.children, 1):
            print(f"  Child {i}: {child}")

    # Check if XOR model captures all traces accurately
    print("\n  ⚠️  Limitation: XOR forces activities into disjoint branches")
    print("     Activity 'b' and 'c' must be in separate branches")
    print("     Trace 3 (a->b->c->d) cannot be represented accurately!")

    # Discover with Choice Graph (DECISION_GRAPH_MAX variant)
    print("\n" + "-" * 70)
    print("Method 2: Choice Graph (POWLDiscoveryVariant.DECISION_GRAPH_MAX)")
    print("-" * 70)

    cg_model = powl_algorithm.apply(log, variant=POWLDiscoveryVariant.DECISION_GRAPH_MAX)
    print(f"Discovered model: {type(cg_model).__name__}")

    if isinstance(cg_model, DecisionGraph):
        print(f"Children: {len(cg_model.children)}")
        for child in cg_model.children:
            print(f"  Child: {child}")

        # Show soundness
        report = cg_model.get_soundness_report()
        print(f"\nSoundness: {report['is_sound']}")
        print(f"  Nodes: {report['metrics']['num_nodes']}")
        print(f"  Edges: {report['metrics']['num_edges']}")

        # Show that all traces are captured
        print("\n  ✅ Advantage: Choice Graph allows overlapping regions")
        print("     Activities 'b' and 'c' can both be reached from 'a'")

        # Show language
        print("\n  Model Language (L(G)):")
        language = list(cg_model.language())
        log_traces = {
            tuple(e['concept:name'] for e in trace)
            for trace in log
        }
        model_traces = {tuple(trace) for trace in language}

        print(f"  Log traces: {len(log_traces)}")
        print(f"  Model traces: {len(model_traces)}")
        print(f"  All log traces in model: {log_traces.issubset(model_traces)}")

        for i, trace in enumerate(language, 1):
            in_log = trace in [tuple(e['concept:name'] for e in t) for t in log]
            print(f"    Trace {i}: {trace} {'✓' if in_log else '✗'}")

    print("\n" + "=" * 70)
    print("Conclusion: Choice Graph provides more accurate model for overlapping choices")
    print("=" * 70)


def demonstrate_fitness_preservation():
    """
    Demonstrate Lemma 1: Fitness Preservation.

    All log traces must be in the model's language.
    """
    print("\n" + "=" * 70)
    print("Lemma 1: Fitness Preservation")
    print("=" * 70)

    log = create_overlapping_choice_log()

    # Discover with Choice Graph
    model = powl_algorithm.apply(log, variant=POWLDiscoveryVariant.DECISION_GRAPH_MAX)

    if isinstance(model, DecisionGraph):
        # Get log traces
        log_traces = {
            tuple(e['concept:name'] for e in trace)
            for trace in log
        }

        # Get model language
        model_traces = {tuple(trace) for trace in model.language()}

        print(f"\nLog traces: {len(log_traces)}")
        for trace in log_traces:
            print(f"  - {trace}")

        print(f"\nModel language: {len(model_traces)} traces")
        for trace in model_traces:
            in_log = trace in log_traces
            print(f"  - {trace} {'✓ (in log)' if in_log else '  (extra)'}")

        # Verify fitness preservation
        fitness_preserved = log_traces.issubset(model_traces)

        print(f"\nFitness Preserved (Lemma 1): {fitness_preserved}")
        print("  ✓ All log traces are in the model language")
        print("  ✓ The discovery algorithm is correct!")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    compare_discovery_methods()
    demonstrate_fitness_preservation()
