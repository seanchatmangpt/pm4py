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


from enum import Enum
from pm4py.algo.conformance.footprints.variants import (
    log_model,
    log_extensive,
    trace_extensive,
)
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union, List


class Variants(Enum):
    LOG_MODEL = log_model
    LOG_EXTENSIVE = log_extensive
    TRACE_EXTENSIVE = trace_extensive


def apply(
    log_footprints: Union[Dict[str, Any], List[Dict[str, Any]]],
    model_footprints: Dict[str, Any],
    variant=Variants.LOG_MODEL,
    parameters: Optional[Dict[Any, Any]] = None,
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Apply footprints conformance between a log footprints object
    and a model footprints object

    Parameters
    -----------------
    log_footprints
        Footprints of the log
    model_footprints
        Footprints of the model
    parameters
        Parameters of the algorithm, including:
            - Parameters.STRICT => strict check of the footprints

    Returns
    ------------------
    violations
        Set/dictionary of all the violations between the log footprints
        and the model footprints, OR list of case-per-case violations
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(
        log_footprints, model_footprints, parameters=parameters
    )
