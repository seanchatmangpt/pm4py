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



from pm4py.algo.discovery.powl.inductive.base_case.abc import BaseCase
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from typing import Optional, Dict, Any

from pm4py.objects.powl.obj import Transition


class SingleActivityBaseCaseUVCL(BaseCase[IMDataStructureUVCL]):
    @classmethod
    def holds(
        cls,
        obj=IMDataStructureUVCL,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> bool:
        if len(obj.data_structure.keys()) != 1:
            return False
        if len(list(obj.data_structure.keys())[0]) > 1:
            return False
        return True

    @classmethod
    def leaf(
        cls,
        obj=IMDataStructureUVCL,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Transition:
        for t in obj.data_structure:
            return Transition(label=t[0])
