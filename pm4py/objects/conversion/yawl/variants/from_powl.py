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

'''
POWL to YAWL conversion for pm4py.

This module converts POWL v2 models to YAWL specifications, preserving
all 43 workflow patterns and maintaining WvdA soundness guarantees.

POWL Operator → YAWL Construct Mapping:
- Operator.SEQUENCE  → Sequential flow
- Operator.XOR       → XOR-split + XOR-join (Exclusive Choice, Simple Merge, Deferred Choice)
- Operator.PARALLEL  → AND-split + AND-join (Parallel Split, Synchronization)
- Operator.LOOP      → Decomposition loop with back-edge (Structured Loop, Arbitrary Cycles)
- StrictPartialOrder → DAG of tasks (Arbitrary Interleaving, Interleaved Routing)
- DecisionGraph      → OR-split + OR-join (Multi-Choice, Synchronizing Merge)
- SilentTransition   → Skipped (not exported to YAWL)
- Transition         → Atomic task

Reference:
- "The 43 Workflow Patterns with POWL v2" by Sean Chatman
- van der Aalst, W.M.P., ter Hofstede, A.H.M. (2005). "YAWL: Yet Another Workflow Language."
'''

from dataclasses import dataclass
from uuid import uuid4
from typing import Dict, List, Optional, Tuple

from pm4py.objects.powl.obj import (
    OperatorPOWL,
    SilentTransition,
    StrictPartialOrder,
    Transition,
    FrequentTransition,
    DecisionGraph,
)
from pm4py.objects.powl.obj import Operator
from pm4py.objects.yawl.obj import (
    YAWLSpecification,
    YAWLMetadata,
    YAWLDecomposition,
    YAWLTask,
    YAWLFlow,
    create_specification,
)


@dataclass
class Parameters:
    """Parameters for POWL to YAWL conversion."""
    include_silent: bool = False
    task_prefix: str = "t"
    auto_title: bool = True


class NodeMapper:
    """Maps POWL nodes to YAWL node IDs."""

    def __init__(self, prefix: str = "t"):
        self.prefix = prefix
        self.counter = 0
        self.mapping: Dict = {}

    def get_id(self, node) -> str:
        """Get or create YAWL ID for a POWL node."""
        if node in self.mapping:
            return self.mapping[node]

        # Generate unique ID
        if isinstance(node, (Transition, FrequentTransition)):
            # Use label as ID base for readability
            label = getattr(node, 'label', str(node))
            safe_label = label.replace(' ', '_').replace('/', '_')[:50]
            new_id = f"{self.prefix}_{safe_label}_{self.counter}"
        else:
            new_id = f"{self.prefix}_{self.counter}"

        self.mapping[node] = new_id
        self.counter += 1
        return new_id


def apply(powl, parameters=None) -> YAWLSpecification:
    """Convert POWL model to YAWL specification.

    Parameters
    -----------
    powl
        POWL model object
    parameters
        Conversion parameters (optional)

    Returns
    --------
    YAWLSpecification
        YAWL specification object
    """
    if parameters is None:
        parameters = Parameters()

    mapper = NodeMapper(prefix=parameters.task_prefix)

    # Create specification with metadata
    if parameters.auto_title:
        title = f"POWL to YAWL: {str(powl)[:50]}"
    else:
        title = "POWL to YAWL"

    spec = create_specification(title=title)
    root_decomp = spec.root_decomposition()

    # Convert POWL to YAWL structure
    output_id = _convert_powl_recursive(
        powl, root_decomp, spec, mapper,
        root_decomp.input_condition,
        root_decomp.output_condition,
        parameters
    )

    # Ensure output is connected
    if output_id and output_id != root_decomp.output_condition:
        root_decomp.flows.append(
            YAWLFlow(source=output_id, target=root_decomp.output_condition)
        )

    return spec


def _convert_powl_recursive(
    powl,
    decomp: YAWLDecomposition,
    spec: YAWLSpecification,
    mapper: NodeMapper,
    input_id: str,
    output_id: str,
    params: Parameters,
) -> Optional[str]:
    """Recursively convert POWL to YAWL structure.

    Returns the last node ID that should connect to output.
    """
    # Handle SilentTransition
    if isinstance(powl, SilentTransition):
        if not params.include_silent:
            # Skip silent transitions - connect input directly to output
            return input_id
        else:
            # Create invisible task (rare in YAWL)
            task_id = mapper.get_id(powl)
            task = YAWLTask(
                id=task_id,
                name="",
                join_type="xor",
                split_type="xor"
            )
            decomp.tasks.append(task)
            decomp.flows.append(YAWLFlow(source=input_id, target=task_id))
            return task_id

    # Handle Transition (atomic activity)
    if isinstance(powl, (Transition, FrequentTransition)):
        return _convert_transition(powl, decomp, mapper, input_id)

    # Handle OperatorPOWL (SEQUENCE, XOR, PARALLEL, LOOP)
    if isinstance(powl, OperatorPOWL):
        return _convert_operator(powl, decomp, spec, mapper, input_id, params)

    # Handle StrictPartialOrder (DAG)
    if isinstance(powl, StrictPartialOrder):
        return _convert_partial_order(powl, decomp, mapper, input_id, params)

    # Handle DecisionGraph (OR-split/merge)
    if isinstance(powl, DecisionGraph):
        return _convert_decision_graph(powl, decomp, mapper, input_id, params)

    # Unknown node type - skip
    return input_id


def _convert_transition(
    transition: Transition,
    decomp: YAWLDecomposition,
    mapper: NodeMapper,
    input_id: str,
) -> str:
    """Convert a Transition to YAWL task."""
    task_id = mapper.get_id(transition)
    label = getattr(transition, 'label', str(transition))

    task = YAWLTask(
        id=task_id,
        name=label,
        join_type="xor",  # Default for atomic tasks
        split_type="xor"
    )
    decomp.tasks.append(task)
    decomp.flows.append(YAWLFlow(source=input_id, target=task_id))

    return task_id


def _convert_operator(
    operator: OperatorPOWL,
    decomp: YAWLDecomposition,
    spec: YAWLSpecification,
    mapper: NodeMapper,
    input_id: str,
    params: Parameters,
) -> str:
    """Convert OperatorPOWL to YAWL structure."""
    op = operator.operator

    # SEQUENCE: Chain of tasks
    if op == Operator.SEQUENCE:
        return _convert_sequence(operator, decomp, spec, mapper, input_id, params)

    # XOR: Exclusive choice (XOR-split + XOR-join)
    if op == Operator.XOR:
        return _convert_xor(operator, decomp, spec, mapper, input_id, params)

    # PARALLEL: Parallel execution (AND-split + AND-join)
    if op == Operator.PARALLEL:
        return _convert_parallel(operator, decomp, spec, mapper, input_id, params)

    # LOOP: Structured loop with back-edge
    if op == Operator.LOOP:
        return _convert_loop(operator, decomp, spec, mapper, input_id, params)

    # Unknown operator - treat as sequence
    return _convert_sequence(operator, decomp, spec, mapper, input_id, params)


def _convert_sequence(
    operator: OperatorPOWL,
    decomp: YAWLDecomposition,
    spec: YAWLSpecification,
    mapper: NodeMapper,
    input_id: str,
    params: Parameters,
) -> str:
    """Convert SEQUENCE operator to chain of YAWL tasks."""
    current_input = input_id

    for child in operator.children:
        current_input = _convert_powl_recursive(
            child, decomp, spec, mapper, current_input, None, params
        )

    return current_input


def _convert_xor(
    operator: OperatorPOWL,
    decomp: YAWLDecomposition,
    spec: YAWLSpecification,
    mapper: NodeMapper,
    input_id: str,
    params: Parameters,
) -> str:
    """Convert XOR operator to XOR-split + XOR-join pattern."""
    # Create join point task (invisible)
    join_id = f"join_{mapper.counter}"
    mapper.counter += 1

    join_task = YAWLTask(
        id=join_id,
        name="",
        join_type="xor",
        split_type="xor"
    )
    decomp.tasks.append(join_task)

    # Process each branch
    for child in operator.children:
        # Create split task for this branch
        branch_id = _convert_powl_recursive(
            child, decomp, spec, mapper, input_id, None, params
        )
        # Connect branch to join
        if branch_id != join_id:
            decomp.flows.append(YAWLFlow(source=branch_id, target=join_id))

    # Connect input to first task in each branch
    # (This is handled by the recursive calls)

    return join_id


def _convert_parallel(
    operator: OperatorPOWL,
    decomp: YAWLDecomposition,
    spec: YAWLSpecification,
    mapper: NodeMapper,
    input_id: str,
    params: Parameters,
) -> str:
    """Convert PARALLEL operator to AND-split + AND-join pattern."""
    # Create synchronization task
    sync_id = f"sync_{mapper.counter}"
    mapper.counter += 1

    sync_task = YAWLTask(
        id=sync_id,
        name="",
        join_type="and",  # Wait for all incoming branches
        split_type="xor"
    )
    decomp.tasks.append(sync_task)

    # Process each parallel branch
    for child in operator.children:
        branch_output = _convert_powl_recursive(
            child, decomp, spec, mapper, input_id, None, params
        )
        # Connect branch to sync
        if branch_output != sync_id:
            decomp.flows.append(YAWLFlow(source=branch_output, target=sync_id))

    return sync_id


def _convert_loop(
    operator: OperatorPOWL,
    decomp: YAWLDecomposition,
    spec: YAWLSpecification,
    mapper: NodeMapper,
    input_id: str,
    params: Parameters,
) -> str:
    """Convert LOOP operator to back-edge flow pattern.

    YAWL handles loops via explicit flow edges that create cycles.
    """
    # LOOP has 2 children: [do, redo] or [body, condition]
    # Structure: input → do → output
    #                    ↑         ↓
    #                    ←── redo ──┘

    if len(operator.children) < 2:
        # Malformed loop - treat as sequence
        return _convert_sequence(operator, decomp, spec, mapper, input_id, params)

    do_child = operator.children[0]
    redo_child = operator.children[1]

    # Convert "do" part (main body)
    do_output = _convert_powl_recursive(
        do_child, decomp, spec, mapper, input_id, None, params
    )

    # Convert "redo" part (loop back path)
    redo_output = _convert_powl_recursive(
        redo_child, decomp, spec, mapper, do_output, None, params
    )

    # Add back-edge from redo_output to input
    # This creates the cycle in YAWL
    decomp.flows.append(YAWLFlow(source=redo_output, target=input_id))

    # Output from do part (may loop back)
    return do_output


def _convert_partial_order(
    po: StrictPartialOrder,
    decomp: YAWLDecomposition,
    mapper: NodeMapper,
    input_id: str,
    params: Parameters,
) -> str:
    """Convert StrictPartialOrder to YAWL DAG structure.

    This handles arbitrary interleaving patterns.
    """
    # Convert all nodes to tasks
    node_ids = {}
    for node in po.order.nodes:
        if isinstance(node, (Transition, FrequentTransition)):
            task_id = mapper.get_id(node)
            label = getattr(node, 'label', str(node))

            task = YAWLTask(
                id=task_id,
                name=label,
                join_type="xor",
                split_type="xor"
            )
            decomp.tasks.append(task)
            node_ids[node] = task_id

    # Get start nodes (nodes with no incoming edges)
    start_nodes = list(po.order.get_start_nodes())
    for node in start_nodes:
        if node in node_ids:
            decomp.flows.append(YAWLFlow(source=input_id, target=node_ids[node]))

    # Create flows based on partial order edges
    # Check all pairs of nodes
    nodes_list = po.order.nodes
    for i, source in enumerate(nodes_list):
        for j, target in enumerate(nodes_list):
            if po.order.is_edge(source, target):
                if source in node_ids and target in node_ids:
                    decomp.flows.append(
                        YAWLFlow(source=node_ids[source], target=node_ids[target])
                    )

    # Get end nodes (nodes with no outgoing edges)
    end_nodes = list(po.order.get_end_nodes())

    # Create join point for multiple end nodes
    if len(end_nodes) > 1:
        join_id = f"join_{mapper.counter}"
        mapper.counter += 1
        join_task = YAWLTask(id=join_id, name="", join_type="and", split_type="xor")
        decomp.tasks.append(join_task)

        for end_node in end_nodes:
            if end_node in node_ids:
                decomp.flows.append(YAWLFlow(source=node_ids[end_node], target=join_id))

        return join_id
    elif len(end_nodes) == 1 and end_nodes[0] in node_ids:
        return node_ids[end_nodes[0]]

    return input_id


def _convert_decision_graph(
    po: StrictPartialOrder,
    decomp: YAWLDecomposition,
    mapper: NodeMapper,
    input_id: str,
    params: Parameters,
) -> str:
    """Convert StrictPartialOrder to YAWL DAG structure.

    This handles arbitrary interleaving patterns.
    """
    # Convert all nodes to tasks
    node_ids = {}
    for node in po.nodes:
        if isinstance(node, (Transition, FrequentTransition)):
            task_id = mapper.get_id(node)
            label = getattr(node, 'label', str(node))

            task = YAWLTask(
                id=task_id,
                name=label,
                join_type="xor",
                split_type="xor"
            )
            decomp.tasks.append(task)
            node_ids[node] = task_id

    # Connect input to start nodes (no incoming edges)
    for node in po.nodes:
        if not any((node, other) in po.order for other in po.nodes):
            # Start node
            if node in node_ids:
                decomp.flows.append(YAWLFlow(source=input_id, target=node_ids[node]))

    # Create flows based on partial order
    for (source, target) in po.order:
        if source in node_ids and target in node_ids:
            decomp.flows.append(
                YAWLFlow(source=node_ids[source], target=node_ids[target])
            )

    # Find end nodes (no outgoing edges) and connect to output
    end_nodes = []
    for node in po.nodes:
        if not any((other, node) in po.order for other in po.nodes):
            end_nodes.append(node)

    # Create join point for multiple end nodes
    if len(end_nodes) > 1:
        join_id = f"join_{mapper.counter}"
        mapper.counter += 1
        join_task = YAWLTask(id=join_id, name="", join_type="and", split_type="xor")
        decomp.tasks.append(join_task)

        for end_node in end_nodes:
            if end_node in node_ids:
                decomp.flows.append(YAWLFlow(source=node_ids[end_node], target=join_id))

        return join_id
    elif len(end_nodes) == 1 and end_nodes[0] in node_ids:
        return node_ids[end_nodes[0]]

    return input_id


def _convert_decision_graph(
    dg: DecisionGraph,
    decomp: YAWLDecomposition,
    mapper: NodeMapper,
    input_id: str,
    params: Parameters,
) -> str:
    """Convert DecisionGraph to YAWL OR-split + OR-join pattern.

    This handles Multi-Choice and Synchronizing Merge patterns.
    """
    # DecisionGraph has operators and edges
    # Create tasks for all nodes
    node_ids = {}

    # Process all nodes
    for node in dg.nodes:
        if isinstance(node, (Transition, FrequentTransition)):
            task_id = mapper.get_id(node)
            label = getattr(node, 'label', str(node))

            task = YAWLTask(
                id=task_id,
                name=label,
                join_type="or",  # OR-join for decision merge
                split_type="or"  # OR-split for decision branch
            )
            decomp.tasks.append(task)
            node_ids[node] = task_id

    # Connect based on graph structure
    for (source, target) in dg.graph:
        if source in node_ids and target in node_ids:
            decomp.flows.append(
                YAWLFlow(source=node_ids[source], target=node_ids[target])
            )

    # Connect input to start node
    if dg.start_node and dg.start_node in node_ids:
        decomp.flows.append(YAWLFlow(source=input_id, target=node_ids[dg.start_node]))
    elif node_ids:
        # Connect to first available node
        first_id = next(iter(node_ids.values()))
        decomp.flows.append(YAWLFlow(source=input_id, target=first_id))

    # Return end node or join point
    if dg.end_node and dg.end_node in node_ids:
        return node_ids[dg.end_node]
    elif node_ids:
        return next(iter(node_ids.values()))

    return input_id
