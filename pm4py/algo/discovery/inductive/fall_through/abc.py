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


from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Tuple, List, Optional, Dict, Any

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure
from pm4py.objects.process_tree.obj import ProcessTree

T = TypeVar("T", bound=IMDataStructure)


class FallThrough(ABC, Generic[T]):

    @classmethod
    @abstractmethod
    def holds(cls, t: T, parameters: Optional[Dict[str, Any]] = None) -> bool:
        pass

    @classmethod
    @abstractmethod
    def apply(
        cls,
        t: T,
        pool=None,
        manager=None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Optional[Tuple[ProcessTree, List[T]]]:
        pass
