"""
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions UG (haftungsbeschränkt)

Licensed under the GNU AGPL v3.0 - see LICENSE file for details.
"""

"""
Format Conversion: POWL 2.0 DecisionGraph → BPMN/Petri Net

Verifies that Choice Graph models can be converted to PM4Py's other formats.
"""

from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.algo.discovery.powl import algorithm as powl_algorithm
from pm4py.algo.discovery.powl.inductive.variants.powl_discovery_varaints import POWLDiscoveryVariant
from pm4py.objects.powl.obj import DecisionGraph, OperatorPOWL, Transition
from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.visualization.powl import visualizer as powl_visualizer
from pm4py.visualization.bpmn import visualizer as bpmn_visualizer
from pm4py.visualization.petri_net import visualizer as pn_visualizer
import tempfile
import os


def create_test_log():
    """Create a simple test log with overlapping choices."""
    log = EventLog()

    # a -> b -> d
    log.append(Trace([
        Event({'concept:name': 'a'}),
        Event({'concept:name': 'b'}),
        Event({'concept:name': 'd'}),
    ]))

    # a -> c -> d
    log.append(Trace([
        Event({'concept:name': 'a'}),
        Event({'concept:name': 'c'}),
        Event({'concept:name': 'd'}),
    ]))

    # a -> b -> c -> d (overlapping!)
    log.append(Trace([
        Event({'concept:name': 'a'}),
        Event({'concept:name': 'b'}),
        Event({'concept:name': 'c'}),
        Event({'concept:name': 'd'}),
    ]))

    return log


def discover_choice_graph(log):
    """Discover a Choice Graph model."""
    model = powl_algorithm.apply(log, variant=POWLDiscoveryVariant.DECISION_GRAPH_MAX)

    if isinstance(model, DecisionGraph):
        print(f"✓ Discovered DecisionGraph with {len(model.children)} children")

        # Show soundness
        report = model.get_soundness_report()
        print(f"  Soundness: {report['is_sound']}")
        print(f"  Nodes: {report['metrics']['num_nodes']}")
        print(f"  Edges: {report['metrics']['num_edges']}")

    return model


def visualize_powl(model, filename):
    """Generate POWL visualization."""
    try:
        gviz = powl_visualizer.apply(model)
        powl_visualizer.save(gviz, filename)
        print(f"✓ POWL visualization saved: {filename}")
        return True
    except Exception as e:
        print(f"✗ POWL visualization failed: {e}")
        return False


def convert_to_bpmn(model):
    """
    Convert DecisionGraph to BPMN.

    Note: PM4Py's POWL→BPMN conversion may have limitations for
    non-block-structured Choice Graphs. This example demonstrates
    the conversion attempt.
    """
    print("\n" + "-" * 70)
    print("Converting to BPMN...")
    print("-" * 70)

    try:
        # Try PM4Py's POWL→BPMN conversion
        from pm4py.objects.conversion.powl.converter import convert as powl_to_bpmn

        bpmn: BPMN = powl_to_bpmn.apply(model)

        print(f"✓ Converted to BPMN")
        print(f"  Process: {bpmn.get_process_by_id(bpmn.get_processes()[0].get_id()).get_name()}")
        print(f"  Nodes: {len(bpmn.get_nodes())}")
        print(f"  Edges: {len(bpmn.get_flows())}")

        # Visualize BPMN
        gviz = bpmn_visualizer.apply(bpmn)
        filename = tempfile.mktemp(suffix=".png")
        bpmn_visualizer.save(gviz, filename)
        print(f"  ✓ BPMN visualization saved: {filename}")

        return bpmn

    except NotImplementedError as e:
        print(f"⚠️  BPMN conversion not implemented: {e}")
        print("  → Choice Graphs may require specialized BPMN export")
        return None
    except Exception as e:
        print(f"✗ BPMN conversion failed: {e}")
        return None


def convert_to_petri_net(model):
    """
    Convert DecisionGraph to Petri Net.

    Note: PM4Py's POWL→PNML conversion may have limitations for
    non-block-structured Choice Graphs. This example demonstrates
    the conversion attempt.
    """
    print("\n" + "-" * 70)
    print("Converting to Petri Net...")
    print("-" * 70)

    try:
        # Try PM4Py's POWL→Petri Net conversion
        from pm4py.objects.conversion.powl.converter import convert as powl_to_pn

        net, im, fm = powl_to_pn.apply(model)

        print(f"✓ Converted to Petri Net")
        print(f"  Places: {len(net.places)}")
        print(f"  Transitions: {len(net.transitions)}")
        print(f"  Arcs: {len(net.arcs)}")

        # Visualize Petri Net
        gviz = pn_visualizer.apply(net, im, fm)
        filename = tempfile.mktemp(suffix=".png")
        pn_visualizer.save(gviz, filename)
        print(f"  ✓ Petri Net visualization saved: {filename}")

        return net, im, fm

    except NotImplementedError as e:
        print(f"⚠️  Petri Net conversion not implemented: {e}")
        print("  → Choice Graphs may require specialized PNML export")
        return None, None, None
    except Exception as e:
        print(f"✗ Petri Net conversion failed: {e}")
        return None, None, None


def test_conversion_on_simple_model():
    """Test conversion on a simple (block-structured) POWL model."""
    print("\n" + "=" * 70)
    print("Test 1: Simple Block-Structured POWL (XOR)")
    print("=" * 70)

    # Create simple XOR log (block-structured)
    log = EventLog([
        Trace([Event({'concept:name': 'a'}), Event({'concept:name': 'b'})]),
        Trace([Event({'concept:name': 'a'}), Event({'concept:name': 'c'})]),
    ])

    # Discover with MAXIMAL (block-structured)
    model = powl_algorithm.apply(log, variant=POWLDiscoveryVariant.MAXIMAL)

    print(f"Discovered: {type(model).__name__}")

    if isinstance(model, OperatorPOWL):
        print(f"Operator: {model.operator}")
        print(f"Children: {len(model.children)}")

    # Try conversions
    convert_to_bpmn(model)
    convert_to_petri_net(model)


def test_conversion_on_choice_graph():
    """Test conversion on a Choice Graph model."""
    print("\n" + "=" * 70)
    print("Test 2: Choice Graph (Non-Block-Structured)")
    print("=" * 70)

    # Create overlapping choice log
    log = create_test_log()

    # Discover with Choice Graph
    model = discover_choice_graph(log)

    # Visualize POWL
    print("\n" + "-" * 70)
    print("Visualizing Choice Graph...")
    print("-" * 70)
    visualize_powl(model, "choice_graph.png")

    # Try conversions (may not be fully supported)
    bpmn = convert_to_bpmn(model)
    net, im, fm = convert_to_petri_net(model)

    # Summary
    print("\n" + "-" * 70)
    print("Conversion Summary")
    print("-" * 70)
    print("Choice Graphs are a new POWL 2.0 feature.")
    print("Full BPMN/PNML conversion support may be pending.")


def test_roundtrip_conversion():
    """
    Test roundtrip conversion: POWL → BPMN → POWL
    """
    print("\n" + "=" * 70)
    print("Test 3: Roundtrip Conversion (POWL → BPMN → POWL)")
    print("=" * 70)

    # Create simple log
    log = EventLog([
        Trace([Event({'concept:name': 'a'}), Event({'concept:name': 'b'}])],
    ])

    # Discover POWL
    powl_model = powl_algorithm.apply(log, variant=POWLDiscoveryVariant.MAXIMAL)
    print(f"Original POWL: {type(powl_model).__name__}")

    try:
        # Convert to BPMN
        from pm4py.objects.conversion.powl.converter import convert as powl_to_bpmn
        bpmn_model = powl_to_bpmn.apply(powl_model)
        print(f"✓ Converted to BPMN")

        # Convert back to POWL
        from pm4py.objects.conversion.bpmn.converter import convert as bpmn_to_powl
        powl_reconstructed = bpmn_to_powl.apply(bpmn_model)
        print(f"✓ Converted back to POWL: {type(powl_reconstructed).__name__}")

    except Exception as e:
        print(f"⚠️  Roundtrip conversion: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("POWL 2.0 Format Conversion Tests")
    print("=" * 70)

    # Run tests
    test_conversion_on_simple_model()
    test_conversion_on_choice_graph()
    test_roundtrip_conversion()

    print("\n" + "=" * 70)
    print("Conversion Tests Completed!")
    print("=" * 70)
    print("\nNote: Choice Graph → BPMN/PNML conversion may require")
    print("      specialized export logic for non-block-structured models.")
    print("=" * 70)
