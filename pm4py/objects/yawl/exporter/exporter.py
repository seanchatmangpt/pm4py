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



'''
YAWL exporter facade for pm4py.

This module provides the main entry point for YAWL export,
dispatching to the appropriate variant implementation.
'''

from enum import Enum
from pm4py.objects.yawl.exporter.variants import yawl_xml
from pm4py.util import exec_utils


class Variants(Enum):
    """YAWL export variants."""
    EXPORT_YAWL_XML = yawl_xml


DEFAULT_VARIANT = Variants.EXPORT_YAWL_XML


def apply(model, file_path, variant=DEFAULT_VARIANT, parameters=None):
    """Export YAWL specification to file.

    Parameters
    -----------
    model
        YAWL specification object
    file_path : str
        Output file path (.yawl extension recommended)
    variant : Variants, optional
        Export variant (default: EXPORT_YAWL_XML)
    parameters
        Export parameters (optional)
    """
    xml_str = exec_utils.get_variant(variant).apply(model, parameters=parameters)

    with open(file_path, "w") as f:
        f.write(xml_str)


def serialize(model, variant=DEFAULT_VARIANT, parameters=None):
    """Serialize YAWL specification to XML string.

    Parameters
    -----------
    model
        YAWL specification object
    variant : Variants, optional
        Export variant (default: EXPORT_YAWL_XML)
    parameters
        Export parameters (optional)

    Returns
    --------
    str
        XML string representation
    """
    return exec_utils.get_variant(variant).apply(model, parameters=parameters)
