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



from pm4py.util import exec_utils
from enum import Enum
from pm4py.algo.conformance.declare.variants import classic
from pm4py.objects.log.obj import EventLog
import pandas as pd
from typing import Union, Dict, Optional, Any, List


class Variants(Enum):
    CLASSIC = classic


def apply(
    log: Union[EventLog, pd.DataFrame],
    model: Dict[str, Dict[Any, Dict[str, int]]],
    variant=Variants.CLASSIC,
    parameters: Optional[Dict[Any, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Applies conformance checking against a DECLARE model.

    Parameters
    --------------
    log
        Event log / Pandas dataframe
    model
        DECLARE model
    variant
        Variant to be used:
        - Variants.CLASSIC
    parameters
        Variant-specific parameters

    Returns
    -------------
    lst_conf_res
        List containing for every case a dictionary with different keys:
        - no_constr_total => the total number of constraints of the DECLARE model
        - deviations => a list of deviations
        - no_dev_total => the total number of deviations
        - dev_fitness => the fitness (1 - no_dev_total / no_constr_total)
        - is_fit => True if the case is perfectly fit
    """
    return exec_utils.get_variant(variant).apply(log, model, parameters)


def get_diagnostics_dataframe(
    log, conf_result, variant=Variants.CLASSIC, parameters=None
) -> pd.DataFrame:
    """
    Gets the diagnostics dataframe from a log and the results
    of DECLARE-based conformance checking

    Parameters
    --------------
    log
        Event log
    conf_result
        Results of conformance checking
    variant
        Variant to be used:
        - Variants.CLASSIC
    parameters
        Variant-specific parameters

    Returns
    --------------
    diagn_dataframe
        Diagnostics dataframe
    """
    return exec_utils.get_variant(variant).get_diagnostics_dataframe(
        log, conf_result, parameters
    )
