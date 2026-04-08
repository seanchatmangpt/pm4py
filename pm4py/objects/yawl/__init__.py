'''
PM4Py – A Process Mining Library for Python
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

'''
This module implements the YAWL (Yet Another Workflow Language) object model
for pm4py. YAWL is a workflow language that supports all 43 workflow patterns.

The object model includes:
- YAWLSpecification: Root specification element
- YAWLMetadata: Specification metadata
- YAWLDecomposition: Process net (decomposition)
- YAWLTask: Atomic or composite task
- YAWLFlow: Flow edge between nodes
'''

from pm4py.objects.yawl.obj import (
    YAWLSpecification,
    YAWLMetadata,
    YAWLDecomposition,
    YAWLTask,
    YAWLFlow,
)

__all__ = [
    'YAWLSpecification',
    'YAWLMetadata',
    'YAWLDecomposition',
    'YAWLTask',
    'YAWLFlow',
]
