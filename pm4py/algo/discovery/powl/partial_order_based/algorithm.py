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



import importlib.util
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog
import pandas as pd


def apply(
    log: Union[EventLog, pd.DataFrame],
    parameters: Optional[Dict[Any, Any]] = None,
) -> "POWL":
    """
    Discovers a POWL model from a partially ordered event log.

    Requires the 'powl' PyPI package: ``pip install pm4py[powl]``.

    Reference paper:
    H Kourani, G Park, WMP van der Aalst. "Revealing Inherent Concurrency in Event Data:
    A Partial Order Approach to Process Discovery"

    :param log: event log / Pandas dataframe
    :param parameters: Optional parameters including:
        - activity_key: attribute to be used for the activity (default: "concept:name")
        - order_key: attribute to be used for ordering events within traces (default: "time:timestamp")
        - case_id_key: attribute to be used as case identifier (default: "case:concept:name")
        - lifecycle_key: attribute to be used as lifecycle identifier (default: "lifecycle:transition")
    :rtype: ``POWL``
    """
    if importlib.util.find_spec("powl") is None:
        raise ImportError(
            "The 'powl' package is required for partial order-based discovery. "
            "Install it with: pip install pm4py[powl]"
        )
    from powl.discovery.partial_order_based.utils import log_to_partial_orders
    from powl.discovery.partial_order_based.variants.base import miner

    if parameters is None:
        parameters = {}

    activity_key = parameters.get("activity_key", "concept:name")
    order_key = parameters.get("order_key", "time:timestamp")
    case_id_key = parameters.get("case_id_key", "case:concept:name")
    lifecycle_key = parameters.get("lifecycle_key", "lifecycle:transition")

    complete_tags = {"complete", "COMPLETE", "Complete"}
    start_tags = {"start", "START", "Start"}

    partial_orders = log_to_partial_orders.apply(
        log,
        case_id_col=case_id_key,
        activity_col=activity_key,
        ordering_col=order_key,
        lifecycle_col=lifecycle_key,
        start_transitions=start_tags,
        complete_transitions=complete_tags,
    )

    return miner.apply(partial_orders)
