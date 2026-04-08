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


from pm4py.statistics.passed_time.polars.variants import pre, post
from typing import Optional, Dict, Any
import polars as pl


def apply(
    lf: pl.LazyFrame,
    activity: str,
    parameters: Optional[Dict[Any, Any]] = None,
) -> Dict[str, Any]:
    """
    Gets the time passed from/to each preceding/succeeding activity

    Parameters
    -------------
    lf
        LazyFrame
    activity
        Activity that we are considering
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    dictio
        Dictionary containing both 'pre' and 'post' keys with the
        list of aggregates times from/to each preceding/succeeding activity
    """
    if parameters is None:
        parameters = {}

    # Get pre statistics
    pre_stats = pre.apply(lf, activity, parameters=parameters)

    # Get post statistics  
    post_stats = post.apply(lf, activity, parameters=parameters)

    # Combine results
    result = {}
    result.update(pre_stats)
    result.update(post_stats)

    return result