from typing import Dict, Union, Any, Optional, List
from pm4py.objects.log.obj import EventLog
import pandas as pd
from enum import Enum
from pm4py.util import exec_utils
from pm4py.statistics.chaotic_activities.variants import niek_sidorova


class Variants(Enum):
    NIEK_SIDOROVA = niek_sidorova


def apply(log: Union[pd.DataFrame, EventLog], variant=Variants.NIEK_SIDOROVA,
          parameters: Optional[Dict[Any, Any]] = None) -> List[Dict[str, Any]]:
    """
    Compute metrics used to detect *chaotic activities* in an event log.

    Parameters
    -----------------
    log
        Event log or Pandas dataframe
    variant
        Variant of the algorithm: Variants.NIEK_SIDOROVA
    parameters
        Variant-specific parameters

    Returns
    -----------------
    chaotic_activities
        List of dictionaries, each representing an activity, sorted decreasingly based on the chaotic score (less is better).
    """
    return exec_utils.get_variant(variant).apply(log, parameters)
