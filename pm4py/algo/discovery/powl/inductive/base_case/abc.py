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
from typing import Union, TypeVar, Generic, Optional, Dict, Any

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure
from pm4py.objects.powl.obj import POWL

T = TypeVar("T", bound=Union[IMDataStructure])


class BaseCase(ABC, Generic[T]):

    @classmethod
    def apply(
        cls, obj=T, parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[POWL]:
        return (
            cls.leaf(obj, parameters) if cls.holds(obj, parameters) else None
        )

    @classmethod
    @abstractmethod
    def holds(cls, obj=T, parameters: Optional[Dict[str, Any]] = None) -> bool:
        pass

    @classmethod
    @abstractmethod
    def leaf(cls, obj=T, parameters: Optional[Dict[str, Any]] = None) -> POWL:
        pass
