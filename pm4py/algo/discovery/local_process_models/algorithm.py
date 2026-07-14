from enum import Enum
from typing import Optional, Dict, Any, Union, Tuple, List

import pandas as pd

from pm4py import ProcessTree
from pm4py.algo.discovery.local_process_models.metrics.quality_metrics import LocalProcessModelStats
from pm4py.algo.discovery.local_process_models.variants import classic
from pm4py.objects.log.obj import EventLog
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic


def find_local_process_models(
    log: Union[EventLog, pd.DataFrame],
    selected_activities: Union[None, list] = None,
    variant=Variants.CLASSIC,
    parameters: Optional[Dict[Any, Any]] = None,
) -> List[Tuple[ProcessTree, LocalProcessModelStats]]:
    return exec_utils.get_variant(variant).apply(log, selected_activities, parameters)

