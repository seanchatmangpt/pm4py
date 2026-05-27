"""Abstract base class for the PDFG filtering phase."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pm4py.algo.discovery.split_miner.dtypes.dfg import DFG
from pm4py.algo.discovery.split_miner.dtypes.filtering import FilterResult


class Filterer(ABC):
    """Reduce a pruned DFG to a sound, low-complexity edge set."""

    @classmethod
    @abstractmethod
    def apply(
        cls,
        pdfg: DFG,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> FilterResult:
        """Return the source/sink and the kept edges."""
