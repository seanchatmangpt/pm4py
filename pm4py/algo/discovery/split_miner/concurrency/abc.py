"""Abstract base class for the concurrency-discovery phase.

A :class:`ConcurrencyOracle` takes a DFG (and, optionally, the underlying
trace list) and returns both the set of unordered concurrent pairs and
the *pruned* DFG with the concurrent arcs removed.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar

from pm4py.algo.discovery.split_miner.dtypes.concurrency import (
    ConcurrencyResult,
)
from pm4py.algo.discovery.split_miner.dtypes.dfg import DFG
from pm4py.algo.discovery.split_miner.dtypes.loops import LoopInfo


TraceT = TypeVar("TraceT")


class ConcurrencyOracle(ABC):
    """Detect concurrent activity pairs and prune the DFG accordingly."""

    @classmethod
    @abstractmethod
    def apply(
        cls,
        dfg: DFG,
        traces: Optional[List[TraceT]],
        loops: LoopInfo,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> ConcurrencyResult:
        """Return the pruned DFG together with the concurrency relation."""
