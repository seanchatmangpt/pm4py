from typing import Optional, Dict, Any
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureDFG
from pm4py.algo.discovery.inductive.variants.abc import InductiveMinerFramework
from pm4py.algo.discovery.inductive.variants.instances import IMInstance
from pm4py.algo.discovery.inductive.fall_through.empty_traces import EmptyTracesDFG
from pm4py.objects.process_tree.obj import ProcessTree

class IMD(InductiveMinerFramework[IMDataStructureDFG]):

    def instance(self) -> IMInstance:
        return IMInstance.IMd


    def apply(
        self,
        obj: IMDataStructureDFG,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> ProcessTree:
        # Handle empty traces FIRST (so τ is not lost if a base case/cut triggers)
        empty_traces = EmptyTracesDFG.apply(obj, parameters=parameters)
        if empty_traces is not None:
            return self._recurse(empty_traces[0], empty_traces[1], parameters)
        return super().apply(obj, parameters)
