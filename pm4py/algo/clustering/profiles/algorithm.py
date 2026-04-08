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
from pm4py.util import exec_utils
from pm4py.algo.clustering.profiles.variants import sklearn_profiles
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from typing import Optional, Dict, Any, Generator, Union


class Variants(Enum):
    SKLEARN_PROFILES = sklearn_profiles


def apply(
    log: Union[EventLog, EventStream, pd.DataFrame],
    variant=Variants.SKLEARN_PROFILES,
    parameters: Optional[Dict[Any, Any]] = None,
) -> Generator[EventLog, None, None]:
    """
    Apply clustering to the provided event log
    (methods based on the extraction of profiles for the traces of the event log)

    Implements the approach described in:
    Song, Minseok, Christian W. Günther, and Wil MP Van der Aalst. "Trace clustering in process mining." Business Process Management Workshops: BPM 2008 International Workshops, Milano, Italy, September 1-4, 2008. Revised Papers 6. Springer Berlin Heidelberg, 2009.

    Parameters
    ----------------
    log
        Event log
    variant
        Variant of the clustering to be used, available values:
        - Variants.SKLEARN_PROFILES
    parameters
        Variant-specific parameters

    Returns
    ----------------
    generator
        Generator of dataframes (clusters)
    """
    return exec_utils.get_variant(variant).apply(log, parameters=parameters)
