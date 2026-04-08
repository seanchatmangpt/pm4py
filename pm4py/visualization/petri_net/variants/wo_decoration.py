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


from pm4py.visualization.petri_net.common import visualize
from enum import Enum
from pm4py.util.constants import (
    PARAMETER_CONSTANT_ACTIVITY_KEY,
    PARAMETER_CONSTANT_TIMESTAMP_KEY,
)
from pm4py.objects.petri_net.obj import PetriNet, Marking
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog
import graphviz


class Parameters(Enum):
    FORMAT = "format"
    DEBUG = "debug"
    RANKDIR = "set_rankdir"
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = PARAMETER_CONSTANT_TIMESTAMP_KEY
    AGGREGATION_MEASURE = "aggregationMeasure"
    FONT_SIZE = "font_size"


def apply(
    net: PetriNet,
    initial_marking: Marking,
    final_marking: Marking,
    log: EventLog = None,
    aggregated_statistics=None,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> graphviz.Digraph:
    """
    Apply method for Petri net visualization (it calls the
    graphviz_visualization method)

    Parameters
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    log
        (Optional) log
    aggregated_statistics
        Dictionary containing the frequency statistics
    parameters
        Algorithm parameters

    Returns
    -----------
    viz
        Graph object
    """
    # remove unused variables
    del log
    del aggregated_statistics
    return visualize.apply(
        net, initial_marking, final_marking, parameters=parameters
    )
