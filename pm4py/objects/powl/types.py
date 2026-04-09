"""
Type definitions for POWL objects.

Provides ModelType enum and base types for POWL serialization.
This is part of making PM4Py self-contained for POWL functionality.
"""

from enum import Enum


class ModelType(Enum):
    """
    Model type enumeration for POWL serialization dispatch.

    Identifies the concrete type of POWL nodes for serialization/deserialization.
    Compatible with official POWL package's ModelType but independently implemented.
    """
    ACTIVITY = "activity"
    PARTIAL_ORDER = "partial_order"
    CHOICE_GRAPH = "choice_graph"
    LOOP = "loop"
    OPERATOR = "operator"

    def __str__(self) -> str:
        """Return string value."""
        return self.value

    @classmethod
    def from_string(cls, value: str) -> "ModelType":
        """
        Create ModelType from string value.

        Args:
            value: String representation of model type

        Returns:
            Corresponding ModelType enum value

        Raises:
            ValueError: If value is not a valid model type
        """
        try:
            return cls(value)
        except ValueError:
            valid_values = [t.value for t in cls]
            raise ValueError(
                f"Invalid model type '{value}'. Must be one of: {valid_values}"
            )


__all__ = [
    "ModelType",
]
