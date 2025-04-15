from enum import Enum
from pm4py.algo.concept_drift.variants import bose
from pm4py.util import exec_utils
import pandas as pd
from pm4py.objects.log.obj import EventLog
from typing import Union, Dict, Any, Optional, Tuple, List


class Variants(Enum):
    BOSE = bose


def apply(log: Union[EventLog, pd.DataFrame], variant=Variants.BOSE, parameters: Optional[Dict[Any, Any]] = None) -> \
Tuple[List[pd.DataFrame], List[int], List[float]]:
    """
    Parameters
    --------------
    log
        Event log or Pandas dataframe
    variant
        Variant of the algorithm (available: Variants.BOSE)
    parameters
        Variant-specific parameters

    Returns
    ---------------
    returned_sublogs : List[EventLog]
        A list of sub-logs, where each sub-log is an EventLog object representing the cumulative segment of the original event log from the start up to each detected change point (and the final sub-log up to the end). Note: Due to a potential implementation issue, these sub-logs are not segments between change points but rather cumulative logs up to each change point.
    change_timestamps : List[float]
        A list of timestamps where concept drifts are detected. Each timestamp corresponds to the start time of the first trace in the sub-log where a change point occurs, based on case start timestamps.
    p_values : List[float]
        A list of p-values associated with each detected change point, indicating the statistical significance of the drift (lower values suggest stronger evidence of a change).
    """
    return exec_utils.get_variant(variant).apply(log, parameters)
