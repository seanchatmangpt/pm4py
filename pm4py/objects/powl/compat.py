"""
API-compatible compatibility layer for POWL.

This module provides adapter classes that expose the official POWL package API
while using PM4Py's enhanced POWL implementation under the hood.

This allows ostar to use PM4Py's POWL without changing import statements or API calls.
All code is independently implemented to maintain Apache 2.0 license compatibility.
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Union

# Import PM4Py's enhanced POWL implementation
from .enhanced import (
    EnhancedTransition as _EnhancedTransition,
    EnhancedSilentTransition as _EnhancedSilentTransition,
    EnhancedFrequentTransition as _EnhancedFrequentTransition,
    EnhancedStrictPartialOrder as _EnhancedStrictPartialOrder,
    EnhancedSequence as _EnhancedSequence,
    EnhancedOperatorPOWL as _EnhancedOperatorPOWL,
    EnhancedChoiceGraph as _EnhancedChoiceGraph,
)

from .types import ModelType


class Activity:
    """
    API-compatible Activity class.

    Wraps PM4Py's EnhancedTransition to match official POWL package API.
    """

    def __init__(
        self,
        label: Optional[str] = None,
        min_freq: int = 1,
        max_freq: Optional[int] = None
    ):
        """
        Create an activity.

        Args:
            label: Activity label (None for silent activities)
            min_freq: Minimum frequency (default: 1)
            max_freq: Maximum frequency (None for unbounded, defaults to min_freq)
        """
        self._inner = _EnhancedTransition(label, min_freq, max_freq)

    @property
    def label(self) -> Optional[str]:
        """Get activity label."""
        return self._inner.label

    def is_silent(self) -> bool:
        """Check if this is a silent activity."""
        return self._inner.is_silent()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return self._inner.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Activity":
        """Deserialize from dictionary."""
        inner = _EnhancedTransition.from_dict(data)
        result = cls(inner.label)
        result._inner = inner
        return result

    def __repr__(self) -> str:
        return f"Activity({self.label})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Activity):
            return self._inner.equal_content(other._inner)
        return False

    def __hash__(self) -> int:
        return hash(self._inner)


class PartialOrder:
    """
    API-compatible PartialOrder class.

    Wraps PM4Py's EnhancedStrictPartialOrder to match official POWL package API.
    """

    def __init__(
        self,
        nodes: Optional[List[Any]] = None,
        edges: Optional[List[Tuple[Any, Any]]] = None,
        min_freq: int = 1,
        max_freq: Optional[int] = None
    ):
        """
        Create a partial order.

        Args:
            nodes: List of POWL nodes
            edges: List of (source, target) tuples
            min_freq: Minimum frequency (default: 1)
            max_freq: Maximum frequency (None for unbounded)
        """
        nodes = nodes or []
        self._inner = _EnhancedStrictPartialOrder(nodes, min_freq, max_freq)

        # Add edges if provided
        if edges:
            for source, target in edges:
                self.add_edge(source, target)

    def get_nodes(self) -> List[Any]:
        """Get all nodes in the partial order."""
        return self._inner.get_nodes()

    def get_edges(self) -> List[Tuple[Any, Any]]:
        """Get all edges in the partial order."""
        return self._inner.get_edges()

    def add_node(self, node: Any) -> None:
        """Add a node to the partial order."""
        self._inner.order.add_node(node)

    def add_edge(self, source: Any, target: Any) -> None:
        """Add an edge between two nodes."""
        self._inner.add_edge(source, target)

    def successors(self, node: Any) -> List[Any]:
        """Get immediate successors of a node."""
        return self._inner.successors(node)

    def predecessors(self, node: Any) -> List[Any]:
        """Get immediate predecessors of a node."""
        return self._inner.predecessors(node)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return self._inner.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PartialOrder":
        """Deserialize from dictionary."""
        inner = _EnhancedStrictPartialOrder.from_dict(data)
        result = cls(list(inner.get_nodes()), list(inner.get_edges()))
        result._inner = inner
        return result

    def __repr__(self) -> str:
        return f"PartialOrder({len(self.get_nodes())} nodes, {len(self.get_edges())} edges)"


class ChoiceGraph:
    """
    API-compatible ChoiceGraph class.

    Wraps PM4Py's EnhancedChoiceGraph to match official POWL package API.
    """

    def __init__(
        self,
        nodes: Optional[List[Any]] = None,
        start_nodes: Optional[List[Any]] = None,
        end_nodes: Optional[List[Any]] = None,
        min_freq: int = 1,
        max_freq: Optional[int] = None
    ):
        """
        Create a choice graph.

        Args:
            nodes: List of POWL nodes
            start_nodes: List of entry nodes
            end_nodes: List of exit nodes
            min_freq: Minimum frequency (default: 1)
            max_freq: Maximum frequency (None for unbounded)
        """
        nodes = nodes or []
        self._inner = _EnhancedChoiceGraph(nodes, min_freq, max_freq)

        # Mark start/end nodes
        if start_nodes:
            for node in start_nodes:
                self.mark_start(node)
        if end_nodes:
            for node in end_nodes:
                self.mark_end(node)

    def get_nodes(self) -> List[Any]:
        """Get all nodes in the choice graph."""
        return self._inner.get_nodes()

    def add_node(self, node: Any) -> None:
        """Add a node to the choice graph."""
        self._inner.add_node(node)

    def add_edge(self, source: Any, target: Any) -> None:
        """Add an edge between two nodes."""
        self._inner.add_edge(source, target)

    def mark_start(self, node: Any) -> None:
        """Mark a node as a start node."""
        self._inner.mark_start(node)

    def mark_end(self, node: Any) -> None:
        """Mark a node as an end node."""
        self._inner.mark_end(node)

    def start_nodes(self) -> List[Any]:
        """Get start nodes."""
        return self._inner.start_nodes()

    def end_nodes(self) -> List[Any]:
        """Get end nodes."""
        return self._inner.end_nodes()

    def successors(self, node: Any) -> List[Any]:
        """Get immediate successors of a node."""
        return self._inner.successors(node)

    def predecessors(self, node: Any) -> List[Any]:
        """Get immediate predecessors of a node."""
        return self._inner.predecessors(node)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return self._inner.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChoiceGraph":
        """Deserialize from dictionary."""
        inner = _EnhancedChoiceGraph.from_dict(data)
        nodes = list(inner.get_nodes())
        result = cls(nodes, list(inner.start_nodes()), list(inner.end_nodes()))
        result._inner = inner
        return result

    def __repr__(self) -> str:
        return f"ChoiceGraph({len(self.get_nodes())} nodes)"


# Union type for type hints
TaggedPOWL = Union[Activity, PartialOrder, ChoiceGraph]


__all__ = [
    "Activity",
    "PartialOrder",
    "ChoiceGraph",
    "TaggedPOWL",
    "ModelType",
]
