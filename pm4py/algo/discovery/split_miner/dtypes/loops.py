"""Output of the loop-discovery phase."""
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Set, Tuple


@dataclass
class LoopInfo:
    """Self-loops, short-loops, and the underlying frequency map."""

    self_loops: Set[str] = field(default_factory=set)
    short_loops: Set[FrozenSet[str]] = field(default_factory=set)
    short_loop_freq: Dict[Tuple[str, str], int] = field(default_factory=dict)
