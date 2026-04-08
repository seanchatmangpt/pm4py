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



from collections import Counter
from multiprocessing import Pool, Manager
from typing import Tuple, List, Optional, Dict, Any

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.algo.discovery.inductive.fall_through.empty_traces import (
    EmptyTracesUVCL,
)
from pm4py.objects.powl.obj import OperatorPOWL
from pm4py.objects.process_tree.obj import Operator
from copy import copy


class POWLEmptyTracesUVCL(EmptyTracesUVCL):

    @classmethod
    def apply(
        cls,
        obj: IMDataStructureUVCL,
        pool: Pool = None,
        manager: Manager = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Optional[Tuple[OperatorPOWL, List[IMDataStructureUVCL]]]:
        if cls.holds(obj, parameters):
            data_structure = copy(obj.data_structure)
            del data_structure[()]
            children = [
                IMDataStructureUVCL(Counter()),
                IMDataStructureUVCL(data_structure),
            ]
            return OperatorPOWL(Operator.XOR, children), children
        else:
            return None
