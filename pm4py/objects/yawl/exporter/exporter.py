'''
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see this software project's root or
visit <https://www.gnu.org/licenses/>.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
'''

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
