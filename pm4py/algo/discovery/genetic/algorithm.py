from enum import Enum
from pm4py.util import exec_utils
from typing import Union, Optional, Dict, Any, Tuple
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from pm4py.util import constants


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    POPULATION_SIZE = "population_size"
    ELITISM_RATE = "elitism_rate"
    CROSSOVER_RATE = "crossover_rate"
    MUTATION_RATE = "mutation_rate"
    GENERATIONS = "generations"
    ELITISM_MIN_SAMPLE = "elitism_min_sample"
    TOURNAMENT_TIMEOUT = "tournament_timeout"
    LOG_CSV = "log_csv"


from pm4py.algo.discovery.genetic.variants import classic


class Variants(Enum):
    CLASSIC = classic


def apply(
    log: Union[EventLog, EventStream, pd.DataFrame],
    variant=Variants.CLASSIC,
    parameters: Optional[Dict[Any, Any]] = None,
) -> Tuple[PetriNet, Marking, Marking]:
    """
    Discovers a Petri net using the genetic miner.

    Parameters
    ---------------
    log
        Event log / Event stream / Pandas dataframe
    variant
        Variant of the algorithm to be used, possible values:
        - Variants.CLASSIC
    parameters
        Variant-specific parameters

    Returns
    ---------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    return exec_utils.get_variant(variant).apply(log, parameters)
