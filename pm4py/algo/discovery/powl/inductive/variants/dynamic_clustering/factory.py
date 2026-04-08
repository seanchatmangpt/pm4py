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


from typing import List, Optional, Dict, Any, Tuple

from pm4py.algo.discovery.powl.inductive.cuts.factory import T, CutFactory
from pm4py.algo.discovery.powl.inductive.cuts.loop import POWLLoopCutUVCL
from pm4py.algo.discovery.powl.inductive.cuts.xor import (
    POWLExclusiveChoiceCutUVCL,
)
from pm4py.algo.discovery.powl.inductive.variants.dynamic_clustering.dynamic_clustering_partial_order_cut import (
    DynamicClusteringPartialOrderCutUVCL, )
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure
from pm4py.objects.powl.obj import POWL
from pm4py.objects.dfg import util as dfu


class CutFactoryPOWLDynamicClustering(CutFactory):

    @classmethod
    def get_cuts(cls, obj, parameters=None):
        return [
            POWLExclusiveChoiceCutUVCL,
            POWLLoopCutUVCL,
            DynamicClusteringPartialOrderCutUVCL,
        ]

    @classmethod
    def find_cut(
        cls, obj: IMDataStructure, parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[Tuple[POWL, List[T]]]:
        alphabet = sorted(dfu.get_vertices(obj.dfg), key=lambda g: g.__str__())
        if len(alphabet) < 2:
            return None
        for c in CutFactoryPOWLDynamicClustering.get_cuts(obj):
            r = c.apply(obj, parameters)
            if r is not None:
                return r
        return None
