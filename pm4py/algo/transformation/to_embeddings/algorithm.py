import warnings
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from pm4py.algo.transformation.trace_encodings import algorithm as trace_encodings
from pm4py.algo.transformation.trace_encodings.variants import (
    cases_transformers,
    events_transformers,
)


class Variants(Enum):
    CASES_TRANSFORMERS = cases_transformers
    EVENTS_TRANSFORMERS = events_transformers


def apply(
    log: pd.DataFrame,
    variant=Variants.CASES_TRANSFORMERS,
    parameters: Optional[Dict[Any, Any]] = None,
) -> Tuple[List[str], List[List[float]]]:
    warnings.warn(
        "pm4py.algo.transformation.to_embeddings.apply is deprecated; use "
        "pm4py.algo.transformation.trace_encodings.apply instead.",
        FutureWarning,
        stacklevel=2,
    )
    return trace_encodings.apply(log, variant=variant, parameters=parameters)


def keep_top_k_per_similarity(
    log: pd.DataFrame,
    target_sentence: str,
    k: int,
    variant=Variants.CASES_TRANSFORMERS,
    parameters: Optional[Dict[Any, Any]] = None,
) -> pd.DataFrame:
    warnings.warn(
        "pm4py.algo.transformation.to_embeddings.keep_top_k_per_similarity "
        "is deprecated; use "
        "pm4py.algo.transformation.trace_encodings.keep_top_k_per_similarity "
        "instead.",
        FutureWarning,
        stacklevel=2,
    )
    return trace_encodings.keep_top_k_per_similarity(
        log, target_sentence, k, variant=variant, parameters=parameters
    )
