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
