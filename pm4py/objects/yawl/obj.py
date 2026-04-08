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



'''
YAWL object model for pm4py.

This module defines the core data structures for representing YAWL specifications,
which can be exported to YAWL XML format and executed in YAWL engines.

Reference:
- van der Aalst, W.M.P., ter Hofstede, A.H.M. (2005). "YAWL: Yet Another Workflow Language."
- YAWL Foundation: https://www.yawlfoundation.org/
'''

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4


@dataclass
class YAWLMetadata:
    """YAWL specification metadata.

    Attributes:
    -----------
    title : str
        Title of the specification
    description : str, optional
        Description of the specification
    version : str, optional
        Version string (default: "1.0")
    author : str, optional
        Author/creator (default: "pm4py")
    created : str, optional
        ISO timestamp of creation (default: current time)
    """
    title: str
    description: str = ""
    version: str = "1.0"
    author: str = "pm4py"
    created: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class YAWLTask:
    """YAWL task (atomic or composite).

    Attributes:
    -----------
    id : str
        Unique task identifier
    name : str
        Human-readable task label
    join_type : str, optional
        Join type: "xor", "and", or "or" (default: "xor")
    split_type : str, optional
        Split type: "xor", "and", or "or" (default: "xor")
    decomposition_id : Optional[str], optional
        Reference to decomposition if composite task (default: None)
    """
    id: str
    name: str
    join_type: str = "xor"
    split_type: str = "xor"
    decomposition_id: Optional[str] = None


@dataclass
class YAWLFlow:
    """YAWL flow edge between nodes.

    Attributes:
    -----------
    source : str
        Source node ID (task or condition)
    target : str
        Target node ID (task or condition)
    """
    source: str
    target: str


@dataclass
class YAWLDecomposition:
    """YAWL decomposition (process net).

    A decomposition represents a process net with tasks, conditions, and flows.
    The root decomposition is the main process; composite tasks can reference
    other decompositions for subprocesses.

    Attributes:
    -----------
    id : str
        Unique decomposition identifier
    is_root_net : bool, optional
        Whether this is the root/main process net (default: False)
    input_condition : str, optional
        ID of input condition (default: "input")
    output_condition : str, optional
        ID of output condition (default: "output")
    tasks : List[YAWLTask], optional
        List of tasks in this decomposition (default: empty)
    flows : List[YAWLFlow], optional
        List of flows between nodes (default: empty)
    """
    id: str
    is_root_net: bool = False
    input_condition: str = "input"
    output_condition: str = "output"
    tasks: List[YAWLTask] = field(default_factory=list)
    flows: List[YAWLFlow] = field(default_factory=list)


@dataclass
class YAWLSpecification:
    """YAWL specification root element.

    A YAWL specification contains metadata and one or more decompositions.
    The root decomposition represents the main process flow.

    Attributes:
    -----------
    uri : str
        Unique URI for this specification
    metadata : YAWLMetadata
        Specification metadata (title, version, etc.)
    decompositions : List[YAWLDecomposition]
        List of decompositions (at least one: the root net)
    """
    uri: str
    metadata: YAWLMetadata
    decompositions: List[YAWLDecomposition] = field(default_factory=list)

    def __post_init__(self):
        """Ensure at least root decomposition exists."""
        if not self.decompositions:
            self.decompositions.append(
                YAWLDecomposition(id="root", is_root_net=True)
            )

    def root_decomposition(self) -> Optional[YAWLDecomposition]:
        """Get the root decomposition."""
        for decomp in self.decompositions:
            if decomp.is_root_net:
                return decomp
        return None


def create_specification(title: str, description: str = "") -> YAWLSpecification:
    """Create a new YAWL specification with basic metadata.

    Args:
    -----
    title : str
        Specification title
    description : str, optional
        Specification description

    Returns:
    --------
    YAWLSpecification
        New specification with root decomposition
    """
    return YAWLSpecification(
        uri=f"pm4py-{uuid4()}",
        metadata=YAWLMetadata(title=title, description=description),
        decompositions=[
            YAWLDecomposition(id="root", is_root_net=True)
        ]
    )
