"""Abstract base class for the OR-join minimisation phase."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pm4py.algo.discovery.split_miner.dtypes.working_graph import WorkingGraph


class OrJoinMinimizer(ABC):
    """Replace trivial OR-joins by their XOR or AND equivalent."""

    @classmethod
    @abstractmethod
    def apply(
        cls,
        wg: WorkingGraph,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Mutate ``wg`` in-place."""
