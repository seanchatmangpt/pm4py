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


def replace_values(dfg1, dfg2):
    """
    Replace edge values specified in a DFG by values from a (potentially bigger) DFG

    Parameters
    -----------
    dfg1
        First specified DFG (where values of edges should be replaces)
    dfg2
        Second specified DFG (from which values should be taken)

    Returns
    -----------
    dfg1
        First specified DFG with overrided values
    """
    for edge in dfg1:
        if edge in dfg2:
            dfg1[edge] = dfg2[edge]
    return dfg1
