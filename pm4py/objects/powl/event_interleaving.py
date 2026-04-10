'''
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions UG (haftungsbeschränkt)

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
Event Interleaving for Object-Centric Event Logs (OCEL).

Mines interleaving patterns from OCEL data following van der Aalst's
object-centric process mining approach:
1. Extract event logs per object type
2. Discover interleavings between object types
3. Build Object-Centric Process Model (OCPM)

Reference:
- van der Aalst, "Object-Centric Process Mining" (2022)
- van der Aalst et al., "OCEL: A Standardized Format for Event Logs"
"""

from typing import Dict, List, Set, Optional, Any, Tuple
from collections import defaultdict

from pm4py.objects.powl.obj import (
    POWL, Transition, StrictPartialOrder, DecisionGraph, SilentTransition,
)
from pm4py.objects.powl.BinaryRelation import BinaryRelation


class EventInterleavingMiner:
    """
    Mine event interleaving patterns from Object-Centric Event Logs.

    Van der Aalst's approach (OCEL paper):
    1. Extract event logs per object type
    2. Discover interleavings between object types
    3. Build Object-Centric Process Model (OCPM)
    """

    def __init__(self, ocel=None):
        self.ocel = ocel

    def mine_interleavings_from_log(
        self,
        event_log=None,
        object_type_column: Optional[str] = None,
    ) -> Dict[str, List[str]]:
        """
        Discover which events from different object types interleave.

        Args:
            event_log: Standard PM4Py event log
            object_type_column: Column name for object type classification

        Returns:
            Dict mapping event_name -> list of interleaved event_names
        """
        if event_log is None:
            return {}

        interleavings: Dict[str, List[str]] = defaultdict(list)

        # Group events by trace
        for trace in event_log:
            events = [e["concept:name"] for e in trace]
            seen = set()

            for i, event in enumerate(events):
                for j, other in enumerate(events):
                    if i != j and other not in seen:
                        # Events in same trace that aren't causally ordered
                        interleavings[event].append(other)
                seen.add(event)

        # Deduplicate
        return {
            k: list(set(v)) for k, v in interleavings.items()
        }

    def mine_causal_relations(
        self,
        event_log=None,
    ) -> Set[Tuple[str, str]]:
        """
        Discover causal ordering relations from event log.

        Returns set of (before, after) tuples indicating causal ordering.
        """
        if event_log is None:
            return set()

        relations: Set[Tuple[str, str]] = set()

        for trace in event_log:
            events = [e["concept:name"] for e in trace]
            for i in range(len(events) - 1):
                relations.add((events[i], events[i + 1]))

        return relations

    def to_powl(
        self,
        event_log=None,
        use_decision_graph: bool = False,
    ) -> Optional[POWL]:
        """
        Convert interleavings to POWL model.

        Strategy:
        1. Discover causal relations between events
        2. Create StrictPartialOrder for concurrent events
        3. Use DecisionGraph for complex interleavings

        Args:
            event_log: Standard PM4Py event log
            use_decision_graph: If True, use DecisionGraph; otherwise StrictPartialOrder

        Returns:
            POWL model representing the interleaving structure
        """
        if event_log is None:
            return None

        # Get all unique activities
        activities: Set[str] = set()
        for trace in event_log:
            for e in trace:
                activities.add(e["concept:name"])

        if not activities:
            return None

        # Get causal relations
        causal = self.mine_causal_relations(event_log)

        if use_decision_graph:
            return self._build_decision_graph(activities, causal)
        else:
            return self._build_partial_order(activities, causal)

    def _build_partial_order(
        self,
        activities: Set[str],
        causal: Set[Tuple[str, str]],
    ) -> StrictPartialOrder:
        """Build a StrictPartialOrder from activities and causal relations."""
        nodes = [Transition(act) for act in sorted(activities)]
        po = StrictPartialOrder(nodes)

        # Add causal edges
        node_map = {n.label: n for n in nodes if n.label}
        for before, after in causal:
            if before in node_map and after in node_map:
                po.add_edge(node_map[before], node_map[after])

        return po

    def _build_decision_graph(
        self,
        activities: Set[str],
        causal: Set[Tuple[str, str]],
    ) -> Optional[DecisionGraph]:
        """Build a DecisionGraph from activities and causal relations."""
        nodes = [Transition(act) for act in sorted(activities)]

        # Determine start and end nodes
        start_activities = {before for before, _ in causal} - {after for _, after in causal}
        end_activities = {after for _, after in causal} - {before for before, _ in causal}

        if not start_activities:
            start_activities = {sorted(activities)[0]}
        if not end_activities:
            end_activities = {sorted(activities)[-1]}

        node_map = {n.label: n for n in nodes if n.label}
        start_nodes = [node_map[a] for a in start_activities if a in node_map]
        end_nodes = [node_map[a] for a in end_activities if a in node_map]

        if not start_nodes or not end_nodes:
            return None

        order = BinaryRelation(nodes)
        for before, after in causal:
            if before in node_map and after in node_map:
                order.add_edge(node_map[before], node_map[after])

        return DecisionGraph(order, start_nodes, end_nodes)

    def get_interleaving_report(
        self,
        event_log=None,
    ) -> Dict[str, Any]:
        """Generate a detailed interleaving analysis report."""
        if event_log is None:
            return {"error": "No event log provided"}

        interleavings = self.mine_interleavings_from_log(event_log)
        causal = self.mine_causal_relations(event_log)

        return {
            "num_activities": len(interleavings),
            "num_causal_relations": len(causal),
            "activities": sorted(interleavings.keys()),
            "causal_relations": sorted(causal),
            "max_interleaving": max(
                len(v) for v in interleavings.values()
            ) if interleavings else 0,
        }


__all__ = [
    "EventInterleavingMiner",
]
