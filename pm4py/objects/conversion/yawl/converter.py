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
