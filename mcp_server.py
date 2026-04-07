"""
MCP server exposing pm4py POWL (Partially Ordered Workflow Language) tools.

POWL models are exchanged as their string representation, e.g.:
  PO=(nodes={ A, B, C }, order={ A-->B, A-->C })
  X(A, B)          -- exclusive choice
  *(A, B)          -- loop
  A                -- single activity transition
  tau              -- silent transition

Run with:
  python mcp_server.py
"""

import os
import tempfile
from typing import Optional

import pandas as pd

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("pm4py-powl")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _variant_from_str(variant_str: Optional[str]):
    """Convert a variant name string to the POWLDiscoveryVariant enum value."""
    from pm4py.algo.discovery.powl.algorithm import Variants

    if variant_str is None:
        return None
    mapping = {
        "tree": Variants.TREE,
        "brute_force": Variants.BRUTE_FORCE,
        "maximal": Variants.MAXIMAL,
        "dynamic_clustering": Variants.DYNAMIC_CLUSTERING,
    }
    key = variant_str.lower().strip()
    if key not in mapping:
        raise ValueError(
            f"Unknown variant '{variant_str}'. "
            f"Choose from: {', '.join(mapping.keys())}"
        )
    return mapping[key]


def _powl_summary(powl) -> str:
    """Build a brief structural summary for a POWL object."""
    from pm4py.objects.powl.obj import (
        OperatorPOWL,
        StrictPartialOrder,
        Transition,
        SilentTransition,
    )
    from pm4py.objects.process_tree.obj import Operator

    lines = []

    def _walk(node, depth=0):
        indent = "  " * depth
        if isinstance(node, SilentTransition):
            lines.append(f"{indent}[silent]")
        elif isinstance(node, Transition):
            lines.append(f"{indent}[activity] {node.label}")
        elif isinstance(node, StrictPartialOrder):
            order = node.order
            edge_count = sum(
                1
                for row in order.edges
                for val in row
                if val
            )
            lines.append(
                f"{indent}[partial_order] nodes={len(node.children)}, "
                f"edges={edge_count}"
            )
            for child in node.children:
                _walk(child, depth + 1)
        elif isinstance(node, OperatorPOWL):
            op_name = node.operator.name if node.operator else "unknown"
            lines.append(f"{indent}[operator:{op_name}] children={len(node.children)}")
            for child in node.children:
                _walk(child, depth + 1)
        else:
            lines.append(f"{indent}[node] {type(node).__name__}")

    _walk(powl)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def discover_powl_from_xes(
    xes_file_path: str,
    variant: Optional[str] = None,
) -> str:
    """
    Discover a POWL process model from an XES event log file.

    Args:
        xes_file_path: Absolute path to the .xes event log file.
        variant: Discovery algorithm variant. One of: "tree", "brute_force",
                 "maximal", "dynamic_clustering". Defaults to the library default.

    Returns:
        String representation of the discovered POWL model.
    """
    try:
        import pm4py

        if not os.path.isfile(xes_file_path):
            return f"Error: file not found: {xes_file_path}"

        log = pm4py.read_xes(xes_file_path)
        powl = pm4py.discover_powl(log, variant=_variant_from_str(variant))
        return str(powl)
    except Exception as exc:
        return f"Error: {exc}"


@mcp.tool()
def discover_powl_from_csv(
    csv_file_path: str,
    case_id_col: str = "case:concept:name",
    activity_col: str = "concept:name",
    timestamp_col: str = "time:timestamp",
    variant: Optional[str] = None,
) -> str:
    """
    Discover a POWL process model from a CSV event log file.

    Args:
        csv_file_path: Absolute path to the .csv event log file.
        case_id_col: Column name for the case identifier (default: "case:concept:name").
        activity_col: Column name for the activity label (default: "concept:name").
        timestamp_col: Column name for the timestamp (default: "time:timestamp").
        variant: Discovery algorithm variant. One of: "tree", "brute_force",
                 "maximal", "dynamic_clustering". Defaults to the library default.

    Returns:
        String representation of the discovered POWL model.
    """
    try:
        import pm4py

        if not os.path.isfile(csv_file_path):
            return f"Error: file not found: {csv_file_path}"

        df = pd.read_csv(csv_file_path)
        df = pm4py.format_dataframe(
            df,
            case_id=case_id_col,
            activity_key=activity_col,
            timestamp_key=timestamp_col,
        )
        powl = pm4py.discover_powl(
            df,
            variant=_variant_from_str(variant),
            activity_key=activity_col,
            timestamp_key=timestamp_col,
            case_id_key=case_id_col,
        )
        return str(powl)
    except Exception as exc:
        return f"Error: {exc}"


@mcp.tool()
def parse_powl_model(powl_string: str) -> str:
    """
    Parse a POWL model from its string representation and return structural info.

    The string format uses:
      PO=(nodes={ A, B }, order={ A-->B })  -- partial order
      X(A, B)                               -- exclusive choice (XOR)
      *(A, B)                               -- loop
      A                                     -- single activity
      tau                                   -- silent transition

    Args:
        powl_string: String representation of the POWL model.

    Returns:
        Structural summary of the parsed POWL model.
    """
    try:
        import pm4py

        powl = pm4py.parse_powl_model_string(powl_string)
        summary = _powl_summary(powl)
        return f"Parsed successfully.\n\nString repr:\n{powl}\n\nStructure:\n{summary}"
    except Exception as exc:
        return f"Error: {exc}"


@mcp.tool()
def visualize_powl(
    powl_string: str,
    output_path: Optional[str] = None,
    variant: str = "basic",
    rankdir: str = "TB",
) -> str:
    """
    Visualize a POWL model and save the image to a file.

    Args:
        powl_string: String representation of the POWL model.
        output_path: File path to save the image (e.g. "/tmp/model.png").
                     Defaults to a temporary file.
        variant: Visualization style: "basic" (default) or "net" (BPMN-like gates).
        rankdir: Graph layout direction: "TB" (top-to-bottom, default) or "LR".

    Returns:
        Path to the saved image file.
    """
    try:
        import pm4py

        powl = pm4py.parse_powl_model_string(powl_string)

        if output_path is None:
            suffix = ".png"
            fd, output_path = tempfile.mkstemp(suffix=suffix, prefix="powl_")
            os.close(fd)

        pm4py.save_vis_powl(powl, output_path, rankdir=rankdir, variant_str=variant)
        return f"Visualization saved to: {output_path}"
    except Exception as exc:
        return f"Error: {exc}"


@mcp.tool()
def convert_powl_to_petri_net(powl_string: str) -> str:
    """
    Convert a POWL model to a Petri net and return its structural description.

    Args:
        powl_string: String representation of the POWL model.

    Returns:
        Description of the resulting Petri net (places, transitions, arcs).
    """
    try:
        import pm4py

        powl = pm4py.parse_powl_model_string(powl_string)
        net, im, fm = pm4py.convert_to_petri_net(powl)

        place_names = [p.name for p in net.places]
        trans_labels = [
            t.label if t.label else f"(silent:{t.name})" for t in net.transitions
        ]
        arc_count = len(net.arcs)

        im_places = [p.name for p in im]
        fm_places = [p.name for p in fm]

        return (
            f"Petri net conversion successful.\n\n"
            f"Places ({len(net.places)}): {', '.join(place_names)}\n"
            f"Transitions ({len(net.transitions)}): {', '.join(trans_labels)}\n"
            f"Arcs: {arc_count}\n"
            f"Initial marking: {{{', '.join(im_places)}}}\n"
            f"Final marking: {{{', '.join(fm_places)}}}"
        )
    except Exception as exc:
        return f"Error: {exc}"


@mcp.tool()
def get_powl_model_info(powl_string: str) -> str:
    """
    Return detailed structural information about a POWL model.

    Args:
        powl_string: String representation of the POWL model.

    Returns:
        Detailed structural info: node types, operators, depth, activity labels.
    """
    try:
        import pm4py
        from pm4py.objects.powl.obj import (
            OperatorPOWL,
            StrictPartialOrder,
            Transition,
            SilentTransition,
        )

        powl = pm4py.parse_powl_model_string(powl_string)

        activities = []
        operators = []
        partial_orders = []
        max_depth = [0]

        def _collect(node, depth=0):
            max_depth[0] = max(max_depth[0], depth)
            if isinstance(node, SilentTransition):
                activities.append("tau (silent)")
            elif isinstance(node, Transition):
                activities.append(node.label)
            elif isinstance(node, StrictPartialOrder):
                edge_count = sum(1 for row in node.order.edges for val in row if val)
                partial_orders.append(
                    f"PO(nodes={len(node.children)}, edges={edge_count})"
                )
                for child in node.children:
                    _collect(child, depth + 1)
            elif isinstance(node, OperatorPOWL):
                op_name = node.operator.name if node.operator else "unknown"
                operators.append(op_name)
                for child in node.children:
                    _collect(child, depth + 1)

        _collect(powl)

        return (
            f"POWL Model Info\n"
            f"---------------\n"
            f"String repr: {powl}\n\n"
            f"Activities ({len(activities)}): {', '.join(activities)}\n"
            f"Operators ({len(operators)}): {', '.join(operators) if operators else 'none'}\n"
            f"Partial orders ({len(partial_orders)}): {', '.join(partial_orders) if partial_orders else 'none'}\n"
            f"Model depth: {max_depth[0]}\n\n"
            f"Structure:\n{_powl_summary(powl)}"
        )
    except Exception as exc:
        return f"Error: {exc}"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
