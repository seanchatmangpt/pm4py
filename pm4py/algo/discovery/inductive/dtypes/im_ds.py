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
from typing import TypeVar, Generic, Optional

from pm4py.algo.discovery.inductive.dtypes.im_dfg import InductiveDFG
from pm4py.objects.dfg.obj import DFG
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL

T = TypeVar("T")


class IMDataStructure(ABC, Generic[T]):
    """
    The IMDataStructure is a helper class that unifies all possible data structures (typically logs or dfgs) that can
    be used for the classical Inductive Miner. The generic TypeVar 'T' is supposed to be the underlying data object
    used, and, should always be able to construct a DFG object. For example, T can be a dataframe, some other
    object representing an event log or a DFG itself.
    """

    def __init__(self, obj: T):
        self._obj = obj

    @property
    def dfg(self) -> DFG:
        pass

    @property
    def data_structure(self) -> T:
        return self._obj


class IMDataStructureLog(IMDataStructure[T], ABC, Generic[T]):
    """
    Generic class intended to represent that any subclass carries information that is captured in an event log.
    """


class IMDataStructureUVCL(IMDataStructureLog[UVCL]):
    """
    Log-Based data structure class that represents the event log as a 'Univariate Variant Compressed Log (UVCL)'
    """

    def __init__(self, obj: UVCL, dfg: Optional[DFG] = None):
        super().__init__(obj)
        if dfg is None:
            self._dfg = comut.discover_dfg_uvcl(self._obj)
        else:
            self._dfg = dfg

    @property
    def dfg(self) -> DFG:
        return self._dfg


class IMDataStructureDFG(IMDataStructure[InductiveDFG]):
    """
    DFG-Based data structure class
    """

    @property
    def dfg(self) -> DFG:
        return self._obj.dfg
