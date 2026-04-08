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


from typing import Dict, Any, Optional, List

from pm4py.objects.ocel.obj import OCEL
from pm4py.util import pandas_utils


def related_objects_dct_per_type(
    ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None
) -> Dict[str, Dict[str, List[str]]]:
    if parameters is None:
        parameters = {}

    object_types = pandas_utils.format_unique(
        ocel.relations[ocel.object_type_column].unique()
    )
    dct = {}
    for ot in object_types:
        dct[ot] = (
            ocel.relations[ocel.relations[ocel.object_type_column] == ot]
            .groupby(ocel.event_id_column)[ocel.object_id_column]
            .apply(list)
            .to_dict()
        )
    return dct


def related_objects_dct_overall(
    ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None
) -> Dict[str, List[str]]:
    if parameters is None:
        parameters = {}

    evids = pandas_utils.format_unique(
        ocel.events[ocel.event_id_column].unique()
    )
    dct = (
        ocel.relations.groupby(ocel.event_id_column)[ocel.object_id_column]
        .agg(list)
        .to_dict()
    )

    for evid in evids:
        if evid not in dct:
            dct[evid] = []

    return dct
