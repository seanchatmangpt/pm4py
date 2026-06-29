"""OR-join minimisation.

Replace every inclusive (OR) join with the behaviourally equivalent
exclusive (XOR) or parallel (AND) join, following the reference Split
Miner ``replaceIORs`` step. The heavy lifting lives in
:mod:`pm4py.algo.discovery.split_miner.dtypes.gateway_map`, which builds
a gateway map, walks each OR-join back to its dominator and decides
between XOR and AND (inserting token-generator gateways for the parallel
case so the join can always synchronise).
"""
from typing import Any, Dict, Optional

from pm4py.algo.discovery.split_miner.dtypes.working_graph import WorkingGraph
from pm4py.algo.discovery.split_miner.or_min.abc import OrJoinMinimizer
from pm4py.algo.discovery.split_miner.dtypes.gateway_map import (
    replace_inclusive_joins,
)


class ClassicOrJoinMinimizer(OrJoinMinimizer):
    """Replace every inclusive (OR) join with an XOR or AND join."""

    @classmethod
    def apply(
        cls,
        wg: WorkingGraph,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> None:
        replace_inclusive_joins(wg, apply_hagen=True)
