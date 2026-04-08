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

from pm4py.objects.petri_net.exporter.variants import pnml
from pm4py.util import exec_utils


class Variants(Enum):
    PNML = pnml


PNML = Variants.PNML


def apply(
    net,
    initial_marking,
    output_filename,
    final_marking=None,
    variant=PNML,
    parameters=None,
):
    """
    Export a Petri net along with an initial marking (and possibly a final marking) to an output file

    Parameters
    ------------
    net
        Petri net
    initial_marking
        Initial marking
    output_filename
        Output filename
    final_marking
        Final marking
    variant
        Variant of the algorithm, possible values:
            - Variants.PNML
    parameters
        Parameters of the exporter
    """
    return exec_utils.get_variant(variant).export_net(
        net,
        initial_marking,
        output_filename,
        final_marking=final_marking,
        parameters=parameters,
    )


def serialize(net, initial_marking, final_marking=None, variant=PNML):
    """
    Serialize a Petri net along with an initial marking (and possibly a final marking) to a binary PNML string

    Parameters
    ------------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    variant
        Variant of the algorithm, possible values:
            - Variants.PNML

    Returns
    -------------
    serialization
        Binary string (BPMN 2.0 XML standard)
    """
    return exec_utils.get_variant(variant).export_petri_as_string(
        net, initial_marking, final_marking=final_marking
    )
