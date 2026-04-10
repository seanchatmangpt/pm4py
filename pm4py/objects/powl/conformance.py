"""
Conformance Checking for POWL Models

Provides utilities to check if event traces conform to a discovered POWL model.
"""

from typing import List, Tuple, Set
from pm4py.objects.log.obj import EventLog, Trace
from pm4py.objects.powl.obj import POWL, DecisionGraph


def check_trace_conformance(trace: Tuple[str, ...], model: POWL) -> dict:
    """
    Check if a single trace conforms to the model.

    Args:
        trace: Tuple of activity names representing the trace
        model: POWL model (DecisionGraph or other)

    Returns:
        Dictionary with conformance results:
        - conforms: bool - whether trace is in model language
        - reason: str - explanation if not conforming
    """
    if isinstance(model, DecisionGraph):
        # Get model language
        model_traces = {tuple(t) for t in model.language()}

        if trace in model_traces:
            return {
                'conforms': True,
                'reason': 'Trace is in model language'
            }
        else:
            # Try to find similar traces
            similar = []
            for model_trace in model_traces:
                if len(set(trace) & set(model_trace)) > 0:
                    similar.append(model_trace)

            return {
                'conforms': False,
                'reason': f'Trace not in model language',
                'similar_traces': similar[:3]  # Show up to 3 similar traces
            }
    else:
        return {
            'conforms': None,
            'reason': 'Conformance checking only implemented for DecisionGraph'
        }


def check_log_conformance(log: EventLog, model: POWL) -> dict:
    """
    Check conformance of an entire event log against a POWL model.

    Args:
        log: Event log to check
        model: POWL model

    Returns:
        Dictionary with conformance results:
        - total_traces: int - total number of traces in log
        - conforming_traces: int - number of traces in model language
        - fitness: float - percentage (0.0 to 1.0)
        - non_conforming_traces: list - traces not in model language
    """
    if not isinstance(model, DecisionGraph):
        return {
            'error': 'Conformance checking only implemented for DecisionGraph'
        }

    # Get log traces
    log_traces = [tuple(e['concept:name'] for e in trace) for trace in log]

    # Get model language
    model_traces = {tuple(t) for t in model.language()}

    # Check each trace
    conforming = []
    non_conforming = []

    for trace in log_traces:
        if trace in model_traces:
            conforming.append(trace)
        else:
            non_conforming.append(trace)

    total = len(log_traces)
    conforming_count = len(conforming)
    fitness = conforming_count / total if total > 0 else 0.0

    return {
        'total_traces': total,
        'conforming_traces': conforming_count,
        'non_conforming_traces': len(non_conforming),
        'fitness': fitness,
        'non_conforming_trace_list': non_conforming,
        'model_language_size': len(model_traces)
    }


def print_conformance_report(log: EventLog, model: POWL):
    """
    Print a formatted conformance report.

    Args:
        log: Event log to check
        model: POWL model
    """
    if not isinstance(model, DecisionGraph):
        print("Conformance checking only implemented for DecisionGraph models")
        return

    result = check_log_conformance(log, model)

    print("=" * 70)
    print("Conformance Report")
    print("=" * 70)
    print(f"\nTotal traces in log: {result['total_traces']}")
    print(f"Conforming traces: {result['conforming_traces']}")
    print(f"Non-conforming traces: {result['non_conforming_traces']}")
    print(f"Fitness: {result['fitness']:.2%}")
    print(f"Model language size: {result['model_language_size']} traces")

    if result['non_conforming_traces'] > 0:
        print("\nNon-conforming traces:")
        for i, trace in enumerate(result['non_conforming_trace_list'], 1):
            print(f"  {i}. {trace}")

    # Check soundness
    report = model.get_soundness_report()
    print(f"\nModel Soundness: {report['is_sound']}")
    print(f"  - Connectivity: {report['metrics']['connectivity']}")
    print(f"  - Acyclicity: {report['metrics']['acyclicity']}")
    print(f"  - Structural soundness: {report['metrics']['structural_soundness']}")

    print("\n" + "=" * 70)
