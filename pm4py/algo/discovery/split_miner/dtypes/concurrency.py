"""Output of the concurrency phase: pruned DFG + concurrency relation."""
from dataclasses import dataclass, field
from typing import FrozenSet, Set

from pm4py.algo.discovery.split_miner.dtypes.dfg import DFG


@dataclass
class ConcurrencyResult:
    pdfg: DFG = field(default_factory=dict)
    concurrent_pairs: Set[FrozenSet[str]] = field(default_factory=set)
