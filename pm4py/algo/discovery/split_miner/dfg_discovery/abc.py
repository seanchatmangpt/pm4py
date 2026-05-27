"""Abstract base class for the DFG-discovery phase."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar

from pm4py.algo.discovery.split_miner.dtypes.dfg import DFG
from pm4py.algo.discovery.split_miner.dtypes.loops import LoopInfo


TraceT = TypeVar("TraceT")


class DFGDiscoverer(ABC, Generic[TraceT]):
    """Build a DFG and the corresponding ``LoopInfo`` from a list of traces."""

    @classmethod
    @abstractmethod
    def apply(
        cls,
        traces: List[TraceT],
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Tuple[DFG, LoopInfo]:
        """Return the directly-follows graph and its self/short-loop summary."""
