"""Abstract base class for the BPMN-export phase."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pm4py.algo.discovery.split_miner.dtypes.working_graph import WorkingGraph
from pm4py.objects.bpmn.obj import BPMN


class BPMNExporter(ABC):
    """Convert the internal :class:`WorkingGraph` into a pm4py BPMN object."""

    @classmethod
    @abstractmethod
    def apply(
        cls,
        wg: WorkingGraph,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> BPMN:
        ...
