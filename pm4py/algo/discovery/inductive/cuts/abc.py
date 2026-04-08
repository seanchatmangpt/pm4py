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
from typing import (
    Optional,
    List,
    Collection,
    Any,
    Tuple,
    Generic,
    TypeVar,
    Dict,
)

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure
from pm4py.objects.process_tree.obj import ProcessTree

T = TypeVar("T", bound=IMDataStructure)


class Cut(ABC, Generic[T]):

    @classmethod
    @abstractmethod
    def operator(
        cls, parameters: Optional[Dict[str, Any]] = None
    ) -> ProcessTree:
        pass

    @classmethod
    @abstractmethod
    def holds(
        cls, obj: T, parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[List[Collection[Any]]]:
        pass

    @classmethod
    def apply(
        cls, obj: T, parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[Tuple[ProcessTree, List[T]]]:
        g = cls.holds(obj, parameters)
        return (
            (cls.operator(), cls.project(obj, g, parameters))
            if g is not None
            else g
        )

    @classmethod
    @abstractmethod
    def project(
        cls,
        obj: T,
        groups: List[Collection[Any]],
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[T]:
        """
        Projection of the given data object (Generic type T).
        Returns a corresponding process tree and the projected sub logs according to the identified groups.
        A precondition of the project function is that it holds on the object for the given Object
        """
        pass
