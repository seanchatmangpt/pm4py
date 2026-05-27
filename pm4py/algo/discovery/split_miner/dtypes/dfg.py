"""Directly-follows graph type alias used across Split Miner phases."""
from typing import Dict, Tuple

#: ``DFG[(a, b)] = number of times b directly follows a``.
DFG = Dict[Tuple[str, str], int]
