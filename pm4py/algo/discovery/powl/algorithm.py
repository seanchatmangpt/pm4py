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

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.algo.discovery.powl.inductive.variants.im_dynamic_clustering_frequencies import (
    POWLInductiveMinerDynamicClusteringFrequency, )
from pm4py.algo.discovery.powl.inductive.variants.im_tree import IMBasePOWL
from pm4py.algo.discovery.powl.inductive.variants.im_brute_force import (
    POWLInductiveMinerBruteForce,
)
from pm4py.algo.discovery.powl.inductive.variants.im_maximal import (
    POWLInductiveMinerMaximalOrder,
)
from pm4py.algo.discovery.powl.inductive.variants.powl_discovery_varaints import (
    POWLDiscoveryVariant, )

from pm4py import util
from pm4py.algo.discovery.inductive.algorithm import Parameters
from pm4py.objects.powl.obj import POWL

from pm4py.util import xes_constants as xes_util
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL

from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union, Type
from pm4py.objects.log.obj import EventLog
import pandas as pd


def get_variant(variant: POWLDiscoveryVariant) -> Type[IMBasePOWL]:
    if variant == POWLDiscoveryVariant.TREE:
        return IMBasePOWL
    elif variant == POWLDiscoveryVariant.BRUTE_FORCE:
        return POWLInductiveMinerBruteForce
    elif variant == POWLDiscoveryVariant.MAXIMAL:
        return POWLInductiveMinerMaximalOrder
    elif variant == POWLDiscoveryVariant.DYNAMIC_CLUSTERING:
        return POWLInductiveMinerDynamicClusteringFrequency
    elif variant in (
        POWLDiscoveryVariant.DECISION_GRAPH_MAX,
        POWLDiscoveryVariant.DECISION_GRAPH_CLUSTERING,
        POWLDiscoveryVariant.DECISION_GRAPH_CYCLIC,
        POWLDiscoveryVariant.DECISION_GRAPH_CYCLIC_STRICT,
    ):
        if importlib.util.find_spec("powl") is None:
            raise ImportError(
                "The 'powl' package is required for DecisionGraph variants. "
                "Install it with: pip install pm4py[powl]"
            )
        from powl.discovery.total_order_based import algorithm as powl_discovery
        variant_map = {
            POWLDiscoveryVariant.DECISION_GRAPH_MAX: powl_discovery.POWLDiscoveryVariant.DECISION_GRAPH_MAX,
            POWLDiscoveryVariant.DECISION_GRAPH_CLUSTERING: powl_discovery.POWLDiscoveryVariant.DECISION_GRAPH_CLUSTERING,
            POWLDiscoveryVariant.DECISION_GRAPH_CYCLIC: powl_discovery.POWLDiscoveryVariant.DECISION_GRAPH_CYCLIC,
            POWLDiscoveryVariant.DECISION_GRAPH_CYCLIC_STRICT: powl_discovery.POWLDiscoveryVariant.DECISION_GRAPH_CYCLIC_STRICT,
        }
        return _PowlPackageVariantFactory(variant_map[variant])
    else:
        raise Exception("Invalid Variant!")


class _PowlPackageVariant(IMBasePOWL):
    """Wrapper that delegates to the PyPI powl package for DecisionGraph variants."""

    def __init__(self, powl_variant):
        self.powl_variant = powl_variant

    def apply(self, obj, parameters=None):
        from powl.discovery.total_order_based import algorithm as powl_discovery
        # The powl package expects a raw UVCL, not an IMDataStructureUVCL wrapper.
        # Extract the raw UVCL if needed.
        from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
        raw_obj = obj._obj if isinstance(obj, IMDataStructureUVCL) else obj
        return powl_discovery.apply(
            raw_obj, variant=self.powl_variant, parameters=parameters, simplify=False
        )


class _PowlPackageVariantFactory:
    """Factory that returns _PowlPackageVariant instances, matching the IMBasePOWL instantiation pattern."""

    def __init__(self, powl_variant):
        self.powl_variant = powl_variant

    def __call__(self, parameters=None):
        return _PowlPackageVariant(self.powl_variant)


def apply(
    obj: Union[EventLog, pd.DataFrame, UVCL],
    parameters: Optional[Dict[Any, Any]] = None,
    variant=POWLDiscoveryVariant.MAXIMAL,
) -> POWL:
    if parameters is None:
        parameters = {}
    ack = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes_util.DEFAULT_NAME_KEY
    )
    tk = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY, parameters, xes_util.DEFAULT_TIMESTAMP_KEY
    )
    cidk = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, util.constants.CASE_CONCEPT_NAME
    )

    if type(obj) is UVCL:
        uvcl = obj
    else:
        uvcl = comut.get_variants(
            comut.project_univariate(
                obj, key=ack, df_glue=cidk, df_sorting_criterion_key=tk
            )
        )

    algorithm = get_variant(variant)
    im = algorithm(parameters)
    res = im.apply(IMDataStructureUVCL(uvcl), parameters)
    res = res.simplify()

    return res
