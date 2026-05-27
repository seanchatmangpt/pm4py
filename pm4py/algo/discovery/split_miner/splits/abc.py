"""Abstract base class for the splits-discovery phase."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pm4py.algo.discovery.split_miner.dtypes.working_graph import WorkingGraph


class SplitsDiscoverer(ABC):
    """Insert split gateways for every task with multiple successors."""

    @classmethod
    @abstractmethod
    def apply(
        cls,
        wg: WorkingGraph,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Mutate ``wg`` in-place with the discovered split hierarchy."""
