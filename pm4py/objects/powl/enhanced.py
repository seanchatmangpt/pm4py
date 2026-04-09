"""
Enhanced POWL objects with frequency, serialization, and graph traversal mixins.

This module extends PM4Py's POWL implementation with features needed for ostar:
- Frequency tagging (min_freq, max_freq)
- Dict serialization (.to_dict()/.from_dict())
- Graph traversal API (.get_nodes(), .get_edges(), .successors(), .predecessors())
- Start/end node management for choice-like structures

These additions maintain Apache 2.0 license compatibility by implementing
functionality independently rather than copying AGPL-licensed code.
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Type, TypeVar, Union
from abc import ABC, abstractmethod

from pm4py.objects.powl.BinaryRelation import BinaryRelation
from pm4py.objects.powl.constants import STRICT_PARTIAL_ORDER_LABEL
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.util import hie_utils
import sys

from .frequency import FrequencyTagged
from .serializable import SerializablePOWL
from .graph_base import GraphTraversable, StartEndNodes
from .types import ModelType


T = TypeVar('T', bound='EnhancedPOWL')


class EnhancedPOWL(ProcessTree, FrequencyTagged, SerializablePOWL, ABC):
    """
    Base class for enhanced POWL objects with mixins.

    Combines PM4Py's ProcessTree with frequency tagging and serialization.
    """

    def __init__(self, *args, min_freq: int = 1, max_freq: Optional[int] = None, **kwargs):
        ProcessTree.__init__(self, *args, **kwargs)
        FrequencyTagged.__init__(self, *args, min_freq=min_freq, max_freq=max_freq, **kwargs)

    @abstractmethod
    def model_type(self) -> ModelType:
        """Get model type for serialization."""
        pass


class EnhancedTransition(EnhancedPOWL):
    """
    Enhanced Transition with frequency tagging and serialization.

    Represents an activity in a POWL model.
    """

    transition_id: int = 0

    def __init__(
        self,
        label: Optional[str] = None,
        min_freq: int = 1,
        max_freq: Optional[int] = None
    ) -> None:
        super().__init__(min_freq=min_freq, max_freq=max_freq)
        self._label = label
        self._identifier = EnhancedTransition.transition_id
        EnhancedTransition.transition_id += 1

    @property
    def label(self) -> Optional[str]:
        """Get activity label."""
        return self._label

    def model_type(self) -> ModelType:
        """Get model type for serialization."""
        return ModelType.ACTIVITY

    def is_silent(self) -> bool:
        """Check if this is a silent transition (no label)."""
        return self._label is None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "type": self.model_type().value,
            "label": self._label,
            "identifier": self._identifier,
            **self._serialize_frequency()
        }

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Deserialize from dictionary."""
        min_freq, max_freq = cls._deserialize_frequency(data)
        return cls(
            label=data.get("label"),
            min_freq=min_freq,
            max_freq=max_freq
        )

    def copy(self) -> "EnhancedTransition":
        """Create a copy of this transition."""
        return EnhancedTransition(self._label, self.min_freq, self.max_freq)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, EnhancedTransition):
            return (
                self._label == other._label
                and self._identifier == other._identifier
            )
        return False

    def equal_content(self, other: object) -> bool:
        if isinstance(other, EnhancedTransition):
            return self._label == other._label
        return False

    def __hash__(self) -> int:
        return self._identifier

    def __repr__(self) -> str:
        if self._label:
            return f"Transition({self._label})"
        return "Transition(silent)"


class EnhancedSilentTransition(EnhancedTransition):
    """Enhanced silent transition (tau)."""

    def __init__(self) -> None:
        super().__init__(label=None)

    def copy(self) -> "EnhancedSilentTransition":
        """Create a copy of this silent transition."""
        return EnhancedSilentTransition()

    def __repr__(self) -> str:
        return "SilentTransition()"


class EnhancedFrequentTransition(EnhancedTransition):
    """
    Enhanced transition with frequency information.

    Represents activities that can be skipped or repeated.
    """

    def __init__(
        self,
        label: Optional[str] = None,
        min_freq: int = 1,
        max_freq: Optional[int] = None
    ) -> None:
        super().__init__(label=label, min_freq=min_freq, max_freq=max_freq)

    @property
    def skippable(self) -> bool:
        """Check if this transition can be skipped."""
        return self.min_freq == 0

    @property
    def selfloop(self) -> bool:
        """Check if this transition can repeat indefinitely."""
        return self.max_freq is None

    def copy(self) -> "EnhancedFrequentTransition":
        """Create a copy."""
        return EnhancedFrequentTransition(self._label, self.min_freq, self.max_freq)

    def __repr__(self) -> str:
        freq_str = f"[{self.min_freq}"
        if self.max_freq != self.min_freq:
            if self.max_freq is None:
                freq_str += "-*]"
            else:
                freq_str += f"-{self.max_freq}]"
        else:
            freq_str += "]"
        return f"FrequentTransition({self._label}{freq_str})"


class EnhancedStrictPartialOrder(
    EnhancedPOWL,
    GraphTraversable
):
    """
    Enhanced partial order with serialization and graph traversal.

    Represents a set of nodes with ordering constraints.
    """

    def __init__(
        self,
        nodes: List["EnhancedPOWL"],
        min_freq: int = 1,
        max_freq: Optional[int] = None
    ) -> None:
        super().__init__(min_freq=min_freq, max_freq=max_freq)
        self.operator = Operator.PARTIALORDER
        self._set_order(nodes)
        self.additional_information = None

    def _set_order(self, nodes: List["EnhancedPOWL"]) -> None:
        """Set the binary relation for this partial order."""
        self.order = BinaryRelation(nodes)

    def model_type(self) -> ModelType:
        """Get model type for serialization."""
        return ModelType.PARTIAL_ORDER

    def get_nodes(self) -> List["EnhancedPOWL"]:
        """Get all nodes in this partial order."""
        return list(self.order.nodes)

    def get_edges(self) -> List[Tuple["EnhancedPOWL", "EnhancedPOWL"]]:
        """Get all edges in this partial order."""
        edges = []
        for source in self.order.nodes:
            for target in self.order.nodes:
                if self.order.is_edge(source, target):
                    edges.append((source, target))
        return edges

    def successors(self, node: "EnhancedPOWL") -> List["EnhancedPOWL"]:
        """Get immediate successors of a node."""
        return list(self.order.get_postset(node))

    def predecessors(self, node: "EnhancedPOWL") -> List["EnhancedPOWL"]:
        """Get immediate predecessors of a node."""
        return list(self.order.get_preset(node))

    def add_edge(self, source: "EnhancedPOWL", target: "EnhancedPOWL") -> None:
        """Add an edge between two nodes."""
        self.order.add_edge(source, target)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "type": self.model_type().value,
            "nodes": self._serialize_children(list(self.order.nodes)),
            "edges": [
                {"source": self.order.nodes.index(src), "target": self.order.nodes.index(tgt)}
                for src in self.order.nodes
                for tgt in self.order.nodes
                if self.order.is_edge(src, tgt)
            ],
            **self._serialize_frequency()
        }

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Deserialize from dictionary."""
        min_freq, max_freq = cls._deserialize_frequency(data)

        # Deserialize nodes
        nodes_data = data.get("nodes", [])
        nodes = cls._deserialize_children(None, nodes_data)

        # Create partial order
        result = cls(nodes, min_freq=min_freq, max_freq=max_freq)

        # Add edges
        for edge in data.get("edges", []):
            source_idx = edge["source"]
            target_idx = edge["target"]
            if 0 <= source_idx < len(nodes) and 0 <= target_idx < len(nodes):
                result.add_edge(nodes[source_idx], nodes[target_idx])

        return result

    def copy(self) -> "EnhancedStrictPartialOrder":
        """Create a copy of this partial order."""
        copied_nodes = {n: n.copy() for n in self.order.nodes}
        res = EnhancedStrictPartialOrder(list(copied_nodes.values()))
        for n1 in self.order.nodes:
            for n2 in self.order.nodes:
                if self.order.is_edge(n1, n2):
                    res.add_edge(copied_nodes[n1], copied_nodes[n2])
        return res

    @property
    def partial_order(self) -> BinaryRelation:
        """Get the binary relation."""
        return self.order

    @partial_order.setter
    def partial_order(self, value: BinaryRelation) -> None:
        """Set the binary relation."""
        self.order = value

    @property
    def children(self) -> List["EnhancedPOWL"]:
        """Get child nodes."""
        return list(self.order.nodes)

    @children.setter
    def children(self, value: List["EnhancedPOWL"]) -> None:
        """Set child nodes."""
        self.order.nodes = value

    def __repr__(self) -> str:
        return f"StrictPartialOrder({len(self.order.nodes)} nodes, {len(self.get_edges())} edges)"


class EnhancedSequence(EnhancedStrictPartialOrder):
    """
    Enhanced sequence (strict partial order with sequential edges).

    All nodes are ordered sequentially.
    """

    def __init__(
        self,
        nodes: List["EnhancedPOWL"],
        min_freq: int = 1,
        max_freq: Optional[int] = None
    ) -> None:
        super().__init__(nodes, min_freq=min_freq, max_freq=max_freq)
        # Add sequential edges
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                self.add_edge(nodes[i], nodes[j])

    def __repr__(self) -> str:
        labels = [n.label if hasattr(n, 'label') and n.label else "tau" for n in self.children]
        return f"Sequence({' -> '.join(labels)})"


class EnhancedOperatorPOWL(EnhancedPOWL):
    """
    Enhanced operator POWL (XOR, LOOP).

    Represents control-flow operators.
    """

    def __init__(
        self,
        operator: Operator,
        children: List["EnhancedPOWL"],
        min_freq: int = 1,
        max_freq: Optional[int] = None
    ) -> None:
        super().__init__(min_freq=min_freq, max_freq=max_freq)
        if operator is Operator.XOR:
            if len(children) < 2:
                raise ValueError("Cannot create a choice of less than 2 submodels!")
        elif operator is Operator.LOOP:
            if len(children) != 2:
                raise ValueError("Only loops of length 2 are supported!")
        else:
            raise ValueError("Unsupported Operator!")

        self.operator = operator
        self.children = children

    def model_type(self) -> ModelType:
        """Get model type for serialization."""
        if self.operator == Operator.LOOP:
            return ModelType.LOOP
        return ModelType.OPERATOR

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "type": self.model_type().value,
            "operator": self.operator.name,
            "children": self._serialize_children(self.children),
            **self._serialize_frequency()
        }

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Deserialize from dictionary."""
        min_freq, max_freq = cls._deserialize_frequency(data)

        # Deserialize operator
        operator_name = data.get("operator", "XOR")
        operator = Operator[operator_name]

        # Deserialize children
        children = cls._deserialize_children(None, data.get("children", []))

        return cls(operator, children, min_freq=min_freq, max_freq=max_freq)

    def copy(self) -> "EnhancedOperatorPOWL":
        """Create a copy."""
        copied_nodes = [n.copy() for n in self.children]
        return EnhancedOperatorPOWL(self.operator, copied_nodes)

    def __repr__(self) -> str:
        op_name = "XOR" if self.operator == Operator.XOR else "LOOP"
        return f"OperatorPOWL({op_name}, {len(self.children)} children)"


class EnhancedChoiceGraph(
    EnhancedPOWL,
    GraphTraversable,
    StartEndNodes
):
    """
    Enhanced choice graph with start/end node management.

    Represents non-block-structured choices.
    """

    def __init__(
        self,
        nodes: List["EnhancedPOWL"],
        min_freq: int = 1,
        max_freq: Optional[int] = None
    ) -> None:
        super().__init__(min_freq=min_freq, max_freq=max_freq)
        self._nodes = list(nodes)
        self._start_nodes: Set["EnhancedPOWL"] = set()
        self._end_nodes: Set["EnhancedPOWL"] = set()
        self._edges: Set[Tuple["EnhancedPOWL", "EnhancedPOWL"]] = set()

    def model_type(self) -> ModelType:
        """Get model type for serialization."""
        return ModelType.CHOICE_GRAPH

    def get_nodes(self) -> List["EnhancedPOWL"]:
        """Get all nodes."""
        return list(self._nodes)

    def get_edges(self) -> List[Tuple["EnhancedPOWL", "EnhancedPOWL"]]:
        """Get all edges."""
        return list(self._edges)

    def add_node(self, node: "EnhancedPOWL") -> None:
        """Add a node to the choice graph."""
        if node not in self._nodes:
            self._nodes.append(node)

    def add_edge(self, source: "EnhancedPOWL", target: "EnhancedPOWL") -> None:
        """Add an edge between two nodes."""
        self._edges.add((source, target))

    def start_nodes(self) -> List["EnhancedPOWL"]:
        """Get start nodes."""
        if self._start_nodes:
            return list(self._start_nodes)
        # Compute start nodes (nodes with no predecessors)
        return [n for n in self._nodes if not any(s == n for _, t in self._edges)]

    def end_nodes(self) -> List["EnhancedPOWL"]:
        """Get end nodes."""
        if self._end_nodes:
            return list(self._end_nodes)
        # Compute end nodes (nodes with no successors)
        return [n for n in self._nodes if not any(t == n for s, t in self._edges)]

    def successors(self, node: "EnhancedPOWL") -> List["EnhancedPOWL"]:
        """Get immediate successors."""
        return [t for s, t in self._edges if s == node]

    def predecessors(self, node: "EnhancedPOWL") -> List["EnhancedPOWL"]:
        """Get immediate predecessors."""
        return [s for s, t in self._edges if t == node]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        # Get node indices for edges
        node_indices = {node: i for i, node in enumerate(self._nodes)}

        return {
            "type": self.model_type().value,
            "nodes": self._serialize_children(self._nodes),
            "edges": [
                {"source": node_indices[src], "target": node_indices[tgt]}
                for src, tgt in self._edges
            ],
            "start_nodes": [node_indices[n] for n in self.start_nodes()],
            "end_nodes": [node_indices[n] for n in self.end_nodes()],
            **self._serialize_frequency()
        }

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Deserialize from dictionary."""
        min_freq, max_freq = cls._deserialize_frequency(data)

        # Deserialize nodes
        nodes = cls._deserialize_children(None, data.get("nodes", []))
        result = cls(nodes, min_freq=min_freq, max_freq=max_freq)

        # Add edges
        node_list = result.get_nodes()
        for edge in data.get("edges", []):
            source_idx = edge["source"]
            target_idx = edge["target"]
            if 0 <= source_idx < len(node_list) and 0 <= target_idx < len(node_list):
                result.add_edge(node_list[source_idx], node_list[target_idx])

        # Set start/end nodes
        for idx in data.get("start_nodes", []):
            if 0 <= idx < len(node_list):
                result.mark_start(node_list[idx])

        for idx in data.get("end_nodes", []):
            if 0 <= idx < len(node_list):
                result.mark_end(node_list[idx])

        return result

    def copy(self) -> "EnhancedChoiceGraph":
        """Create a copy."""
        copied_nodes = [n.copy() for n in self._nodes]
        result = EnhancedChoiceGraph(copied_nodes)
        for src, tgt in self._edges:
            result.add_edge(copied_nodes[copied_nodes.index(src)], copied_nodes[copied_nodes.index(tgt)])
        for node in self._start_nodes:
            result.mark_start(copied_nodes[self._nodes.index(node)])
        for node in self._end_nodes:
            result.mark_end(copied_nodes[self._nodes.index(node)])
        return result

    def __repr__(self) -> str:
        return f"ChoiceGraph({len(self._nodes)} nodes, {len(self._edges)} edges)"


# Type aliases for API compatibility
Activity = EnhancedTransition
PartialOrder = EnhancedStrictPartialOrder
ChoiceGraph = EnhancedChoiceGraph
TaggedPOWL = Union[Activity, PartialOrder, ChoiceGraph, EnhancedOperatorPOWL]


__all__ = [
    "EnhancedPOWL",
    "EnhancedTransition",
    "EnhancedSilentTransition",
    "EnhancedFrequentTransition",
    "EnhancedStrictPartialOrder",
    "EnhancedSequence",
    "EnhancedOperatorPOWL",
    "EnhancedChoiceGraph",
    # Type aliases for API compatibility
    "Activity",
    "PartialOrder",
    "ChoiceGraph",
    "TaggedPOWL",
]
