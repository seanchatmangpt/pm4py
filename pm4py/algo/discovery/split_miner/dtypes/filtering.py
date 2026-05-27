"""Output of the PDFG filtering phase."""
from dataclasses import dataclass, field
from typing import Set, Tuple


@dataclass
class FilterResult:
    edges: Set[Tuple[str, str]] = field(default_factory=set)
    source: str = ""
    sink: str = ""
