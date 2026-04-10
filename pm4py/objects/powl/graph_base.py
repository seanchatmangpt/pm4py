"""
Graph traversal API for POWL objects.

Provides mixin classes for graph-like operations on POWL nodes.
This is part of making PM4Py self-contained for POWL functionality.
"""
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



from typing import Any, Dict, List, Set, Tuple
from abc import ABC, abstractmethod


class GraphTraversable:
    """
    Mixin providing graph traversal methods for POWL objects.

    Adds successors(), predecessors(), get_nodes(), and get_edges() methods
    for consistent graph-like API across POWL node types.
    """

    @abstractmethod
    def get_nodes(self) -> List[Any]:
        """
        Get all nodes in this graph structure.

        Returns:
            List of POWL nodes
        """
        pass

    @abstractmethod
    def get_edges(self) -> List[Tuple[Any, Any]]:
        """
        Get all edges in this graph structure.

        Returns:
            List of tuples (from_node, to_node)
        """
        pass

    def successors(self, node: Any) -> List[Any]:
        """
        Get immediate successors of a node.

        Args:
            node: The node to get successors for

        Returns:
            List of successor nodes
        """
        edges = self.get_edges()
        return [target for source, target in edges if source == node]

    def predecessors(self, node: Any) -> List[Any]:
        """
        Get immediate predecessors of a node.

        Args:
            node: The node to get predecessors for

        Returns:
            List of predecessor nodes
        """
        edges = self.get_edges()
        return [source for source, target in edges if target == node]

    def adjacent(self, node: Any) -> List[Any]:
        """
        Get all adjacent nodes (both successors and predecessors).

        Args:
            node: The node to get adjacent nodes for

        Returns:
            List of adjacent nodes (unique)
        """
        return list(set(self.successors(node) + self.predecessors(node)))


class StartEndNodes:
    """
    Mixin for managing start and end nodes in graph structures.

    Provides start_nodes() and end_nodes() methods for identifying
    entry and exit points in the graph.
    """

    @abstractmethod
    def start_nodes(self) -> List[Any]:
        """
        Get start nodes (nodes with no predecessors).

        Returns:
            List of start nodes
        """
        pass

    @abstractmethod
    def end_nodes(self) -> List[Any]:
        """
        Get end nodes (nodes with no successors).

        Returns:
            List of end nodes
        """
        pass

    def mark_start(self, node: Any) -> None:
        """
        Mark a node as a start node.

        Args:
            node: The node to mark as start
        """
        if not hasattr(self, '_start_nodes'):
            self._start_nodes = set()
        self._start_nodes.add(node)

    def mark_end(self, node: Any) -> None:
        """
        Mark a node as an end node.

        Args:
            node: The node to mark as end
        """
        if not hasattr(self, '_end_nodes'):
            self._end_nodes = set()
        self._end_nodes.add(node)

    def clear_start_markers(self) -> None:
        """Clear all start node markers."""
        if hasattr(self, '_start_nodes'):
            self._start_nodes.clear()

    def clear_end_markers(self) -> None:
        """Clear all end node markers."""
        if hasattr(self, '_end_nodes'):
            self._end_nodes.clear()


__all__ = [
    "GraphTraversable",
    "StartEndNodes",
]
