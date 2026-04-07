'''
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see this software project's root or
visit <https://www.gnu.org/licenses/>.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
'''

"""
Developer Experience (DX) and Quality of Life (QoL) utilities for pm4py.

This module provides high-level convenience functions for common workflows,
inspired by the JavaScript pm4wasm client's utils.ts (469 lines).

Categories:
- Model utilities: POWL model inspection and formatting
- Log utilities: Event log statistics and manipulation
- Conformance utilities: Conformance result analysis and visualization
- Petri net utilities: Petri net inspection and export

Example:
    >>> import pm4py
    >>> from pm4py.dx import log_summary, conformance_table
    >>>
    >>> log = pm4py.read_xes("running-example.xes")
    >>> stats = log_summary(log)
    >>> print(f"Traces: {stats.trace_count}, Variants: {stats.variant_count}")
    >>>
    >>> model = pm4py.discover_powl(log)
    >>> result = pm4py.fitness_token_based_replay(log, model)
    >>> table = conformance_table(log, result)
    >>> print(table)
"""

from typing import List, Dict, Callable, Optional, Any, Tuple
from dataclasses import dataclass
import re

# Import POWL classes for type hints
try:
    from pm4py.objects.powl.obj import POWL, OperatorPOWL, StrictPartialOrder, Transition
except ImportError:
    POWL = None
    OperatorPOWL = None
    StrictPartialOrder = None
    Transition = None


# =============================================================================
# Model Utilities
# =============================================================================

def pretty_print_powl(model: POWL, indent: str = "  ") -> str:
    """
    Pretty-print a POWL model with indentation.

    Parses the POWL string representation and adds newlines and indentation
    for better readability.

    Parameters
    ----------
    model : POWL
        The POWL model to pretty-print.
    indent : str
        Indentation string (default: two spaces).

    Returns
    -------
    str
        Pretty-printed POWL model string.

    Examples
    --------
    >>> from pm4py.objects.powl.parser import parse_powl_model_string
    >>> model = parse_powl_model_string("PO=(nodes={A,X(B,C)},order={A-->X(B,C)})")
    >>> print(pretty_print_powl(model))
    PO=(
      nodes={ A, X(B, C) },
      order={ A-->X(B, C) }
    )
    """
    if model is None:
        return ""

    # Get string representation
    repr_str = str(model)

    # Pretty-print by adding newlines after special characters
    depth = 0
    out = ""
    i = 0
    while i < len(repr_str):
        ch = repr_str[i]
        if ch == "{" or ch == "(":
            out += ch + "\n" + indent * (depth + 1)
            depth += 1
        elif ch == "}" or ch == ")":
            depth -= 1
            out += "\n" + indent * depth + ch
        elif ch == "," and i + 1 < len(repr_str) and repr_str[i + 1] == " ":
            out += ch + "\n" + indent * depth
            i += 1  # skip the trailing space
        else:
            out += ch
        i += 1

    return out.strip()


def model_summary(model: POWL) -> str:
    """
    Generate a compact summary of a POWL model's structure.

    Counts operators, nodes, and edges to provide a quick overview.

    Parameters
    ----------
    model : POWL
        The POWL model to summarize.

    Returns
    -------
    str
        Compact summary string (e.g., "SPO(4 nodes, 3 edges) with XOR(2), LOOP(1)").

    Examples
    --------
    >>> from pm4py.objects.powl.parser import parse_powl_model_string
    >>> model = parse_powl_model_string("X(A, *(B, C))")
    >>> print(model_summary(model))
    """
    if model is None:
        return "Empty model"

    # Import Operator enum for comparison
    try:
        from pm4py.objects.process_tree.obj import Operator
    except ImportError:
        Operator = None

    counts = {}
    edges = 0

    def _visit(node):
        nonlocal edges
        node_type = type(node).__name__

        if node_type == "OperatorPOWL":
            op = node.operator

            # Handle Operator enum (has .name and .value attributes)
            if hasattr(op, 'name') and hasattr(op, 'value'):
                # It's an Operator enum
                op_name = op.name  # "XOR", "LOOP", etc.
            elif isinstance(op, str):
                # Handle string values: "X", "*", "+", "->", "O"
                if op == "X":
                    op_name = "XOR"
                elif op == "*":
                    op_name = "LOOP"
                elif op == "+":
                    op_name = "PARALLEL"
                elif op == "->":
                    op_name = "SEQUENCE"
                elif op == "O":
                    op_name = "OR"
                else:
                    op_name = op
            else:
                # Fallback: use string representation
                op_str = str(op)
                if "XOR" in op_str:
                    op_name = "XOR"
                elif "LOOP" in op_str:
                    op_name = "LOOP"
                elif "PARALLEL" in op_str:
                    op_name = "PARALLEL"
                elif "SEQUENCE" in op_str:
                    op_name = "SEQUENCE"
                elif "OR" in op_str:
                    op_name = "OR"
                else:
                    op_name = op_str

            counts[op_name] = counts.get(op_name, 0) + 1

            for child in node.children:
                _visit(child)

        elif node_type == "StrictPartialOrder":
            counts["SPO"] = counts.get("SPO", 0) + 1
            if hasattr(node, 'order') and node.order:
                edges += len(node.order.edges)

            for child in node.children:
                _visit(child)

        elif node_type == "Transition":
            if hasattr(node, 'label') and node.label:
                counts["activities"] = counts.get("activities", 0) + 1

    _visit(model)

    # Build summary string
    parts = []
    if counts.get("SPO"):
        spo_count = counts["SPO"]
        parts.append(f"{spo_count} SPO ({edges} edges)")

    operator_parts = []
    for op_type in ["XOR", "LOOP", "PARALLEL", "SEQUENCE", "OR"]:
        if counts.get(op_type):
            operator_parts.append(f"{op_type}({counts[op_type]})")

    if operator_parts:
        parts.append(", ".join(operator_parts))

    if counts.get("activities"):
        parts.append(f"{counts['activities']} activities")

    return " with ".join(parts) if parts else "Empty model"


def model_activities(model: POWL) -> List[str]:
    """
    Collect all distinct activity labels from a POWL model.

    Excludes silent transitions (tau/empty labels).

    Parameters
    ----------
    model : POWL
        The POWL model to extract activities from.

    Returns
    -------
    List[str]
        Sorted list of unique activity labels.

    Examples
    --------
    >>> from pm4py.objects.powl.parser import parse_powl_model_string
    >>> model = parse_powl_model_string("X(A, B)")
    >>> model_activities(model)
    ['A', 'B']
    """
    if model is None:
        return []

    activities = set()

    def _visit(node):
        if isinstance(node, Transition):
            # Only include visible transitions (with labels)
            if hasattr(node, 'label') and node.label:
                activities.add(node.label)
        elif hasattr(node, 'children'):
            for child in node.children:
                _visit(child)

    _visit(model)
    return sorted(list(activities))


def powl_to_dot(model: POWL) -> str:
    """
    Render a POWL model as a Graphviz DOT string.

    Converts POWL → Petri net → DOT for visualization.

    Parameters
    ----------
    model : POWL
        The POWL model to convert.

    Returns
    -------
    str
        Graphviz DOT format string.

    Examples
    --------
    >>> from pm4py.objects.powl.parser import parse_powl_model_string
    >>> model = parse_powl_model_string("X(A, B)")
    >>> dot = powl_to_dot(model)
    >>> print(dot)
    digraph {
      rankdir=LR;
      ...
    }
    """
    if model is None:
        return "digraph { }"

    try:
        # Import conversion function
        from pm4py.convert import convert_to_petri_net
        from pm4py.objects.petri_net.obj import PetriNet, Marking

        # Convert POWL to Petri net
        net, im, fm = convert_to_petri_net(model)

        # Convert Petri net to DOT
        return petri_net_to_dot(net, im)

    except Exception as e:
        # Fallback: return simple representation
        return f"digraph {{ \"POWL\" [label=\"{str(model)[:50]}\"]; }}"


def petri_net_to_dot(petri_net, marking) -> str:
    """
    Render a Petri net as a Graphviz DOT string.

    Parameters
    ----------
    petri_net : PetriNet
        The Petri net to convert.
    marking : Marking
        The initial marking (for token display).

    Returns
    -------
    str
        Graphviz DOT format string.

    Examples
    --------
    >>> import pm4py
    >>> net, im, fm = pm4py.discover_petri_net_inductive(log)
    >>> dot = petri_net_to_dot(net, im)
    >>> print(dot)
    """
    lines = ["digraph {", "  rankdir=LR;"]

    # Add places
    for place in petri_net.places:
        tokens = marking.get(place.name, 0)
        if tokens > 0:
            label = f"{place.name} ({tokens})"
        else:
            label = place.name
        lines.append(f'  "{place.name}" [shape=circle, label="{label}"];')

    # Add transitions
    for trans in petri_net.transitions:
        label = trans.label if trans.label else "τ"
        if trans.label:
            style = ""
        else:
            # Silent transition styling
            style = ', style=filled, fillcolor="#555555", fontcolor=white'
        lines.append(f'  "{trans.name}" [shape=box, label="{label}"{style}];')

    # Add arcs
    for arc in petri_net.arcs:
        lines.append(f'  "{arc.source}" -> "{arc.target}";')

    lines.append("}")
    return "\n".join(lines)


def petri_net_activities(petri_net) -> List[str]:
    """
    Get visible activities from a Petri net.

    Returns transitions with non-null labels, sorted alphabetically.

    Parameters
    ----------
    petri_net : PetriNet
        The Petri net to extract activities from.

    Returns
    -------
    List[str]
        Sorted list of activity labels.

    Examples
    --------
    >>> import pm4py
    >>> net, im, fm = pm4py.discover_petri_net_inductive(log)
    >>> petri_net_activities(net)
    ['A', 'B', 'C']
    """
    activities = []

    for trans in petri_net.transitions:
        if trans.label:
            activities.append(trans.label)

    return sorted(list(activities))


# =============================================================================
# Log Utilities
# =============================================================================

@dataclass
class LogStats:
    """
    Comprehensive event log statistics.

    Attributes
    ----------
    trace_count : int
        Number of traces (cases) in the log.
    event_count : int
        Total number of events across all traces.
    activity_count : int
        Number of distinct activities.
    avg_trace_length : float
        Average number of events per trace.
    min_trace_length : int
        Minimum trace length.
    max_trace_length : int
        Maximum trace length.
    variant_count : int
        Number of distinct variants.
    start_activities : List[str]
        Sorted list of start activities.
    end_activities : List[str]
        Sorted list of end activities.
    """
    trace_count: int
    event_count: int
    activity_count: int
    avg_trace_length: float
    min_trace_length: int
    max_trace_length: int
    variant_count: int
    start_activities: List[str]
    end_activities: List[str]

    def __str__(self) -> str:
        """Return a formatted summary string."""
        return (
            f"LogStats(traces={self.trace_count}, events={self.event_count}, "
            f"activities={self.activity_count}, variants={self.variant_count}, "
            f"avg_length={self.avg_trace_length:.1f})"
        )


def log_summary(log):
    """
    Generate comprehensive statistics for an event log.

    Combines multiple pm4py.stats functions into a single call.

    Parameters
    ----------
    log : EventLog or DataFrame
        The event log to analyze.

    Returns
    -------
    LogStats
        Comprehensive log statistics.

    Examples
    --------
    >>> import pm4py
    >>> from pm4py.dx import log_summary
    >>> log = pm4py.read_xes("running-example.xes")
    >>> stats = log_summary(log)
    >>> print(stats)
    LogStats(traces=6, events=42, activities=8, variants=5, avg_length=7.0)
    """
    try:
        from pm4py.stats import get_variants, get_start_activities, get_end_activities
        from pm4py.util import pandas_utils
    except ImportError:
        # Fallback for older pm4py versions
        from pm4py.statistics.traces.generic.log import case_statistics
        from pm4py.statistics.variants.log import get_variants

    # Convert to event log if needed
    from pm4py.convert import convert_to_event_log
    log = convert_to_event_log(log)

    # Basic counts
    trace_count = len(log)
    event_count = sum(len(trace) for trace in log)

    # Trace lengths
    lengths = [len(trace) for trace in log]
    avg_length = sum(lengths) / len(lengths) if lengths else 0.0
    min_length = min(lengths) if lengths else 0
    max_length = max(lengths) if lengths else 0

    # Activities
    activities = set()
    for trace in log:
        for event in trace:
            if "concept:name" in event:
                activities.add(event["concept:name"])
    activity_count = len(activities)

    # Variants
    variants = get_variants(log)
    variant_count = len(variants)

    # Start and end activities
    start_acts_dict = get_start_activities(log)
    start_activities = sorted(list(start_acts_dict.keys()))

    end_acts_dict = get_end_activities(log)
    end_activities = sorted(list(end_acts_dict.keys()))

    return LogStats(
        trace_count=trace_count,
        event_count=event_count,
        activity_count=activity_count,
        avg_trace_length=avg_length,
        min_trace_length=min_length,
        max_trace_length=max_length,
        variant_count=variant_count,
        start_activities=start_activities,
        end_activities=end_activities,
    )


@dataclass
class VariantInfo:
    """
    Information about a variant.

    Attributes
    ----------
    variant : str
        The variant (activity sequence).
    count : int
        Number of traces with this variant.
    frequency : float
        Proportion of traces (0.0 to 1.0).
    """
    variant: str
    count: int
    frequency: float


def top_variants(log, n: int = 10) -> List[VariantInfo]:
    """
    Return the top-N most frequent variants.

    Parameters
    ----------
    log : EventLog or DataFrame
        The event log to analyze.
    n : int
        Number of top variants to return.

    Returns
    -------
    List[VariantInfo]
        List of top-N variants with counts and frequencies.

    Examples
    --------
    >>> import pm4py
    >>> from pm4py.dx import top_variants
    >>> log = pm4py.read_xes("running-example.xes")
    >>> for v in top_variants(log, 3):
    ...     print(f"{v.variant}: {v.count} ({v.frequency:.1%})")
    """
    try:
        from pm4py.stats import get_variants
    except ImportError:
        from pm4py.statistics.variants.log import get_variants

    # Convert to event log if needed
    from pm4py.convert import convert_to_event_log
    log = convert_to_event_log(log)

    # Get variants
    variants = get_variants(log)

    # Handle different return formats from get_variants
    variant_dict = {}
    if isinstance(variants, dict):
        # Dict format: {variant_tuple: trace_list} or {variant_string: count}
        for key, value in variants.items():
            if isinstance(key, tuple):
                # Key is tuple of activities: ('A', 'B')
                variant_str = " → ".join(key)
                if isinstance(value, list):
                    # Value is list of traces
                    variant_dict[variant_str] = len(value)
                else:
                    # Value is count
                    variant_dict[variant_str] = value
            elif isinstance(key, str):
                # Key is variant string
                if isinstance(value, list):
                    variant_dict[key] = len(value)
                else:
                    variant_dict[key] = value
    elif isinstance(variants, list):
        # List format: [(variant_string, count), ...]
        for item in variants:
            if isinstance(item, tuple) and len(item) >= 2:
                variant_dict[item[0]] = item[1]
            elif isinstance(item, list):
                # List of traces
                variant_str = " → ".join([event["concept:name"] for event in item[0]])
                variant_dict[variant_str] = len(item)
    else:
        # Fallback: try to iterate
        try:
            for item in variants:
                if isinstance(item, tuple) and len(item) >= 2:
                    variant_dict[item[0]] = item[1]
        except (TypeError, IndexError):
            variant_dict = {}

    # Calculate total traces
    total = sum(variant_dict.values()) if variant_dict else len(log)

    # Convert to list and sort by count
    variant_list = []
    for variant, count in variant_dict.items():
        frequency = count / total if total > 0 else 0.0
        variant_list.append(VariantInfo(
            variant=variant,
            count=count,
            frequency=frequency
        ))

    # Sort by count (descending) and return top N
    variant_list.sort(key=lambda x: x.count, reverse=True)
    return variant_list[:n]


def truncate_traces(log, k: int):
    """
    Slice log to first k events per trace.

    Useful for prefix analysis or large-log sampling.

    Parameters
    ----------
    log : EventLog or DataFrame
        The event log to truncate.
    k : int
        Maximum number of events per trace.

    Returns
    -------
    EventLog
        Truncated event log.

    Examples
    --------
    >>> import pm4py
    >>> from pm4py.dx import truncate_traces
    >>> log = pm4py.read_xes("running-example.xes")
    >>> truncated = truncate_traces(log, 3)
    """
    from pm4py.convert import convert_to_event_log
    from pm4py.objects.log.obj import EventLog, Trace

    log = convert_to_event_log(log)

    truncated_traces = []
    for trace in log:
        # Create new trace with first k events
        truncated_events = trace._list[:k]

        # Create new trace object
        new_trace = Trace(truncated_events)

        # Copy attributes using internal _attributes
        if hasattr(trace, '_attributes'):
            new_trace._attributes = trace._attributes.copy()

        truncated_traces.append(new_trace)

    return EventLog(truncated_traces, attributes=log.attributes)


def group_by_variant(log) -> Dict[str, List]:
    """
    Group traces by their activity sequence (variant).

    Parameters
    ----------
    log : EventLog or DataFrame
        The event log to group.

    Returns
    -------
    Dict[str, List[Trace]]
        Dictionary mapping variant string to list of traces.

    Examples
    --------
    >>> import pm4py
    >>> from pm4py.dx import group_by_variant
    >>> log = pm4py.read_xes("running-example.xes")
    >>> groups = group_by_variant(log)
    >>> for variant, traces in groups.items():
    ...     print(f"{variant}: {len(traces)} traces")
    """
    try:
        from pm4py.stats import get_variants
    except ImportError:
        from pm4py.statistics.variants.log import get_variants

    from pm4py.convert import convert_to_event_log
    log = convert_to_event_log(log)

    # Get variant for each trace
    variants = get_variants(log)

    # Group traces by variant
    groups = {}
    for trace in log:
        # Find which variant this trace belongs to
        trace_str = ", ".join([event["concept:name"] for event in trace])
        for variant in variants:
            if trace_str == variant:
                if variant not in groups:
                    groups[variant] = []
                groups[variant].append(trace)
                break

    return groups


# =============================================================================
# Conformance Utilities
# =============================================================================

@dataclass
class PartitionedTraces:
    """
    Result of partitioning traces by fitness.

    Attributes
    ----------
    fitting : List
        Traces with fitness >= threshold.
    non_fitting : List
        Traces with fitness < threshold.
    """
    fitting: List
    non_fitting: List


def partition_by_fitness(log, result, threshold: float = 0.8) -> PartitionedTraces:
    """
    Partition traces into fitting / non-fitting at a given threshold.

    Parameters
    ----------
    log : EventLog or DataFrame
        The event log.
    result : dict
        Conformance checking result (from fitness_token_based_replay).
    threshold : float
        Fitness threshold (default: 0.8).

    Returns
    -------
    PartitionedTraces
        Partitioned traces.

    Examples
    --------
    >>> import pm4py
    >>> from pm4py.dx import partition_by_fitness
    >>> log = pm4py.read_xes("running-example.xes")
    >>> model = pm4py.discover_powl(log)
    >>> result = pm4py.fitness_token_based_replay(log, model)
    >>> partitioned = partition_by_fitness(log, result, threshold=0.8)
    >>> print(f"Fitting: {len(partitioned.fitting)}, Non-fitting: {len(partitioned.non_fitting)}")
    """
    from pm4py.convert import convert_to_event_log
    log = convert_to_event_log(log)

    # Extract trace fitness from result
    # Result structure: {"trace_fitness": [...], "log_fitness": ...}
    trace_fitness = result.get("trace_fitness", [])

    fitting = []
    non_fitting = []

    for i, trace in enumerate(log):
        fitness = trace_fitness[i] if i < len(trace_fitness) else 0.0
        if fitness >= threshold:
            fitting.append(trace)
        else:
            non_fitting.append(trace)

    return PartitionedTraces(fitting=fitting, non_fitting=non_fitting)


def activity_fitness(log, result) -> Dict[str, float]:
    """
    Compute per-activity fitness breakdown.

    For each activity, compute the average fitness of traces that contain it.

    Parameters
    ----------
    log : EventLog or DataFrame
        The event log.
    result : dict
        Conformance checking result.

    Returns
    -------
    Dict[str, float]
        Activity to average fitness mapping.

    Examples
    --------
    >>> import pm4py
    >>> from pm4py.dx import activity_fitness
    >>> log = pm4py.read_xes("running-example.xes")
    >>> model = pm4py.discover_powl(log)
    >>> result = pm4py.fitness_token_based_replay(log, model)
    >>> act_fit = activity_fitness(log, result)
    >>> for act, fit in sorted(act_fit.items(), key=lambda x: x[1]):
    ...     print(f"{act}: {fit:.2f}")
    """
    from pm4py.convert import convert_to_event_log
    log = convert_to_event_log(log)

    # Extract trace fitness from result
    trace_fitness = result.get("trace_fitness", [])

    # Compute per-activity fitness
    act_sum = {}
    act_count = {}

    for i, trace in enumerate(log):
        fitness = trace_fitness[i] if i < len(trace_fitness) else 0.0
        seen = set()

        for event in trace:
            if "concept:name" in event:
                act = event["concept:name"]
                if act not in seen:
                    act_sum[act] = act_sum.get(act, 0.0) + fitness
                    act_count[act] = act_count.get(act, 0) + 1
                    seen.add(act)

    # Compute averages
    act_fitness = {}
    for act in act_sum:
        act_fitness[act] = act_sum[act] / act_count[act] if act_count[act] > 0 else 0.0

    return act_fitness


def conformance_table(log, result, max_rows: int = 20) -> str:
    """
    Render conformance result as an ASCII table.

    Parameters
    ----------
    log : EventLog or DataFrame
        The event log.
    result : dict
        Conformance checking result.
    max_rows : int
        Maximum number of traces to display (default: 20).

    Returns
    -------
    str
        ASCII table of conformance results.

    Examples
    --------
    >>> import pm4py
    >>> from pm4py.dx import conformance_table
    >>> log = pm4py.read_xes("running-example.xes")
    >>> model = pm4py.discover_powl(log)
    >>> result = pm4py.fitness_token_based_replay(log, model)
    >>> table = conformance_table(log, result)
    >>> print(table)
    """
    from pm4py.convert import convert_to_event_log
    log = convert_to_event_log(log)

    # Extract trace fitness from result
    trace_fitness = result.get("trace_fitness", [])
    log_fitness = result.get("log_fitness", 0.0)
    total_traces = len(log)

    # Calculate perfectly fitting traces
    perfect = sum(1 for f in trace_fitness if f >= 0.999)

    # Build table rows
    rows = []
    for i, trace in enumerate(log[:max_rows]):
        trace_id = trace.attributes.get("concept:name", f"trace_{i}")
        activities = " → ".join([event.get("concept:name", "?") for event in trace])
        fitness = trace_fitness[i] if i < len(trace_fitness) else 0.0

        # Truncate activities if too long
        if len(activities) > 40:
            activities = activities[:37] + "..."

        rows.append((trace_id, activities, fitness))

    # Calculate column widths
    id_width = max(7, max((len(r[0]) for r in rows), default=7))
    act_width = max(10, min(40, max((len(r[1]) for r in rows), default=10)))
    fit_width = 8

    # Build table
    hr = f"├{'─' * (id_width + 2)}┼{'─' * (act_width + 2)}┼{'─' * (fit_width + 2)}┤"
    top = f"┌{'─' * (id_width + 2)}┬{'─' * (act_width + 2)}┬{'─' * (fit_width + 2)}┐"
    bot = f"└{'─' * (id_width + 2)}┴{'─' * (act_width + 2)}┴{'─' * (fit_width + 2)}┘"

    header = f"│ {'case_id':{id_width}} │ {'activities':{act_width}} │ {'fitness':{fit_width}} │"

    data_rows = []
    for trace_id, activities, fitness in rows:
        pct = f"{fitness * 100:.1f}%"
        data_rows.append(f"│ {trace_id:{id_width}} │ {activities:{act_width}} │ {pct:>{fit_width}} │")

    # Build summary line
    summary = f"Global: {log_fitness * 100:.1f}% | {perfect}/{total_traces} perfect"

    return "\n".join([top, header, hr] + data_rows + [bot, summary])


@dataclass
class FitnessBucket:
    """
    Fitness histogram bucket.

    Attributes
    ----------
    range : str
        Range label (e.g., "0.0-0.1").
    count : int
        Number of traces in this bucket.
    frequency : float
        Proportion of traces (0.0 to 1.0).
    """
    range: str
    count: int
    frequency: float


def fitness_histogram(result, buckets: int = 10) -> List[FitnessBucket]:
    """
    Compute fitness distribution histogram.

    Parameters
    ----------
    result : dict
        Conformance checking result.
    buckets : int
        Number of histogram buckets (default: 10).

    Returns
    -------
    List[FitnessBucket]
        List of histogram buckets.

    Examples
    --------
    >>> import pm4py
    >>> from pm4py.dx import fitness_histogram
    >>> log = pm4py.read_xes("running-example.xes")
    >>> model = pm4py.discover_powl(log)
    >>> result = pm4py.fitness_token_based_replay(log, model)
    >>> histogram = fitness_histogram(result)
    >>> for bucket in histogram:
    ...     print(f"{bucket.range}: {bucket.count} ({bucket.frequency:.1%})")
    """
    # Extract trace fitness from result
    trace_fitness = result.get("trace_fitness", [])

    # Initialize bins
    bins = [0] * buckets

    # Bin the fitness values
    for fitness in trace_fitness:
        b = min(int(fitness * buckets), buckets - 1)
        bins[b] += 1

    # Calculate total
    total = len(trace_fitness) if trace_fitness else 1

    # Create bucket objects
    histogram = []
    for i, count in enumerate(bins):
        range_label = f"{i / buckets:.1f}-{(i + 1) / buckets:.1f}"
        frequency = count / total
        histogram.append(FitnessBucket(
            range=range_label,
            count=count,
            frequency=frequency
        ))

    return histogram


def conformance_batched(
    model,
    log,
    batch_size: int = 50,
    on_progress: Optional[Callable[[int, int], None]] = None
) -> dict:
    """
    Batch conformance checking with progress callback.

    Processes large logs in batches to avoid blocking.
    Calls on_progress(done, total) after each batch.

    Parameters
    ----------
    model : POWL or PetriNet
        The process model.
    log : EventLog or DataFrame
        The event log.
    batch_size : int
        Number of traces per batch (default: 50).
    on_progress : callable, optional
        Progress callback receiving (done, total).

    Returns
    -------
    dict
        Aggregated conformance results.

    Examples
    --------
    >>> import pm4py
    >>> from pm4py.dx import conformance_batched
    >>> log = pm4py.read_xes("large-log.xes")
    >>> model = pm4py.discover_powl(log)
    >>>
    >>> def progress(done, total):
    ...     print(f"Progress: {done}/{total}")
    >>>
    >>> result = conformance_batched(model, log, batch_size=100, on_progress=progress)
    """
    from pm4py.convert import convert_to_event_log
    from pm4py.objects.log.obj import EventLog, Trace
    import pm4py

    log = convert_to_event_log(log)

    total = len(log)
    all_results = []

    # Process in batches
    for i in range(0, total, batch_size):
        # Create batch
        batch_traces = log[i:i + batch_size]
        batch_log = EventLog(batch_traces, attributes=log.attributes)

        # Run conformance on batch
        batch_result = pm4py.fitness_token_based_replay(batch_log, model)

        # Collect results
        if "trace_fitness" in batch_result:
            all_results.extend(batch_result["trace_fitness"])

        # Report progress
        done = min(i + batch_size, total)
        if on_progress:
            on_progress(done, total)

    # Calculate aggregated statistics
    perfect = sum(1 for f in all_results if f >= 0.999)
    avg_fit = sum(all_results) / len(all_results) if all_results else 0.0

    # Calculate overall fitness using token-based replay formula
    # This is simplified; actual implementation would aggregate tokens
    log_fitness = avg_fit  # Simplified

    return {
        "log_fitness": log_fitness,
        "trace_fitness": all_results,
        "total_traces": total,
        "perfectly_fitting_traces": perfect,
        "average_trace_fitness": avg_fit,
    }
