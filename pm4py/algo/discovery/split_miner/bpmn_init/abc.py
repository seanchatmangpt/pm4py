"""Abstract base class for the BPMN-initialisation phase."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pm4py.algo.discovery.split_miner.dtypes.concurrency import (
    ConcurrencyResult,
)
from pm4py.algo.discovery.split_miner.dtypes.filtering import FilterResult
from pm4py.algo.discovery.split_miner.dtypes.loops import LoopInfo
from pm4py.algo.discovery.split_miner.dtypes.working_graph import WorkingGraph


class BPMNInitializer(ABC):
    """Materialise a :class:`WorkingGraph` from the filtered PDFG."""

    @classmethod
    @abstractmethod
    def apply(
        cls,
        filtered: FilterResult,
        concurrency: ConcurrencyResult,
        loops: LoopInfo,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> WorkingGraph:
        """Return a fresh working graph ready for the splits phase."""
