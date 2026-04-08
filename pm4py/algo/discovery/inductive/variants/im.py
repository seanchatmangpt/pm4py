"""
PM4Py – A Process Mining Library for Python
Copyright (C) 2024 Process Intelligence Solutions

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
"""


from typing import TypeVar, Generic, Dict, Any, Optional

from pm4py.algo.discovery.inductive.dtypes.im_ds import (
    IMDataStructureUVCL,
    IMDataStructureLog,
)
from pm4py.algo.discovery.inductive.fall_through.empty_traces import (
    EmptyTracesUVCL,
)
from pm4py.algo.discovery.inductive.variants.abc import InductiveMinerFramework
from pm4py.algo.discovery.inductive.variants.instances import IMInstance
from pm4py.objects.process_tree.obj import ProcessTree

T = TypeVar("T", bound=IMDataStructureLog)


class IM(Generic[T], InductiveMinerFramework[T]):

    def instance(self) -> IMInstance:
        return IMInstance.IM


class IMUVCL(IM[IMDataStructureUVCL]):
    def apply(
        self,
        obj: IMDataStructureUVCL,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> ProcessTree:
        empty_traces = EmptyTracesUVCL.apply(obj, parameters)
        if empty_traces is not None:
            return self._recurse(empty_traces[0], empty_traces[1], parameters)
        return super().apply(obj, parameters)
