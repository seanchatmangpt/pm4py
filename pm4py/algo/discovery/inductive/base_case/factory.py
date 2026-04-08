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


from typing import List, TypeVar, Optional, Dict, Any

from pm4py.algo.discovery.inductive.base_case.abc import BaseCase
from pm4py.algo.discovery.inductive.base_case.empty_log import (
    EmptyLogBaseCaseUVCL,
    EmptyLogBaseCaseDFG,
)
from pm4py.algo.discovery.inductive.base_case.single_activity import (
    SingleActivityBaseCaseUVCL,
    SingleActivityBaseCaseDFG,
)
from pm4py.algo.discovery.inductive.dtypes.im_ds import (
    IMDataStructure,
    IMDataStructureUVCL,
    IMDataStructureDFG,
)
from pm4py.algo.discovery.inductive.variants.instances import IMInstance
from pm4py.objects.process_tree.obj import ProcessTree

T = TypeVar("T", bound=IMDataStructure)
S = TypeVar("S", bound=BaseCase)


class BaseCaseFactory:

    @classmethod
    def get_base_cases(
        cls,
        obj: T,
        inst: IMInstance,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[S]:
        if inst is IMInstance.IM or inst is IMInstance.IMf:
            if type(obj) is IMDataStructureUVCL:
                return [EmptyLogBaseCaseUVCL, SingleActivityBaseCaseUVCL]
        if inst is IMInstance.IMd:
            if type(obj) is IMDataStructureDFG:
                return [EmptyLogBaseCaseDFG, SingleActivityBaseCaseDFG]
        return []

    @classmethod
    def apply_base_cases(
        cls,
        obj: T,
        inst: IMInstance,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Optional[ProcessTree]:
        for b in BaseCaseFactory.get_base_cases(obj, inst):
            r = b.apply(obj, parameters)
            if r is not None:
                return r
        return None
