'''
PM4Py - A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see this software project's root or
visit <https://www.gnu.org/licenses/>.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
'''



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
