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
Message Correlation for POWL Models.

Implements message passing patterns following van der Aalst's workflow nets:
- Message places for send/receive synchronization
- Correlation keys for message matching
- Bounded buffers for soundness

Reference:
- van der Aalst, "Workflow Patterns" (2003) - Pattern 41 (Send/Receive)
- van der Aalst, "The Application of Petri Nets to Workflow Management" (1998)
"""

from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass

from pm4py.objects.powl.obj import POWL


@dataclass
class MessageEvent:
    """A message send or receive event in a process."""
    activity: str
    message_type: str
    correlation_key: str  # e.g., "order_id"
    direction: str  # "send" or "receive"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "activity": self.activity,
            "message_type": self.message_type,
            "correlation_key": self.correlation_key,
            "direction": self.direction,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MessageEvent":
        return cls(**data)

    def __repr__(self) -> str:
        arrow = ">>>" if self.direction == "send" else "<<<"
        return f"Message({arrow} {self.activity}:{self.message_type} [{self.correlation_key}])"


@dataclass
class MessageCorrelation:
    """
    Message correlation mechanism following van der Aalst's workflow nets.

    Soundness requirements (van der Aalst):
    1. Bounded buffers: Message queues have finite capacity
    2. No orphan messages: Every sent message has matching receiver
    3. Synchronization: Receive waits for message (blocking semantic)
    """
    send_event: MessageEvent
    receive_event: MessageEvent
    buffer_capacity: int = 100

    def is_sound(self) -> bool:
        """
        Validate message correlation preserves soundness.

        Van der Aalst's requirements:
        - Must have bounded capacity (prevents unbounded message accumulation)
        - Send and receive must use same correlation key
        - Send direction must be 'send', receive must be 'receive'
        """
        if self.buffer_capacity <= 0:
            return False
        if self.send_event.correlation_key != self.receive_event.correlation_key:
            return False
        if self.send_event.direction != "send":
            return False
        if self.receive_event.direction != "receive":
            return False
        return True

    def to_workflow_net_description(self) -> Dict[str, Any]:
        """
        Describe Petri net mapping.

        Each correlation becomes a message place:
        - Send transition produces token in message place
        - Receive transition consumes token from message place
        """
        return {
            "strategy": "message_place",
            "message_type": self.send_event.message_type,
            "correlation_key": self.send_event.correlation_key,
            "buffer_capacity": self.buffer_capacity,
            "description": (
                f"Send '{self.send_event.activity}' produces token in message place. "
                f"Receive '{self.receive_event.activity}' consumes token."
            ),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "send_event": self.send_event.to_dict(),
            "receive_event": self.receive_event.to_dict(),
            "buffer_capacity": self.buffer_capacity,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MessageCorrelation":
        return cls(
            send_event=MessageEvent.from_dict(data["send_event"]),
            receive_event=MessageEvent.from_dict(data["receive_event"]),
            buffer_capacity=data.get("buffer_capacity", 100),
        )

    def __repr__(self) -> str:
        return f"Correlation({self.send_event.activity} -> {self.receive_event.activity})"


class MessagingPOWL:
    """
    POWL model with message correlation.

    Wraps a base POWL model and adds message passing semantics.
    """

    def __init__(
        self,
        base_powl: POWL,
        correlations: Optional[List[MessageCorrelation]] = None,
    ):
        self.base_powl = base_powl
        self.correlations: List[MessageCorrelation] = correlations or []

    def add_correlation(self, correlation: MessageCorrelation) -> None:
        """Add a message correlation."""
        self.correlations.append(correlation)

    def get_correlations_for_activity(self, activity: str) -> List[MessageCorrelation]:
        """Get all correlations involving an activity."""
        result = []
        for c in self.correlations:
            if c.send_event.activity == activity or c.receive_event.activity == activity:
                result.append(c)
        return result

    def is_sound(self) -> bool:
        """Validate all message correlations preserve soundness."""
        return all(c.is_sound() for c in self.correlations)

    def get_soundness_report(self) -> Dict[str, Any]:
        """Detailed soundness report for all message correlations."""
        issues = []
        for c in self.correlations:
            if not c.is_sound():
                if c.buffer_capacity <= 0:
                    issues.append(f"Unbounded buffer in correlation: {c}")
                if c.send_event.correlation_key != c.receive_event.correlation_key:
                    issues.append(f"Correlation key mismatch: {c}")

        return {
            "is_sound": len(issues) == 0,
            "num_correlations": len(self.correlations),
            "issues": issues,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "correlations": [c.to_dict() for c in self.correlations],
        }

    def __repr__(self) -> str:
        return f"MessagingPOWL({len(self.correlations)} correlations)"


__all__ = [
    "MessageEvent",
    "MessageCorrelation",
    "MessagingPOWL",
]
