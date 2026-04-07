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

import base64
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from func_timeout import func_set_timeout


@dataclass
class ComplexityMetrics:
    """Complexity metrics for a POWL model."""
    node_count: int = 0
    operator_counts: Dict[str, int] = field(default_factory=dict)
    nesting_depth: int = 0
    activity_count: int = 0
    has_loops: bool = False
    has_xor: bool = False
    has_parallel: bool = False
    sequential_ratio: float = 0.0  # ratio of sequential to total edges
    has_generic_names: bool = False


@dataclass
class StructureInfo:
    """Structural information about a POWL model."""
    start_nodes: List[str] = field(default_factory=list)
    end_nodes: List[str] = field(default_factory=list)
    potential_orphans: List[str] = field(default_factory=list)
    connectivity_valid: bool = True
    partial_orders_valid: bool = True
    has_dead_ends: bool = False


@dataclass
class ConversionResults:
    """Results of converting POWL to other formats."""
    petri_net_success: bool = False
    bpmn_success: bool = False
    process_tree_success: bool = False
    petri_net_place_count: int = 0
    petri_net_transition_count: int = 0


@dataclass
class AnalysisResult:
    """Complete analysis result for a POWL model."""
    is_valid: bool = False
    metrics: ComplexityMetrics = field(default_factory=ComplexityMetrics)
    structure: StructureInfo = field(default_factory=StructureInfo)
    conversion: ConversionResults = field(default_factory=ConversionResults)
    visualization_b64: Optional[str] = None
    issues: List[str] = field(default_factory=list)
    raw_powl: Optional[Any] = None


def _calculate_nesting_depth(powl, current_depth: int = 0) -> int:
    """Recursively calculate the maximum nesting depth of a POWL model."""
    from pm4py.objects.powl.obj import OperatorPOWL, StrictPartialOrder

    if isinstance(powl, OperatorPOWL):
        # For operators, add 1 and recurse into children
        child_depths = [_calculate_nesting_depth(child, current_depth + 1) for child in powl.children]
        return max(child_depths) if child_depths else current_depth + 1
    elif isinstance(powl, StrictPartialOrder):
        # For partial orders, recurse into children
        child_depths = [_calculate_nesting_depth(child, current_depth) for child in powl.children]
        return max(child_depths) if child_depths else current_depth
    else:
        # Leaf node
        return current_depth


def _collect_activities(powl, activities: set = None) -> set:
    """Recursively collect all activity labels from a POWL model."""
    from pm4py.objects.powl.obj import Transition, SilentTransition, OperatorPOWL, StrictPartialOrder

    if activities is None:
        activities = set()

    if isinstance(powl, Transition) and not isinstance(powl, SilentTransition):
        if powl.label:
            activities.add(powl.label)
    elif isinstance(powl, (OperatorPOWL, StrictPartialOrder)):
        for child in powl.children:
            _collect_activities(child, activities)

    return activities


def _check_generic_names(activities: set) -> bool:
    """Check if any activity names are generic (too short or vague)."""
    generic_patterns = {'a', 'b', 'c', 'task', 'activity', 'step', 'action', 'do', 'process'}
    generic_count = sum(1 for act in activities if act.lower() in generic_patterns or len(act) <= 3)
    return generic_count > len(activities) * 0.3  # More than 30% generic


def _count_operators(powl) -> Dict[str, int]:
    """Count operators by type in the POWL model."""
    from pm4py.objects.powl.obj import OperatorPOWL, StrictPartialOrder

    counts = {"XOR": 0, "LOOP": 0, "PO": 0, "SEQUENCE": 0}

    def _visit(node):
        if isinstance(node, OperatorPOWL):
            if node.operator == "XOR":
                counts["XOR"] += 1
            elif node.operator == "LOOP":
                counts["LOOP"] += 1
            for child in node.children:
                _visit(child)
        elif isinstance(node, StrictPartialOrder):
            counts["PO"] += 1
            for child in node.children:
                _visit(child)

    _visit(powl)
    return counts


def _detect_structural_issues(powl) -> List[str]:
    """Detect structural issues in a POWL model."""
    from pm4py.objects.powl.obj import (
        OperatorPOWL, StrictPartialOrder, DecisionGraph,
        Transition, SilentTransition, StartNode, EndNode
    )

    issues = []
    all_nodes = []
    reachable_from_start = set()
    can_reach_end = set()

    def _collect_all_nodes(node, visited=None):
        if visited is None:
            visited = set()
        if id(node) in visited:
            return
        visited.add(id(node))
        all_nodes.append(node)

        if isinstance(node, (OperatorPOWL, StrictPartialOrder)):
            for child in node.children:
                _collect_all_nodes(child, visited)

    _collect_all_nodes(powl)

    # Check for orphaned nodes (not reachable from start)
    # This is a simplified check - full reachability would require graph traversal
    if len(all_nodes) > 1:
        # If we have multiple disconnected components
        for node in all_nodes:
            if isinstance(node, Transition) and node not in reachable_from_start:
                if hasattr(node, 'label') and node.label:
                    issues.append(f"Potentially orphaned activity: '{node.label}'")

    # Validate partial orders
    if isinstance(powl, StrictPartialOrder):
        try:
            powl.validate_partial_orders()
        except Exception as e:
            issues.append(f"Partial order validation failed: {str(e)}")

    # Validate decision graph connectivity
    if isinstance(powl, DecisionGraph):
        try:
            powl.validate_connectivity()
        except Exception as e:
            issues.append(f"Connectivity validation failed: {str(e)}")

    return issues


@func_set_timeout(30)
def calculate_complexity_metrics(powl) -> Dict[str, Any]:
    """Calculate complexity metrics for a POWL model."""
    from pm4py.objects.powl.obj import OperatorPOWL, StrictPartialOrder

    metrics = ComplexityMetrics()

    # Count total nodes (approximate)
    def _count_nodes(node):
        count = 1
        if isinstance(node, (OperatorPOWL, StrictPartialOrder)):
            for child in node.children:
                count += _count_nodes(child)
        return count

    metrics.node_count = _count_nodes(powl)

    # Count operators
    op_counts = _count_operators(powl)
    metrics.operator_counts = op_counts
    metrics.has_loops = op_counts.get("LOOP", 0) > 0
    metrics.has_xor = op_counts.get("XOR", 0) > 0
    metrics.has_parallel = op_counts.get("PO", 0) > 0

    # Calculate nesting depth
    metrics.nesting_depth = _calculate_nesting_depth(powl)

    # Collect activities
    activities = _collect_activities(powl)
    metrics.activity_count = len(activities)

    # Check for generic names
    metrics.has_generic_names = _check_generic_names(activities)

    # Calculate sequential ratio (simplified)
    total_edges = metrics.node_count - 1 if metrics.node_count > 1 else 0
    if total_edges > 0:
        # This is a rough approximation - would need proper edge counting
        metrics.sequential_ratio = min(1.0, op_counts.get("SEQUENCE", 0) / total_edges)

    return asdict(metrics)


@func_set_timeout(30)
def detect_structural_issues(powl) -> Dict[str, Any]:
    """Detect structural issues in a POWL model."""
    from pm4py.objects.powl.obj import StrictPartialOrder, DecisionGraph

    structure = StructureInfo()

    # Collect start and end activities
    activities = _collect_activities(powl)
    if activities:
        structure.start_nodes = list(activities)[:1]  # Simplified
        structure.end_nodes = list(activities)[-1:] if len(activities) > 1 else []

    # Validate partial orders
    try:
        if isinstance(powl, StrictPartialOrder):
            powl.validate_partial_orders()
        structure.partial_orders_valid = True
    except Exception:
        structure.partial_orders_valid = False

    # Validate connectivity
    try:
        if isinstance(powl, DecisionGraph):
            powl.validate_connectivity()
        structure.connectivity_valid = True
    except Exception:
        structure.connectivity_valid = False

    # Detect issues
    issues = _detect_structural_issues(powl)
    structure.potential_orphans = [issue.split(": ")[-1].strip("'") for issue in issues
                                    if "orphaned" in issue.lower()]
    structure.has_dead_ends = len(structure.potential_orphans) > 0

    return asdict(structure)


@func_set_timeout(30)
def convert_and_validate(powl) -> Dict[str, Any]:
    """Convert POWL to other formats and report success."""
    from pm4py.objects.conversion.powl import converter as powl_converter

    conversion = ConversionResults()

    # Try Petri net conversion
    try:
        net, im, fm = powl_converter.apply(powl, variant=powl_converter.TO_PETRI_NET)
        conversion.petri_net_success = True
        conversion.petri_net_place_count = len(net.places)
        conversion.petri_net_transition_count = len(net.transitions)
    except Exception:
        conversion.petri_net_success = False

    # Try BPMN conversion
    try:
        from pm4py.objects.conversion.powl.variants import to_bpmn
        bpmn = to_bpmn.apply(powl)
        conversion.bpmn_success = bpmn is not None
    except Exception:
        conversion.bpmn_success = False

    # Try process tree conversion
    try:
        from pm4py.objects.conversion.powl.variants import to_process_tree
        tree = to_process_tree.apply(powl)
        conversion.process_tree_success = tree is not None
    except Exception:
        conversion.process_tree_success = False

    return asdict(conversion)


@func_set_timeout(30)
def generate_visualization_svg(powl) -> Optional[str]:
    """Generate visualization SVG and return as base64 string."""
    try:
        from pm4py.visualization.powl import visualizer
        svg_content = visualizer.apply(powl, variant=visualizer.Variants.BASIC, parameters={})
        if svg_content:
            return base64.b64encode(svg_content.encode('utf-8')).decode('ascii')
    except Exception:
        pass
    return None


@func_set_timeout(30)
def analyze_powl_comprehensive(powl_string: str, include_visualization: bool = False) -> dict:
    """Perform comprehensive analysis of a POWL model.

    Parameters
    ----------
    powl_string : str
        The POWL model string to analyze.
    include_visualization : bool
        Whether to generate a base64-encoded SVG visualization.

    Returns
    -------
    dict
        With 'return_value' (AnalysisResult dict) and 'errors' (str or None).
    """
    from pm4py.objects.powl.parser import parse_powl_model_string

    try:
        # Parse POWL string
        parsed = parse_powl_model_string(powl_string.strip())

        if parsed is None:
            return {
                "return_value": None,
                "errors": "Failed to parse POWL string"
            }

        # Create analysis result
        result = AnalysisResult()
        result.raw_powl = parsed
        result.is_valid = True

        # Calculate metrics
        try:
            metrics_dict = calculate_complexity_metrics(parsed)
            result.metrics = ComplexityMetrics(**{k: v for k, v in metrics_dict.items()
                                                if k in ComplexityMetrics.__dataclass_fields__})
        except Exception as e:
            result.issues.append(f"Metrics calculation failed: {str(e)}")

        # Detect structural issues
        try:
            structure_dict = detect_structural_issues(parsed)
            result.structure = StructureInfo(**{k: v for k, v in structure_dict.items()
                                              if k in StructureInfo.__dataclass_fields__})
        except Exception as e:
            result.issues.append(f"Structure detection failed: {str(e)}")

        # Convert and validate
        try:
            conversion_dict = convert_and_validate(parsed)
            result.conversion = ConversionResults(**{k: v for k, v in conversion_dict.items()
                                                   if k in ConversionResults.__dataclass_fields__})
        except Exception as e:
            result.issues.append(f"Conversion validation failed: {str(e)}")

        # Generate visualization if requested
        if include_visualization:
            try:
                result.visualization_b64 = generate_visualization_svg(parsed)
            except Exception as e:
                result.issues.append(f"Visualization generation failed: {str(e)}")

        # Collect all detected issues
        result.issues.extend(_detect_structural_issues(parsed))

        # If any structural validation failed, mark as invalid
        if not result.structure.connectivity_valid or not result.structure.partial_orders_valid:
            result.is_valid = False

        return {
            "return_value": asdict(result),
            "errors": None
        }

    except Exception as e:
        return {
            "return_value": None,
            "errors": str(e)
        }


# DSPy tool wrapper
def analyze_powl(powl_string: str, include_visualization: bool = False) -> dict:
    """DSPy tool wrapper for comprehensive POWL analysis.

    Returns dict with 'return_value' (AnalysisResult) and 'errors'.
    """
    return analyze_powl_comprehensive(powl_string, include_visualization)
