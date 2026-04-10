'''
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions UG (haftungsbeschränkt)

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

"""
Multi-Instance Activities for POWL Models.

Implements BPMN 2.0 multi-instance semantics following van der Aalst's
soundness requirements:
- Bounded: Must have finite upper bound
- Synchronizing: All instances must complete before proceeding
- Data-driven: Instance count determined by runtime data

Reference:
- van der Aalst, "Workflow Patterns" (2003) - Pattern 15 (Multiple Instance)
- BPMN 2.0 Specification - Multi-Instance Activity
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from pm4py.objects.powl.obj import POWL, Transition


class MultiInstanceType(Enum):
    """Type of multi-instance execution."""
    SEQUENTIAL = "sequential"  # Execute instances one after another
    PARALLEL = "parallel"  # Execute all instances concurrently


@dataclass
class MultiInstanceActivity:
    """
    Multi-instance activity following BPMN 2.0 semantics.

    Van der Aalst's soundness requirements:
    1. Bounded: Must have finite upper bound
    2. Synchronizing: All instances must complete before proceeding
    3. Data-driven: Instance count determined by runtime data
    """
    activity: str
    mi_type: MultiInstanceType
    min_instances: int = 1
    max_instances: Optional[int] = None
    collection_variable: Optional[str] = None
    completion_condition: Optional[str] = None

    def is_sound(self) -> bool:
        """
        Validate multi-instance preserves soundness.

        Van der Aalst's requirements:
        - Must have bounded upper bound (max_instances != None)
        - min_instances <= max_instances
        - Sequential MI always sound (if bounded)
        - Parallel MI requires synchronization barrier (implicit)
        """
        if self.max_instances is None:
            return False  # Unbounded MI is not sound per van der Aalst
        if self.min_instances > self.max_instances:
            return False
        if self.min_instances < 0:
            return False
        return True

    def to_petri_net_description(self) -> Dict[str, Any]:
        """
        Describe Petri net mapping strategy.

        Sequential MI: Expand to sequence of N transitions
        Parallel MI: Create parallel branches with sync barrier
        """
        if self.mi_type == MultiInstanceType.SEQUENTIAL:
            return {
                "strategy": "sequential_expansion",
                "description": f"Expand to sequence of {self.min_instances}-{self.max_instances} transitions",
                "places_needed": self.max_instances + 1,
                "transitions_needed": self.max_instances,
            }
        else:
            return {
                "strategy": "parallel_with_sync",
                "description": f"Create {self.min_instances}-{self.max_instances} parallel branches with sync barrier",
                "places_needed": self.max_instances * 2 + 2,
                "transitions_needed": self.max_instances + 2,  # split + instances + join
            }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "activity": self.activity,
            "mi_type": self.mi_type.value,
            "min_instances": self.min_instances,
            "max_instances": self.max_instances,
            "collection_variable": self.collection_variable,
            "completion_condition": self.completion_condition,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MultiInstanceActivity":
        """Deserialize from dictionary."""
        return cls(
            activity=data["activity"],
            mi_type=MultiInstanceType(data["mi_type"]),
            min_instances=data.get("min_instances", 1),
            max_instances=data.get("max_instances"),
            collection_variable=data.get("collection_variable"),
            completion_condition=data.get("completion_condition"),
        )

    def __repr__(self) -> str:
        bounds = f"{self.min_instances}..{self.max_instances or 'N'}"
        return f"MI({self.activity}, {self.mi_type.value}, [{bounds}])"


class MultiInstancePOWL:
    """
    POWL model with multi-instance activities.

    Wraps a base POWL model and adds multi-instance semantics to
    specific activities. Soundness validation checks all multi-instance
    constraints.
    """

    def __init__(
        self,
        base_powl: POWL,
        multi_instances: Optional[List[MultiInstanceActivity]] = None,
    ):
        self.base_powl = base_powl
        self.multi_instances: List[MultiInstanceActivity] = multi_instances or []

    def add_multi_instance(self, mi: MultiInstanceActivity) -> None:
        """Add a multi-instance activity."""
        self.multi_instances.append(mi)

    def get_multi_instance(self, activity: str) -> Optional[MultiInstanceActivity]:
        """Get multi-instance config for an activity."""
        for mi in self.multi_instances:
            if mi.activity == activity:
                return mi
        return None

    def is_sound(self) -> bool:
        """Validate all multi-instance activities preserve soundness."""
        return all(mi.is_sound() for mi in self.multi_instances)

    def get_soundness_report(self) -> Dict[str, Any]:
        """Detailed soundness report for all multi-instance activities."""
        issues = []
        for mi in self.multi_instances:
            if not mi.is_sound():
                if mi.max_instances is None:
                    issues.append(f"Unbounded multi-instance: {mi.activity}")
                if mi.min_instances > (mi.max_instances or 0):
                    issues.append(f"Invalid bounds for {mi.activity}: min > max")

        return {
            "is_sound": len(issues) == 0,
            "num_multi_instances": len(self.multi_instances),
            "issues": issues,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "multi_instances": [mi.to_dict() for mi in self.multi_instances],
        }

    def __repr__(self) -> str:
        return f"MultiInstancePOWL({len(self.multi_instances)} MI activities)"


__all__ = [
    "MultiInstanceType",
    "MultiInstanceActivity",
    "MultiInstancePOWL",
]
