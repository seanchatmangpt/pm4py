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
"""Improper-completion heuristic.

For every AND-split that has a loop-edge among its outgoing edges (i.e.
a back-edge of the working graph) we insert a preceding XOR-split and
move the loop-edge so it now originates from the new XOR-split. This
prevents the AND-split's parallel branches from being re-entered before
the previous iteration has completed.
"""
from typing import Any, Dict, List, Optional

from pm4py.algo.discovery.split_miner.sese.rpst import analyse
from pm4py.algo.discovery.split_miner.dtypes.log import RefinedTrace
from pm4py.algo.discovery.split_miner.dtypes.working_graph import WorkingGraph
from pm4py.algo.discovery.split_miner.heuristics.abc import Heuristic


class ImproperCompletionHeuristic(Heuristic):
    """Re-route AND-split loop-edges through a new preceding XOR-split."""

    @classmethod
    def apply(
        cls,
        wg: WorkingGraph,
        refined_traces: Optional[List[RefinedTrace]] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> None:
        info = analyse(wg)
        for and_id in [
            nid for nid, n in list(wg.nodes.items()) if n.kind == "and"
        ]:
            if and_id not in wg.nodes or len(wg.successors(and_id)) <= 1:
                continue
            loop_targets = [
                t
                for t in wg.successors(and_id)
                if (and_id, t) in info.back_edges
            ]
            if not loop_targets:
                continue
            preds = wg.predecessors(and_id)
            if len(preds) != 1:
                continue
            parent = preds[0]
            xor_id = wg.add_node("xor", label="xor_lc")

            wg.remove_edge(parent, and_id)
            wg.add_edge(parent, xor_id)
            wg.add_edge(xor_id, and_id)
            for tgt in loop_targets:
                wg.remove_edge(and_id, tgt)
                wg.add_edge(xor_id, tgt)
