import warnings
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

from pm4py.algo.transformation.trace_encodings import algorithm as trace_encodings
from pm4py.algo.transformation.trace_encodings.variants import (
    event_based,
    temporal,
    temporal_lazy,
    trace_based,
)
from pm4py.objects.log.obj import EventLog, EventStream


class Variants(Enum):
    EVENT_BASED = event_based
    TRACE_BASED = trace_based
    TEMPORAL = temporal
    TEMPORAL_LAZY = temporal_lazy


def apply(
    log: Union[EventLog, pd.DataFrame, EventStream],
    variant: Any = Variants.TRACE_BASED,
    parameters: Optional[Dict[Any, Any]] = None,
) -> Tuple[Any, List[str]]:
    warnings.warn(
        "pm4py.algo.transformation.log_to_features.apply is deprecated; use "
        "pm4py.algo.transformation.trace_encodings.apply instead.",
        FutureWarning,
        stacklevel=2,
    )
    return trace_encodings.apply(log, variant=variant, parameters=parameters)
