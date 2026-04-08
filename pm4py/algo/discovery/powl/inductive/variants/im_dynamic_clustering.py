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


from typing import Optional, Tuple, List, TypeVar, Dict, Any

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureLog
from pm4py.algo.discovery.powl.inductive.variants.dynamic_clustering.factory import (
    CutFactoryPOWLDynamicClustering, )
from pm4py.algo.discovery.powl.inductive.variants.im_tree import IMBasePOWL
from pm4py.algo.discovery.powl.inductive.variants.powl_discovery_varaints import (
    POWLDiscoveryVariant, )
from pm4py.objects.powl.obj import POWL

T = TypeVar("T", bound=IMDataStructureLog)


class POWLInductiveMinerDynamicClustering(IMBasePOWL):

    def instance(self) -> POWLDiscoveryVariant:
        return POWLDiscoveryVariant.DYNAMIC_CLUSTERING

    def find_cut(
        self, obj: T, parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[Tuple[POWL, List[T]]]:
        res = CutFactoryPOWLDynamicClustering.find_cut(
            obj, parameters=parameters
        )
        return res
