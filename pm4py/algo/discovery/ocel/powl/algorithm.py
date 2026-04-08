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
from enum import Enum
from typing import Optional, Dict, Any


class Variants(Enum):
    FLATTENING = "flattening"
    OC_POWL = "oc_powl"


def apply(
    ocel,
    parameters: Optional[Dict[Any, Any]] = None,
    variant=Variants.OC_POWL,
):
    """
    Discovers a Petri net from an object-centric event log using POWL-based techniques.

    Requires the 'powl' PyPI package: ``pip install pm4py[powl]``.

    :param ocel: object-centric event log
    :param parameters: optional parameters
    :param variant: variant of the algorithm (FLATTENING or OC_POWL)
    :return: A tuple (net, im, fm) representing the discovered Petri net.
    """
    if importlib.util.find_spec("powl") is None:
        raise ImportError(
            "The 'powl' package is required for OCEL POWL discovery. "
            "Install it with: pip install pm4py[powl]"
        )
    from powl.discovery.object_centric.algorithm import apply as oc_discovery
    from powl.discovery.object_centric.algorithm import OCELDiscoveryVariant

    if variant == Variants.OC_POWL:
        powl_variant = OCELDiscoveryVariant.OC_POWL
    else:
        powl_variant = OCELDiscoveryVariant.FLATTENING

    return oc_discovery(ocel, variant=powl_variant, parameters=parameters)
