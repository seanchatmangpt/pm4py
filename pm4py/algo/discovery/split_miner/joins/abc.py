"""Abstract base class for the joins-discovery phase."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pm4py.algo.discovery.split_miner.dtypes.working_graph import WorkingGraph


class JoinsDiscoverer(ABC):
    """Insert join gateways for every node with multiple incoming edges."""

    @classmethod
    @abstractmethod
    def apply(
        cls,
        wg: WorkingGraph,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Mutate ``wg`` in-place by inserting the discovered joins."""
