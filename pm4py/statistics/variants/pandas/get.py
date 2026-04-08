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


from typing import Optional, Dict, Any, Union, List, Set

import pandas as pd

from pm4py.objects.log.util import pandas_numpy_variants


def get_variants_count(
    df: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None
) -> Union[Dict[str, int], Dict[List[str], int]]:
    """
    Gets the dictionary of variants from the current dataframe

    Parameters
    --------------
    df
        Dataframe
    parameters
        Possible parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Column that contains the activity

    Returns
    --------------
    variants_set
        Dictionary of variants in the log
    """
    if parameters is None:
        parameters = {}

    variants_counter, case_variant = pandas_numpy_variants.apply(
        df, parameters=parameters
    )

    return variants_counter


def get_variants_set(
    df: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None
) -> Union[Set[str], Set[List[str]]]:
    """
    Gets the set of variants from the current dataframe

    Parameters
    --------------
    df
        Dataframe
    parameters
        Possible parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Column that contains the activity

    Returns
    --------------
    variants_set
        Set of variants in the log
    """
    if parameters is None:
        parameters = {}

    variants_dict = get_variants_count(df, parameters=parameters)

    return set(variants_dict.keys())
