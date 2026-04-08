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


from pm4py.algo.transformation.to_embeddings.variants import cases_transformers, events_transformers
from enum import Enum
from pm4py.util import exec_utils
import pandas as pd
from typing import Optional, Dict, Any, List, Tuple


class Variants(Enum):
    CASES_TRANSFORMERS = cases_transformers
    EVENTS_TRANSFORMERS = events_transformers


def apply(log: pd.DataFrame, variant=Variants.CASES_TRANSFORMERS, parameters: Optional[Dict[Any, Any]] = None) -> Tuple[
    List[str], List[List[float]]]:
    """
    Computes the embeddings (case/event level, depending on the variant) of the provided dataframe.

    Parameters
    -----------------
    log
        Pandas dataframe
    variant
        Variant of the algorithm, including:
        - Variants.CASES_TRANSFORMERS => computes the embeddings at the case level
        - Variants.EVENTS_TRANSFORMERS => computes the embeddings at the event level
    parameters
        Variant-specific parameters

    Returns
    ----------------
    ids
        Identifiers of the considered events/cases
    embeddings_list
        List of embeddings for the considered events/cases
    """
    return exec_utils.get_variant(variant).apply(log, parameters=parameters)


def keep_top_k_per_similarity(log: pd.DataFrame, target_sentence: str, k: int, variant=Variants.CASES_TRANSFORMERS,
                              parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Keeps the top K events/cases per similarity

    Parameters
    ----------------
    log
        Pandas dataframe
    variant
        Variant of the algorithm, including:
        - Variants.CASES_TRANSFORMERS => computes the embeddings at the case level
        - Variants.EVENTS_TRANSFORMERS => computes the embeddings at the event level
    parameters
        Variant-specific parameters

    Returns
    -----------------
    filtered_log
        Filtered event log
    """
    return exec_utils.get_variant(variant).keep_top_k_per_similarity(log, target_sentence, k, parameters=parameters)
