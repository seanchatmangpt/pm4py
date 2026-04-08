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


__doc__ = ""

# Import POWL classes for complexity metrics
try:
    from pm4py.objects.powl.obj import (
        Transition, SilentTransition, OperatorPOWL,
        StrictPartialOrder, DecisionGraph
    )
except ImportError:
    # Fallback for older versions or different module structure
    from pm4py.objects.powl.obj import (
        Transition, OperatorPOWL, StrictPartialOrder, POWL
    )
    SilentTransition = None
    DecisionGraph = None

from typing import List, Optional, Tuple, Dict, Union, Generator, Set, Any

from pm4py.objects.log.obj import Trace, EventLog, EventStream
from pm4py.utils import __event_log_deprecation_warning
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.utils import get_properties, pandas_utils, constants
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns
from pm4py.util import labels_similarity as ls_util
from pm4py.util import deprecation

import pandas as pd


@deprecation.deprecated(
    deprecated_in="2.3.0",
    removed_in="3.0.0",
    details="this method will be removed in a future release.",
)
def construct_synchronous_product_net(
    trace: Trace,
    petri_net: PetriNet,
    initial_marking: Marking,
    final_marking: Marking,
) -> Tuple[PetriNet, Marking, Marking]:
    """
    Constructs the synchronous product net between a trace and a Petri net process model.

    :param trace: A trace from an event log.
    :param petri_net: The Petri net process model.
    :param initial_marking: The initial marking of the Petri net.
    :param final_marking: The final marking of the Petri net.
    :return: A tuple containing the synchronous Petri net, the initial marking, and the final marking.
    :rtype: Tuple[PetriNet, ~pm4py.objects.petri_net.obj.Marking, ~pm4py.objects.petri_net.obj.Marking]

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        log = pm4py.read_xes('log.xes')
        sync_net, sync_im, sync_fm = pm4py.construct_synchronous_product_net(log[0], net, im, fm)
    """
    from pm4py.objects.petri_net.utils.petri_utils import construct_trace_net
    from pm4py.objects.petri_net.utils.synchronous_product import construct
    from pm4py.objects.petri_net.utils.align_utils import SKIP

    trace_net, trace_im, trace_fm = construct_trace_net(trace)
    sync_net, sync_im, sync_fm = construct(
        trace_net,
        trace_im,
        trace_fm,
        petri_net,
        initial_marking,
        final_marking,
        SKIP,
    )
    return sync_net, sync_im, sync_fm


def compute_emd(
    language1: Dict[List[str], float], language2: Dict[List[str], float]
) -> float:
    """
    Computes the Earth Mover Distance (EMD) between two stochastic languages. For example, one language may be extracted from a log, and the other from a process model.

    :param language1: The first stochastic language.
    :param language2: The second stochastic language.
    :return: The computed Earth Mover Distance.
    :rtype: float

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes('tests/input_data/running-example.xes')
        language_log = pm4py.get_stochastic_language(log)
        print(language_log)
        net, im, fm = pm4py.read_pnml('tests/input_data/running-example.pnml')
        language_model = pm4py.get_stochastic_language(net, im, fm)
        print(language_model)
        emd_distance = pm4py.compute_emd(language_log, language_model)
        print(emd_distance)
    """
    from pm4py.algo.evaluation.earth_mover_distance import (
        algorithm as earth_mover_distance,
    )

    return earth_mover_distance.apply(language1, language2)


def solve_marking_equation(
    petri_net: PetriNet,
    initial_marking: Marking,
    final_marking: Marking,
    cost_function: Dict[PetriNet.Transition, float] = None,
) -> float:
    """
    Solves the marking equation of a Petri net using an Integer Linear Programming (ILP) approach. An optional transition-based cost function can be provided to minimize the solution.

    :param petri_net: The Petri net.
    :param initial_marking: The initial marking of the Petri net.
    :param final_marking: The final marking of the Petri net.
    :param cost_function: (Optional) A dictionary mapping transitions to their associated costs. If not provided, a default cost of 1 is assigned to each transition.
    :return: The heuristic value obtained by solving the marking equation.
    :rtype: float

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        heuristic = pm4py.solve_marking_equation(net, im, fm)
    """
    from pm4py.algo.analysis.marking_equation import (
        algorithm as marking_equation,
    )

    if cost_function is None:
        cost_function = {t: 1 for t in petri_net.transitions}

    me = marking_equation.build(
        petri_net,
        initial_marking,
        final_marking,
        parameters={"costs": cost_function},
    )
    return marking_equation.get_h_value(me)


@deprecation.deprecated(
    deprecated_in="2.3.0",
    removed_in="3.0.0",
    details="this method will be removed in a future release.",
)
def solve_extended_marking_equation(
    trace: Trace,
    sync_net: PetriNet,
    sync_im: Marking,
    sync_fm: Marking,
    split_points: Optional[List[int]] = None,
) -> float:
    """
    Computes a heuristic value (an underestimation of the cost of an alignment) between a trace
    and a synchronous product net using the extended marking equation with the standard cost function.
    For example, synchronization moves have a cost of 0, invisible moves have a cost of 1,
    and other moves on the model or log have a cost of 10,000. This method provides optimal provisioning of the split points.

    :param trace: The trace to evaluate.
    :param sync_net: The synchronous product net.
    :param sync_im: The initial marking of the synchronous net.
    :param sync_fm: The final marking of the synchronous net.
    :param split_points: (Optional) The indices of the events in the trace to be used as split points. If not specified, the split points are identified automatically.
    :return: The heuristic value representing the cost underestimation.
    :rtype: float

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        log = pm4py.read_xes('log.xes')
        ext_mark_eq_heu = pm4py.solve_extended_marking_equation(log[0], net, im, fm)
    """
    from pm4py.algo.analysis.extended_marking_equation import (
        algorithm as extended_marking_equation,
    )

    parameters = {}
    if split_points is not None:
        parameters[
            extended_marking_equation.Variants.CLASSIC.value.Parameters.SPLIT_IDX
        ] = split_points
    me = extended_marking_equation.build(
        trace, sync_net, sync_im, sync_fm, parameters=parameters
    )
    return extended_marking_equation.get_h_value(me)


def check_is_sound(petri_net: PetriNet,
                   initial_marking: Marking,
                   final_marking: Marking) -> bool:
    """
    Checks if a given Petri net is a sound Workflow net (WF-net).
    Returns a boolean value.

    A Petri net is a WF-net if and only if:

        - It has a unique source place.
        - It has a unique end place.
        - Every element in the WF-net is on a path from the source to the sink place.

    A WF-net is sound if and only if:

        - It contains no live-locks.
        - It contains no deadlocks.
        - It is always possible to reach the final marking from any reachable marking.

    :param petri_net: The Petri net to check.
    :param initial_marking: The initial marking of the Petri net.
    :param final_marking: The final marking of the Petri net.
    :returns: boolean (True if the Petri net is sound)
    """
    try:
        from pm4py.convert import convert_to_powl
        powl_model = convert_to_powl(petri_net, initial_marking, final_marking)
        return True
    except:
        pass

    from pm4py.algo.analysis.woflan import algorithm as woflan
    soundness = woflan.apply(
        petri_net,
        initial_marking,
        final_marking,
        parameters={
            "return_asap_when_not_sound": True,
            "return_diagnostics": True,
            "print_diagnostics": False,
        },
    )

    return soundness[0]


@deprecation.deprecated(
    deprecated_in="2.3.0",
    removed_in="3.0.0",
    details="this method will be removed in a future release.",
)
def check_soundness(
    petri_net: PetriNet,
    initial_marking: Marking,
    final_marking: Marking,
    print_diagnostics: bool = False,
) -> Tuple[bool, Dict[str, Any]]:
    """
    Checks if a given Petri net is a sound Workflow net (WF-net).

    A Petri net is a WF-net if and only if:

        - It has a unique source place.
        - It has a unique end place.
        - Every element in the WF-net is on a path from the source to the sink place.

    A WF-net is sound if and only if:

        - It contains no live-locks.
        - It contains no deadlocks.
        - It is always possible to reach the final marking from any reachable marking.

    For a formal definition of a sound WF-net, refer to: http://www.padsweb.rwth-aachen.de/wvdaalst/publications/p628.pdf

    The returned tuple consists of:

        - A boolean indicating whether the Petri net is a sound WF-net.
        - A dictionary containing diagnostics collected while running WOFLAN, associating diagnostic names with their corresponding details.

    :param petri_net: The Petri net to check.
    :param initial_marking: The initial marking of the Petri net.
    :param final_marking: The final marking of the Petri net.
    :param print_diagnostics: If True, additional diagnostics will be printed during the execution of WOFLAN.
    :return: A tuple containing a boolean indicating soundness and a dictionary of diagnostics.
    :rtype: Tuple[bool, Dict[str, Any]]

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        is_sound = pm4py.check_soundness(net, im, fm)
    """
    from pm4py.algo.analysis.woflan import algorithm as woflan

    return woflan.apply(
        petri_net,
        initial_marking,
        final_marking,
        parameters={
            "return_asap_when_not_sound": True,
            "return_diagnostics": True,
            "print_diagnostics": print_diagnostics,
        },
    )


def cluster_log(
    log: Union[EventLog, EventStream, pd.DataFrame],
    sklearn_clusterer=None,
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
) -> Generator[EventLog, None, None]:
    """
    Applies clustering to the provided event log by extracting profiles for the log's traces and clustering them using a Scikit-Learn clusterer (default is K-Means with two clusters).

    :param log: The event log to cluster.
    :param sklearn_clusterer: (Optional) The Scikit-Learn clusterer to use. Default is KMeans with `n_clusters=2`, `random_state=0`, and `n_init="auto"`.
    :param activity_key: The key used to identify activities in the log.
    :param timestamp_key: The key used to identify timestamps in the log.
    :param case_id_key: The key used to identify case IDs in the log.
    :return: A generator that yields clustered event logs as pandas DataFrames.
    :rtype: Generator[pd.DataFrame, None, None]

    .. code-block:: python3

        import pm4py

        for clust_log in pm4py.cluster_log(df):
            print(clust_log)
    """
    __event_log_deprecation_warning(log)

    properties = get_properties(
        log,
        activity_key=activity_key,
        case_id_key=case_id_key,
        timestamp_key=timestamp_key,
    )
    if sklearn_clusterer is not None:
        properties["sklearn_clusterer"] = sklearn_clusterer

    from pm4py.algo.clustering.profiles import algorithm as clusterer

    return clusterer.apply(log, parameters=properties)


def insert_artificial_start_end(
    log: Union[EventLog, pd.DataFrame],
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
    artificial_start=constants.DEFAULT_ARTIFICIAL_START_ACTIVITY,
    artificial_end=constants.DEFAULT_ARTIFICIAL_END_ACTIVITY,
) -> Union[EventLog, pd.DataFrame]:
    """
    Inserts artificial start and end activities into an event log or a Pandas DataFrame.

    :param log: The event log or Pandas DataFrame to modify.
    :param activity_key: The attribute key used for activities.
    :param timestamp_key: The attribute key used for timestamps.
    :param case_id_key: The attribute key used to identify cases.
    :param artificial_start: The symbol to use for the artificial start activity.
    :param artificial_end: The symbol to use for the artificial end activity.
    :return: The event log or Pandas DataFrame with artificial start and end activities inserted.
    :rtype: Union[EventLog, pd.DataFrame]

    .. code-block:: python3

        import pm4py

        dataframe = pm4py.insert_artificial_start_end(
            dataframe,
            activity_key='concept:name',
            case_id_key='case:concept:name',
            timestamp_key='time:timestamp'
        )
    """
    __event_log_deprecation_warning(log)

    properties = get_properties(
        log,
        activity_key=activity_key,
        case_id_key=case_id_key,
        timestamp_key=timestamp_key,
    )
    properties[constants.PARAM_ARTIFICIAL_START_ACTIVITY] = artificial_start
    properties[constants.PARAM_ARTIFICIAL_END_ACTIVITY] = artificial_end

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(
            log,
            activity_key=activity_key,
            case_id_key=case_id_key,
            timestamp_key=timestamp_key,
        )
        from pm4py.objects.log.util import dataframe_utils

        return dataframe_utils.insert_artificial_start_end(
            log, parameters=properties
        )
    else:
        from pm4py.objects.log.util import artificial

        return artificial.insert_artificial_start_end(
            log, parameters=properties
        )


def insert_case_service_waiting_time(
    log: Union[EventLog, pd.DataFrame],
    service_time_column: str = "@@service_time",
    sojourn_time_column: str = "@@sojourn_time",
    waiting_time_column: str = "@@waiting_time",
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
    start_timestamp_key: str = "time:timestamp",
) -> pd.DataFrame:
    """
    Inserts service time, waiting time, and sojourn time information for each case into a Pandas DataFrame.

    :param log: The event log or Pandas DataFrame to modify.
    :param service_time_column: The name of the column to store service times.
    :param sojourn_time_column: The name of the column to store sojourn times.
    :param waiting_time_column: The name of the column to store waiting times.
    :param activity_key: The attribute key used for activities.
    :param timestamp_key: The attribute key used for timestamps.
    :param case_id_key: The attribute key used to identify cases.
    :param start_timestamp_key: The attribute key used for the start timestamp of cases.
    :return: A Pandas DataFrame with the inserted service, waiting, and sojourn time columns.
    :rtype: pd.DataFrame

    .. code-block:: python3

        import pm4py

        dataframe = pm4py.insert_case_service_waiting_time(
            dataframe,
            activity_key='concept:name',
            timestamp_key='time:timestamp',
            case_id_key='case:concept:name',
            start_timestamp_key='time:timestamp'
        )
    """
    __event_log_deprecation_warning(log)

    properties = get_properties(
        log,
        activity_key=activity_key,
        case_id_key=case_id_key,
        timestamp_key=timestamp_key,
    )

    from pm4py.objects.conversion.log import converter as log_converter

    log_df = log_converter.apply(
        log,
        variant=log_converter.Variants.TO_DATA_FRAME,
        parameters=properties,
    )

    return pandas_utils.insert_case_service_waiting_time(
        log_df,
        case_id_column=case_id_key,
        timestamp_column=timestamp_key,
        start_timestamp_column=start_timestamp_key,
        service_time_column=service_time_column,
        waiting_time_column=waiting_time_column,
        sojourn_time_column=sojourn_time_column,
    )


def insert_case_arrival_finish_rate(
    log: Union[EventLog, pd.DataFrame],
    arrival_rate_column: str = "@@arrival_rate",
    finish_rate_column: str = "@@finish_rate",
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
    start_timestamp_key: str = "time:timestamp",
) -> pd.DataFrame:
    """
    Inserts arrival and finish rate information for each case into a Pandas DataFrame.

    The arrival rate is computed as the time difference between the start of the current case and the start of the previous case to start.
    The finish rate is computed as the time difference between the end of the current case and the end of the next case to finish.

    :param log: The event log or Pandas DataFrame to modify.
    :param arrival_rate_column: The name of the column to store arrival rates.
    :param finish_rate_column: The name of the column to store finish rates.
    :param activity_key: The attribute key used for activities.
    :param timestamp_key: The attribute key used for timestamps.
    :param case_id_key: The attribute key used to identify cases.
    :param start_timestamp_key: The attribute key used for the start timestamp of cases.
    :return: A Pandas DataFrame with the inserted arrival and finish rate columns.
    :rtype: pd.DataFrame

    .. code-block:: python3

        import pm4py

        dataframe = pm4py.insert_case_arrival_finish_rate(
            dataframe,
            activity_key='concept:name',
            timestamp_key='time:timestamp',
            case_id_key='case:concept:name',
            start_timestamp_key='time:timestamp'
        )
    """
    __event_log_deprecation_warning(log)

    properties = get_properties(
        log,
        activity_key=activity_key,
        case_id_key=case_id_key,
        timestamp_key=timestamp_key,
    )

    from pm4py.objects.conversion.log import converter as log_converter

    log_df = log_converter.apply(
        log,
        variant=log_converter.Variants.TO_DATA_FRAME,
        parameters=properties,
    )

    return pandas_utils.insert_case_arrival_finish_rate(
        log_df,
        case_id_column=case_id_key,
        timestamp_column=timestamp_key,
        start_timestamp_column=start_timestamp_key,
        arrival_rate_column=arrival_rate_column,
        finish_rate_column=finish_rate_column,
    )


def check_is_workflow_net(net: PetriNet) -> bool:
    """
    Checks if the input Petri net satisfies the WF-net (Workflow net) conditions:
    1. It has a unique source place.
    2. It has a unique sink place.
    3. Every node is on a path from the source to the sink.

    :param net: The Petri net to check.
    :return: True if the Petri net is a WF-net, False otherwise.
    :rtype: bool

    .. code-block:: python3

        import pm4py

        net = pm4py.read_pnml('model.pnml')
        is_wfnet = pm4py.check_is_workflow_net(net)
    """
    from pm4py.algo.analysis.workflow_net import algorithm

    return algorithm.apply(net)


def maximal_decomposition(
    net: PetriNet, im: Marking, fm: Marking
) -> List[Tuple[PetriNet, Marking, Marking]]:
    """
    Calculates the maximal decomposition of an accepting Petri net into its maximal components.

    :param net: The Petri net to decompose.
    :param im: The initial marking of the Petri net.
    :param fm: The final marking of the Petri net.
    :return: A list of tuples, each containing a subnet Petri net, its initial marking, and its final marking.
    :rtype: List[Tuple[PetriNet, ~pm4py.objects.petri_net.obj.Marking, ~pm4py.objects.petri_net.obj.Marking]]

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        list_nets = pm4py.maximal_decomposition(net, im, fm)
        for subnet, subim, subfm in list_nets:
            pm4py.view_petri_net(subnet, subim, subfm, format='svg')
    """
    from pm4py.objects.petri_net.utils.decomposition import decompose

    return decompose(net, im, fm)


def simplicity_petri_net(
    net: PetriNet,
    im: Marking,
    fm: Marking,
    variant: Optional[str] = "arc_degree",
) -> float:
    """
    Computes the simplicity metric for a given Petri net model.

    Three available approaches are supported:

    - **Arc Degree Simplicity**: Described in the paper "ProDiGen: Mining complete, precise and minimal structure process models with a genetic algorithm." by Vázquez-Barreiros, Borja, Manuel Mucientes, and Manuel Lama. Information Sciences, 294 (2015): 315-333.
    - **Extended Cardoso Metric**: Described in the paper "Complexity Metrics for Workflow Nets" by Lassen, Kristian Bisgaard, and Wil MP van der Aalst.
    - **Extended Cyclomatic Metric**: Also described in the paper "Complexity Metrics for Workflow Nets" by Lassen, Kristian Bisgaard, and Wil MP van der Aalst.

    :param net: The Petri net for which to compute simplicity.
    :param im: The initial marking of the Petri net.
    :param fm: The final marking of the Petri net.
    :param variant: The simplicity metric variant to use ('arc_degree', 'extended_cardoso', 'extended_cyclomatic').
    :return: The computed simplicity value.
    :rtype: float

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.discover_petri_net_inductive(
            dataframe,
            activity_key='concept:name',
            case_id_key='case:concept:name',
            timestamp_key='time:timestamp'
        )
        simplicity = pm4py.simplicity_petri_net(net, im, fm, variant='arc_degree')
    """
    if variant == "arc_degree":
        from pm4py.algo.evaluation.simplicity.variants import arc_degree

        return arc_degree.apply(net)
    elif variant == "extended_cardoso":
        from pm4py.algo.evaluation.simplicity.variants import extended_cardoso

        return extended_cardoso.apply(net)
    elif variant == "extended_cyclomatic":
        from pm4py.algo.evaluation.simplicity.variants import (
            extended_cyclomatic,
        )

        return extended_cyclomatic.apply(net, im)


def generate_marking(
    net: PetriNet,
    place_or_dct_places: Union[
        str, PetriNet.Place, Dict[str, int], Dict[PetriNet.Place, int]
    ],
) -> Marking:
    """
    Generates a marking for a given Petri net based on specified places and token counts.

    :param net: The Petri net for which to generate the marking.
    :param place_or_dct_places: Specifies the places and their token counts for the marking. It can be:

        - A single `PetriNet.Place` object, which will have one token.
        - A string representing the name of a place, which will have one token.
        - A dictionary mapping `PetriNet.Place` objects to their respective number of tokens.
        - A dictionary mapping place names (strings) to their respective number of tokens. :return: The generated ~pm4py.objects.petri_net.obj.Marking object. :rtype: ~pm4py.objects.petri_net.obj.Marking

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        marking = pm4py.generate_marking(net, {'source': 2})
    """
    dct_places = {x.name: x for x in net.places}
    if isinstance(place_or_dct_places, PetriNet.Place):
        # A single Place object is specified for the marking
        return Marking({place_or_dct_places: 1})
    elif isinstance(place_or_dct_places, str):
        # The name of a place is specified for the marking
        return Marking({dct_places[place_or_dct_places]: 1})
    elif isinstance(place_or_dct_places, dict):
        dct_keys = list(place_or_dct_places)
        if dct_keys:
            if isinstance(dct_keys[0], PetriNet.Place):
                # A dictionary mapping Place objects to token counts is
                # specified
                return Marking(place_or_dct_places)
            elif isinstance(dct_keys[0], str):
                # A dictionary mapping place names to token counts is specified
                return Marking(
                    {dct_places[x]: y for x, y in place_or_dct_places.items()}
                )


def reduce_petri_net_invisibles(net: PetriNet) -> PetriNet:
    """
    Reduces the number of invisible transitions in the provided Petri net.

    :param net: The Petri net to be reduced.
    :return: The reduced Petri net with fewer invisible transitions.
    :rtype: PetriNet

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        net = pm4py.reduce_petri_net_invisibles(net)
    """
    from pm4py.objects.petri_net.utils import reduction

    return reduction.apply_simple_reduction(net)


def reduce_petri_net_implicit_places(
    net: PetriNet, im: Marking, fm: Marking
) -> Tuple[PetriNet, Marking, Marking]:
    """
    Reduces the number of implicit places in the provided Petri net.

    :param net: The Petri net to be reduced.
    :param im: The initial marking of the Petri net.
    :param fm: The final marking of the Petri net.
    :return: A tuple containing the reduced Petri net, its initial marking, and its final marking.
    :rtype: Tuple[PetriNet, ~pm4py.objects.petri_net.obj.Marking, ~pm4py.objects.petri_net.obj.Marking]

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        net, im, fm = pm4py.reduce_petri_net_implicit_places(net, im, fm)
    """
    from pm4py.objects.petri_net.utils import murata

    return murata.apply_reduction(net, im, fm)


def get_enabled_transitions(
    net: PetriNet, marking: Marking
) -> Set[PetriNet.Transition]:
    """
    Retrieves the set of transitions that are enabled in a given marking of a Petri net.

    :param net: The Petri net.
    :param marking: The current marking of the Petri net.
    :return: A set of transitions that are enabled in the provided marking.
    :rtype: Set[PetriNet.Transition]

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('tests/input_data/running-example.pnml')
        # Gets the transitions enabled in the initial marking
        enabled_transitions = pm4py.get_enabled_transitions(net, im)
    """
    from pm4py.objects.petri_net import semantics

    return semantics.enabled_transitions(net, marking)


def get_activity_labels(*args) -> List[str]:
    """Gets the activity labels from the specified event log / process model.

    Returns
    ---------------
    activities : list
        Activity labels

    """
    import pm4py

    if isinstance(args[0], EventLog):
        labels = set(y["concept:name"] for x in args[0] for y in x)
    elif isinstance(args[0], pd.DataFrame):
        labels = set(args[0]["concept:name"].unique())
    else:
        net, im, fm = pm4py.convert_to_petri_net(*args)
        labels = {x.label for x in net.transitions if x.label is not None}
    return sorted(list(labels))


def replace_activity_labels(string_dictio, *args):
    """
    Replace the activity labels in the specified process model.

    The first argument is the dictionary, i.e., {"pay": "pay
    compensation", "reject": "reject request"} The rest is the
    specification of the process model
    """
    from pm4py.objects.powl.obj import POWL
    from pm4py.objects.bpmn.obj import BPMN

    if isinstance(args[0], POWL):
        from pm4py.objects.powl.utils import label_replacing
        return label_replacing.apply(args[0], string_dictio)
    elif isinstance(args[0], ProcessTree):
        from pm4py.objects.process_tree.utils import label_replacing
        return label_replacing.apply(args[0], string_dictio)
    elif isinstance(args[0], PetriNet):
        from pm4py.objects.petri_net.utils import label_replacing
        return label_replacing.apply(args[0], args[1], args[2], string_dictio)
    elif isinstance(args[0], BPMN):
        from pm4py.objects.bpmn.util import label_replacing
        return label_replacing.apply(args[0], string_dictio)
    else:
        raise Exception("unsupported.")


def __extract_models(*args) -> List[Any]:
    if len(args) < 2:
        raise Exception("Insufficient arguments provided.")

    counter = 0
    lst_models = []

    import pm4py
    for i in range(2):
        if type(args[counter]) is PetriNet:
            net, im, fm = args[counter:counter + 3]
            lst_models.append([net, im, fm])
            counter += 3
        elif isinstance(args[counter], dict):
            dfg, sa, ea = args[counter:counter + 3]
            net, im, fm = pm4py.convert_to_petri_net(dfg, sa, ea)
            lst_models.append([net, im, fm])
            counter += 3
        else:
            obj = args[counter]
            lst_models.append([obj])
            counter += 1

    return lst_models


def behavioral_similarity(*args) -> float:
    """
    Computes the behavioral similarity (footprints-based) between two process models.

    Examples:

    * pm4py.behavioral_similarity(petri_net, im, fm, process_tree)
    * pm4py.behavioral_similarity(bpmn1, bpmn2)
    * pm4py.behavioral_similarity(process_tree, powl)

    Returns
    --------------
    similarity
        Footprints-based behavioral similarity

    """
    lst_models = __extract_models(*args)

    import pm4py
    footprints = []
    for i in range(len(lst_models)):
        x = lst_models[i]
        if not (isinstance(x[0], PetriNet) or isinstance(x[0], ProcessTree)):
            x = [pm4py.convert_to_powl(*x)]

        footprints.append(pm4py.discover_footprints(*x))

    footprints1, footprints2 = footprints

    sequence_union = footprints1["sequence"].union(footprints2["sequence"])
    sequence_intersection = footprints1["sequence"].intersection(footprints2["sequence"])

    parallel_union = footprints1["parallel"].union(footprints2["parallel"])
    parallel_intersection = footprints1["parallel"].intersection(footprints2["parallel"])

    denominator = len(sequence_union) + len(parallel_union)

    if denominator == 0:
        return 0
    else:
        return (len(sequence_intersection) + len(parallel_intersection)) / denominator


def structural_similarity(*args) -> float:
    """
    Computes the structural similarity between two semi-block-structured process models,
    following an approach similar to:

    Yan, Z., Dijkman, R., & Grefen, P. (2012). Fast business process similarity search.
    Distributed and Parallel Databases, 30(2), 105–144.
    (https://doi.org/10.1007/s10619-012-7089-z)

    Examples:

    * pm4py.structural_similarity(petri_net, im, fm, process_tree)
    * pm4py.structural_similarity(bpmn1, bpmn2)
    * pm4py.structural_similarity(process_tree, powl)

    Returns
    --------------
    similarity
        Structural similarity

    """
    lst_models = __extract_models(*args)

    import pm4py
    i = 0
    while i < len(lst_models):
        lst_models[i] = pm4py.convert_to_process_tree(pm4py.convert_to_powl(*lst_models[i]))
        i = i + 1

    from pm4py.objects.process_tree.utils import struct_similarity
    return struct_similarity.structural_similarity(lst_models[0], lst_models[1])


def embeddings_similarity(*args) -> float:
    """
    Computes the embeddings similarity between two process models,
    following the approach described in:

    Colonna, Juan G., et al. "Process mining embeddings: Learning vector representations for Petri nets."
    Intelligent Systems with Applications 23 (2024): 200423.

    Examples:

    * pm4py.embeddings_similarity(petri_net, im, fm, process_tree)
    * pm4py.embeddings_similarity(bpmn1, bpmn2)
    * pm4py.embeddings_similarity(process_tree, powl)

    Returns
    --------------
    similarity
        Structural similarity

    """
    lst_models = __extract_models(*args)

    import pm4py
    i = 0
    while i < len(lst_models):
        lst_models[i] = pm4py.convert_to_petri_net(*lst_models[i])
        i = i + 1

    from pm4py.objects.petri_net.utils import embeddings_similarity
    return embeddings_similarity.apply(lst_models[0][0], lst_models[1][0])


def label_sets_similarity(*args, threshold=0.75) -> float:
    """
    Computes the label sets similarity between two process models.

    Examples:

    * pm4py.labels_similarity(petri_net, im, fm, process_tree)
    * pm4py.labels_similarity(bpmn1, bpmn2)
    * pm4py.labels_similarity(process_tree, powl)

    Returns
    --------------
    similarity
        Label sets similarity

    """
    lst_models = __extract_models(*args)
    labels = []
    i = 0
    while i < len(lst_models):
        labels.append(get_activity_labels(*lst_models[i]))
        i = i + 1

    return ls_util.label_sets_similarity(labels[0], labels[1], threshold=threshold)


def map_labels_from_second_model(*args, threshold=0.75):
    """
    Maps the labels from the second process model into the first.

    Example usages:

    * pm4py.map_labels_from_second_model(net, im, fm, process_tree)
    * pm4py.map_labels_from_second_model(process_tree, net, im, fm)
    * pm4py.map_labels_from_second_model(powl1, powl2)
    """
    lst_models = __extract_models(*args)
    labels = []
    i = 0
    while i < len(lst_models):
        labels.append(get_activity_labels(*lst_models[i]))
        i = i + 1

    label_mapping = ls_util.map_labels(labels[0], labels[1], threshold=threshold)
    return replace_activity_labels(label_mapping, *lst_models[0])


# ============================================================================
# COMPLEXITY METRICS
# ============================================================================

import math
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ComplexityMetricsResult:
    """Comprehensive complexity metrics for a POWL model."""

    # Basic counts
    node_count: int = 0
    activity_count: int = 0
    operator_count: int = 0

    # McCabe-style metrics
    cyclomatic_complexity: float = 0.0
    decision_points: int = 0

    # Control-flow metrics
    control_flow_complexity: float = 0.0
    nesting_depth: int = 0
    max_sequential_depth: int = 0

    # Entropy/diversity metrics
    operator_diversity: float = 0.0  # Shannon entropy
    activity_diversity: float = 0.0  # Shannon entropy of activities

    # Structural metrics
    connectance: float = 0.0  # actual_edges / possible_edges
    density: float = 0.0  # actual_edges / (node_count * (node_count - 1))

    # Block-structuredness
    structuredness: float = 0.0  # % of model that is block-structured
    is_block_structured: bool = True

    # Operator counts
    xor_count: int = 0
    loop_count: int = 0
    partial_order_count: int = 0
    sequence_count: int = 0

    # Edge metrics
    total_edges: int = 0
    possible_edges: int = 0

    # Metadata
    timestamp: Optional[str] = None
    model_hash: Optional[str] = None


def calculate_complexity_metrics(powl_model, include_timestamp: bool = True) -> ComplexityMetricsResult:
    """
    Calculate comprehensive complexity metrics for a POWL model.

    Parameters
    ----------
    powl_model : POWL
        The POWL model to analyze.
    include_timestamp : bool
        Whether to include timestamp in results.

    Returns
    -------
    ComplexityMetricsResult
        Comprehensive complexity metrics.

    Examples
    --------
    >>> from pm4py.objects.powl.parser import parse_powl_model_string
    >>> from pm4py.analysis import calculate_complexity_metrics
    >>> model = parse_powl_model_string("X(A, B)")
    >>> metrics = calculate_complexity_metrics(model)
    >>> print(f"Cyclomatic complexity: {metrics.cyclomatic_complexity}")
    """
    import hashlib
    from datetime import datetime

    # Capture SilentTransaction at function scope for nested functions
    silent_trans_cls = SilentTransition

    result = ComplexityMetricsResult()

    # Basic counts
    nodes, activities, operators = _count_nodes(powl_model)
    result.node_count = nodes
    result.activity_count = activities
    result.operator_count = operators

    # Operator-specific counts
    op_counts = _count_operators(powl_model)
    result.xor_count = op_counts.get("XOR", 0)
    result.loop_count = op_counts.get("LOOP", 0)
    result.partial_order_count = op_counts.get("PO", 0)
    result.sequence_count = op_counts.get("SEQUENCE", 0)

    # Cyclomatic complexity (McCabe)
    result.cyclomatic_complexity = _calculate_cyclomatic_complexity(powl_model)
    result.decision_points = result.xor_count + result.loop_count

    # Control-flow complexity
    result.control_flow_complexity = _calculate_control_flow_complexity(powl_model)

    # Nesting depth
    result.nesting_depth = _calculate_nesting_depth(powl_model)
    result.max_sequential_depth = _calculate_max_sequential_depth(powl_model)

    # Entropy/diversity
    result.operator_diversity = _calculate_operator_diversity(powl_model)
    result.activity_diversity = _calculate_activity_diversity(powl_model)

    # Edge metrics
    result.total_edges = _count_edges(powl_model)
    result.possible_edges = _calculate_possible_edges(powl_model)
    if result.possible_edges > 0:
        result.connectance = result.total_edges / result.possible_edges
    if result.node_count > 1:
        result.density = result.total_edges / (result.node_count * (result.node_count - 1))

    # Block-structuredness
    result.structuredness, result.is_block_structured = _calculate_structuredness(powl_model)

    # Metadata
    if include_timestamp:
        result.timestamp = datetime.now().isoformat()

    # Create model hash for comparison
    model_str = str(powl_model)
    result.model_hash = hashlib.md5(model_str.encode()).hexdigest()[:8]

    return result


def compare_complexity(metrics1: ComplexityMetricsResult, metrics2: ComplexityMetricsResult) -> Dict[str, Any]:
    """
    Compare two complexity metrics results.

    Returns dict with differences and ratios.

    Parameters
    ----------
    metrics1, metrics2 : ComplexityMetricsResult
        Metrics to compare.

    Returns
    -------
    dict
        Comparison results with deltas and ratios.
    """
    return {
        "node_count_delta": metrics2.node_count - metrics1.node_count,
        "cyclomatic_complexity_delta": metrics2.cyclomatic_complexity - metrics1.cyclomatic_complexity,
        "control_flow_complexity_delta": metrics2.control_flow_complexity - metrics1.control_flow_complexity,
        "nesting_depth_delta": metrics2.nesting_depth - metrics1.nesting_depth,
        "structuredness_delta": metrics2.structuredness - metrics1.structuredness,
        "simpler": metrics2.cyclomatic_complexity < metrics1.cyclomatic_complexity,
        "more_structured": metrics2.structuredness > metrics1.structuredness,
    }


# ============================================================================
# COMPLEXITY METRICS HELPER FUNCTIONS
# ============================================================================

def _count_nodes(powl) -> tuple:
    """Count total nodes, activities, and operators in POWL model."""
    # Import inside function to avoid circular imports
    try:
        from pm4py.objects.powl.obj import Transition, SilentTransition, OperatorPOWL, StrictPartialOrder
    except ImportError:
        from pm4py.objects.powl.obj import Transition, OperatorPOWL, StrictPartialOrder
        SilentTransition = None

    # Capture at function scope for nested function
    silent_trans_cls = SilentTransition

    total = 0
    activities = 0
    operators = 0

    def _visit(node):
        nonlocal total, activities, operators
        total += 1
        if isinstance(node, OperatorPOWL):
            operators += 1
            for child in node.children:
                _visit(child)
        elif isinstance(node, StrictPartialOrder):
            operators += 1
            for child in node.children:
                _visit(child)
        elif isinstance(node, Transition):
            if silent_trans_cls is not None and not isinstance(node, silent_trans_cls):
                if node.label:
                    activities += 1
            elif node.label:
                activities += 1

    _visit(powl)
    return total, activities, operators


def _count_operators(powl) -> Dict[str, int]:
    """Count operators by type."""
    from pm4py.objects.powl.obj import OperatorPOWL, StrictPartialOrder
    from pm4py.objects.process_tree.obj import Operator

    counts = {"XOR": 0, "LOOP": 0, "PO": 0, "SEQUENCE": 0}

    def _visit(node):
        if isinstance(node, OperatorPOWL):
            # Handle both enum and string values
            op = node.operator
            if isinstance(op, str):
                # String values from parser: "X", "*", "+", "->", "O"
                if op == "X":
                    counts["XOR"] += 1
                elif op == "*":
                    counts["LOOP"] += 1
                elif op == "+":
                    counts["SEQUENCE"] += 1  # PARALLEL maps to SEQUENCE for counting
            else:
                # Operator enum
                if op == Operator.XOR:
                    counts["XOR"] += 1
                elif op == Operator.LOOP:
                    counts["LOOP"] += 1
                elif op == Operator.PARALLEL:
                    counts["SEQUENCE"] += 1
            for child in node.children:
                _visit(child)
        elif isinstance(node, StrictPartialOrder):
            counts["PO"] += 1
            for child in node.children:
                _visit(child)

    _visit(powl)
    return counts


def _calculate_cyclomatic_complexity(powl) -> float:
    """
    Calculate McCabe cyclomatic complexity.

    For process models: V(G) = E - N + 2P
    where E = edges, N = nodes, P = connected components (usually 1)

    Simplified: V(G) = number of decision points + 1
    """
    op_counts = _count_operators(powl)
    # Each XOR and LOOP contributes to complexity
    decision_points = op_counts.get("XOR", 0) + op_counts.get("LOOP", 0)
    return float(decision_points + 1)


def _calculate_control_flow_complexity(powl) -> float:
    """
    Calculate control-flow complexity based on nesting and branching.

    CFC = sum(decision_points * (nesting_depth + 1)) for all decisions
    """
    from pm4py.objects.powl.obj import OperatorPOWL, StrictPartialOrder
    from pm4py.objects.process_tree.obj import Operator

    cfc = 0.0

    def _visit(node, depth=0):
        nonlocal cfc
        if isinstance(node, OperatorPOWL):
            # Handle both enum and string values
            op = node.operator
            if isinstance(op, str):
                # String values from parser: "X", "*", "+", "->", "O"
                if op == "X":
                    # XOR contributes based on branching factor and depth
                    branching = len(node.children)
                    cfc += branching * (depth + 1)
                elif op == "*":
                    # LOOP contributes complexity
                    cfc += 2 * (depth + 1)
            else:
                # Operator enum
                if op == Operator.XOR:
                    branching = len(node.children)
                    cfc += branching * (depth + 1)
                elif op == Operator.LOOP:
                    cfc += 2 * (depth + 1)

            for child in node.children:
                _visit(child, depth + 1)
        elif isinstance(node, StrictPartialOrder):
            # Partial order complexity based on number of children
            cfc += len(node.children) * 0.5
            for child in node.children:
                _visit(child, depth)

    _visit(powl)
    return cfc


def _calculate_nesting_depth(powl) -> int:
    """Calculate maximum nesting depth."""
    from pm4py.objects.powl.obj import OperatorPOWL, StrictPartialOrder

    def _visit(node, depth=0):
        if isinstance(node, OperatorPOWL):
            child_depths = [_visit(child, depth + 1) for child in node.children]
            return max(child_depths) if child_depths else depth + 1
        elif isinstance(node, StrictPartialOrder):
            child_depths = [_visit(child, depth) for child in node.children]
            return max(child_depths) if child_depths else depth
        return depth

    return _visit(powl)


def _calculate_max_sequential_depth(powl) -> int:
    """Calculate maximum sequential chain length."""
    from pm4py.objects.powl.obj import StrictPartialOrder

    max_depth = 0

    def _visit(node, current_depth=0):
        nonlocal max_depth
        if isinstance(node, StrictPartialOrder):
            # Check if this PO represents a sequence
            order = node.order
            if order:
                # Calculate longest path through the order
                path_length = _longest_path_in_order(order, node.children)
                max_depth = max(max_depth, current_depth + path_length)

            for child in node.children:
                _visit(child, current_depth)

    _visit(powl)
    return max_depth


def _longest_path_in_order(order, children) -> int:
    """Calculate longest path in a partial order."""
    # Simplified: count children for now
    # A full implementation would do topological sort
    return len(children) if children else 0


def _calculate_operator_diversity(powl) -> float:
    """
    Calculate Shannon entropy of operator distribution.

    Higher values = more diverse mix of operators.
    """
    op_counts = _count_operators(powl)
    total = sum(op_counts.values())

    if total == 0:
        return 0.0

    entropy = 0.0
    for count in op_counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    return entropy


def _calculate_activity_diversity(powl) -> float:
    """
    Calculate Shannon entropy of activity distribution.

    Higher values = more diverse activities (less repetition).
    """
    # Import inside function to avoid circular imports
    try:
        from pm4py.objects.powl.obj import Transition, SilentTransaction, OperatorPOWL, StrictPartialOrder
    except ImportError:
        from pm4py.objects.powl.obj import Transition, OperatorPOWL, StrictPartialOrder
        SilentTransaction = None

    # Capture at function scope for nested function
    silent_trans_cls = SilentTransaction

    activity_counts = {}
    total_activities = 0

    def _visit(node):
        nonlocal total_activities
        if isinstance(node, Transition):
            if silent_trans_cls is not None and not isinstance(node, silent_trans_cls):
                if node.label:
                    activity_counts[node.label] = activity_counts.get(node.label, 0) + 1
                    total_activities += 1
            elif node.label:
                activity_counts[node.label] = activity_counts.get(node.label, 0) + 1
                total_activities += 1
        elif isinstance(node, (OperatorPOWL, StrictPartialOrder)):
            for child in node.children:
                _visit(child)

    _visit(powl)

    if total_activities == 0:
        return 0.0

    entropy = 0.0
    for count in activity_counts.values():
        p = count / total_activities
        entropy -= p * math.log2(p)

    return entropy


def _count_edges(powl) -> int:
    """Count total edges in the model."""
    from pm4py.objects.powl.obj import StrictPartialOrder

    edges = 0

    def _visit(node):
        nonlocal edges
        if isinstance(node, StrictPartialOrder):
            # Count order relations
            if node.order:
                edges += len(node.order.edges)
            for child in node.children:
                _visit(child)
        # Operator children contribute edges
        elif hasattr(node, 'children'):
            for child in node.children:
                edges += 1
                _visit(child)

    _visit(powl)
    return edges


def _calculate_possible_edges(powl) -> int:
    """
    Calculate maximum possible edges in a fully connected model.

    For n nodes, maximum directed edges = n * (n - 1)
    """
    node_count, _, _ = _count_nodes(powl)
    if node_count <= 1:
        return 0
    return node_count * (node_count - 1)


def _calculate_structuredness(powl) -> tuple:
    """
    Calculate how much of the model is block-structured.

    Returns (structuredness_ratio, is_fully_block_structured).

    Block-structured means:
    - Single entry, single exit for each component
    - Proper nesting (no overlapping choices)
    - No cross-edge connections between branches
    """
    # Import inside function to avoid circular imports
    try:
        from pm4py.objects.powl.obj import DecisionGraph
    except ImportError:
        DecisionGraph = None

    # Check if model uses DecisionGraph (non-block-structured)
    if DecisionGraph is not None and isinstance(powl, DecisionGraph):
        return (0.5, False)  # DecisionGraph indicates non-block structure

    # For pure POWL without DecisionGraph, check for overlapping choices
    # This is a simplified check - a full implementation would do graph analysis
    total_nodes, _, operator_count = _count_nodes(powl)

    if operator_count == 0:
        # Single activity - fully structured
        return (1.0, True)

    # Count XOR operators as potential non-block points
    op_counts = _count_operators(powl)
    xor_count = op_counts.get("XOR", 0)

    if xor_count == 0:
        # No XOR choices - likely block-structured
        return (1.0, True)

    # For each XOR, verify it's properly nested
    # This is simplified - full implementation requires graph reachability
    # Assume 80% structured for models with XORs
    structuredness = max(0.5, 1.0 - (xor_count * 0.1))

    return (structuredness, structuredness >= 0.9)
