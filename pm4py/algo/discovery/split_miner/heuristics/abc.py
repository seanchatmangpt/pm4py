"""Abstract base class for working-graph heuristics."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pm4py.algo.discovery.split_miner.dtypes.log import RefinedTrace
from pm4py.algo.discovery.split_miner.dtypes.working_graph import WorkingGraph


class Heuristic(ABC):
    """A post-processing pass that mutates the working graph in-place.

    Heuristics may inspect the refined log (lifecycle-aware trace list)
    to decide what to change.
    """

    @classmethod
    @abstractmethod
    def apply(
        cls,
        wg: WorkingGraph,
        refined_traces: Optional[List[RefinedTrace]] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> None:
        ...
