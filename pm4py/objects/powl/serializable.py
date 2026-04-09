"""
Dict serialization for POWL objects.

Provides mixin classes for to_dict() and from_dict() methods.
This is part of making PM4Py self-contained for POWL functionality.
"""

from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Union
from abc import ABC, abstractmethod

from .types import ModelType
from .obj import POWL, Transition, SilentTransition, StrictPartialOrder, OperatorPOWL
from pm4py.objects.process_tree.obj import Operator


T = TypeVar('T', bound='SerializablePOWL')


class SerializablePOWL(ABC):
    """
    Mixin providing dict serialization for POWL objects.

    Adds to_dict() and from_dict() methods for JSON-serializable
    representation of POWL models.
    """

    @abstractmethod
    def model_type(self) -> ModelType:
        """
        Get the model type for serialization dispatch.

        Returns:
            ModelType enum value identifying the concrete type
        """
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize this POWL object to a dictionary.

        Returns:
            Dictionary representation suitable for JSON serialization
        """
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Deserialize a POWL object from a dictionary.

        Args:
            data: Dictionary representation from to_dict()

        Returns:
            Deserialized POWL object
        """
        pass

    def _serialize_children(self, children: List[POWL]) -> List[Dict[str, Any]]:
        """
        Serialize child POWL objects to dictionaries.

        Args:
            children: List of child POWL objects

        Returns:
            List of serialized child dictionaries
        """
        result = []
        for child in children:
            if isinstance(child, SerializablePOWL):
                result.append(child.to_dict())
            else:
                # Fallback for non-serializable children
                result.append({"type": "unknown", "data": str(child)})
        return result

    def _deserialize_children(
        self,
        data: List[Dict[str, Any]],
        registry: Optional[Dict[str, Type]] = None
    ) -> List[POWL]:
        """
        Deserialize child POWL objects from dictionaries.

        Args:
            data: List of serialized child dictionaries
            registry: Optional type registry for custom types

        Returns:
            List of deserialized POWL objects
        """
        if registry is None:
            registry = {}

        result = []
        for child_data in data:
            model_type = child_data.get("type", "activity")

            # Dispatch based on model type
            if model_type == ModelType.ACTIVITY.value:
                result.append(Transition.from_dict(child_data))
            elif model_type == ModelType.PARTIAL_ORDER.value:
                result.append(StrictPartialOrder.from_dict(child_data))
            elif model_type == ModelType.OPERATOR.value or model_type == ModelType.LOOP.value:
                result.append(OperatorPOWL.from_dict(child_data))
            elif model_type in registry:
                result.append(registry[model_type].from_dict(child_data))
            else:
                raise ValueError(f"Unknown model type: {model_type}")

        return result

    def _serialize_frequency(self) -> Dict[str, Any]:
        """
        Serialize frequency information.

        Returns:
            Dictionary with min_freq and max_freq
        """
        result = {}
        if hasattr(self, 'min_freq'):
            result['min_freq'] = self.min_freq
        if hasattr(self, 'max_freq'):
            result['max_freq'] = self.max_freq
        return result

    def _deserialize_frequency(self, data: Dict[str, Any]) -> tuple:
        """
        Deserialize frequency information.

        Args:
            data: Dictionary containing frequency data

        Returns:
            Tuple of (min_freq, max_freq)
        """
        min_freq = data.get('min_freq', 1)
        max_freq = data.get('max_freq', min_freq)
        return (min_freq, max_freq)


def serialize_powl(powl: POWL) -> Dict[str, Any]:
    """
    Top-level serialization function for any POWL object.

    Args:
        powl: POWL object to serialize

    Returns:
        Dictionary representation
    """
    if isinstance(powl, SerializablePOWL):
        return powl.to_dict()
    else:
        raise TypeError(f"POWL object {type(powl)} is not serializable")


def deserialize_powl(data: Dict[str, Any]) -> POWL:
    """
    Top-level deserialization function for POWL objects.

    Args:
        data: Dictionary representation from to_dict()

    Returns:
        Deserialized POWL object
    """
    model_type = data.get("type")

    if model_type == ModelType.ACTIVITY.value:
        return Transition.from_dict(data)
    elif model_type == ModelType.PARTIAL_ORDER.value:
        return StrictPartialOrder.from_dict(data)
    elif model_type == ModelType.OPERATOR.value or model_type == ModelType.LOOP.value:
        return OperatorPOWL.from_dict(data)
    else:
        raise ValueError(f"Unknown model type: {model_type}")


__all__ = [
    "SerializablePOWL",
    "serialize_powl",
    "deserialize_powl",
]
