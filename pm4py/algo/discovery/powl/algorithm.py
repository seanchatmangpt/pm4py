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
from pm4py.algo.discovery.powl.inductive.variants.im_choice_graph import (
    InductiveMinerChoiceGraph,
    InductiveMinerChoiceGraphMaximal,
    InductiveMinerChoiceGraphClustering,
    InductiveMinerChoiceGraphCyclic,
    InductiveMinerChoiceGraphCyclicStrict,
)

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
    elif variant == POWLDiscoveryVariant.DECISION_GRAPH_MAX:
        # Self-contained choice graph discovery (no external powl package needed)
        return InductiveMinerChoiceGraphMaximal
    elif variant == POWLDiscoveryVariant.DECISION_GRAPH_CLUSTERING:
        # Self-contained choice graph discovery with clustering
        return InductiveMinerChoiceGraphClustering
    elif variant == POWLDiscoveryVariant.DECISION_GRAPH_CYCLIC:
        # Self-contained choice graph discovery with cycle detection
        return InductiveMinerChoiceGraphCyclic
    elif variant == POWLDiscoveryVariant.DECISION_GRAPH_CYCLIC_STRICT:
        # Self-contained choice graph discovery with strict cycle validation
        return InductiveMinerChoiceGraphCyclicStrict
    else:
        raise Exception(f"Invalid Variant: {variant}")


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
