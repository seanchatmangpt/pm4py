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
YAWL converter facade for pm4py.

This module provides the main entry point for YAWL conversion,
dispatching to the appropriate variant implementation.
'''

from enum import Enum
from pm4py.objects.conversion.yawl.variants import from_powl
from pm4py.util import exec_utils


class Variants(Enum):
    """YAWL conversion variants."""
    FROM_POWL = from_powl


def apply(model, parameters=None, variant=Variants.FROM_POWL):
    """Convert a model to YAWL specification.

    Parameters
    -----------
    model
        POWL model
    parameters
        Conversion parameters (optional)
    variant : Variants, optional
        Conversion variant (default: FROM_POWL)

    Returns
    --------
    YAWLSpecification
        YAWL specification object
    """
    return exec_utils.get_variant(variant).apply(model, parameters=parameters)
