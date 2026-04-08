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



from abc import ABC
from typing import Any, Optional, Dict, Generic, Tuple, List

from pm4py.algo.discovery.inductive.cuts.concurrency import (
    ConcurrencyCut,
    ConcurrencyCutUVCL,
    T,
)
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.objects.powl.obj import StrictPartialOrder


class POWLConcurrencyCut(ConcurrencyCut, ABC, Generic[T]):

    @classmethod
    def operator(
        cls, parameters: Optional[Dict[str, Any]] = None
    ) -> StrictPartialOrder:
        raise Exception("This function should not be called!")

    @classmethod
    def apply(
        cls, obj: T, parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[Tuple[StrictPartialOrder, List[T]]]:
        g = cls.holds(obj, parameters)
        if g is None:
            return g
        else:
            children = cls.project(obj, g, parameters)
            return StrictPartialOrder(children), children


class POWLConcurrencyCutUVCL(
    ConcurrencyCutUVCL, POWLConcurrencyCut[IMDataStructureUVCL]
):
    pass
