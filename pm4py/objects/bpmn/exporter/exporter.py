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

from pm4py.objects.bpmn.exporter.variants import etree
from pm4py.util import exec_utils


class Variants(Enum):
    ETREE = etree


DEFAULT_VARIANT = Variants.ETREE


def apply(bpmn_graph, target_path, variant=DEFAULT_VARIANT, parameters=None):
    """
    Exports the BPMN diagram to a file

    Parameters
    -------------
    bpmn_graph
        BPMN diagram
    target_path
        Target path
    variant
        Variant of the algorithm to use, possible values:
        - Variants.ETREE
    parameters
        Possible parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(
        bpmn_graph, target_path, parameters=parameters
    )


def serialize(bpmn_graph, variant=DEFAULT_VARIANT, parameters=None):
    """
    Serializes the BPMN object into a binary string

    Parameters
    -------------
    bpmn_graph
        BPMN diagram
    variant
        Variant of the algorithm to use, possible values:
        - Variants.ETREE
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    serialization
        Binary string (BPMN 2.0 XML standard)
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).get_xml_string(
        bpmn_graph, parameters=parameters
    )
