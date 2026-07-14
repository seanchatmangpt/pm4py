"""Compute a sequential fixed-horizon approximate alignment.

Run this example from the ``examples`` directory:

    python approx_align_fixed_horizon.py

At every iteration the algorithm searches an executable prefix of at most
``horizon`` product-net moves, estimates the remaining suffix with an integer
marking equation, and commits the best prefix.  This bounds the amount of the
synchronous product considered at once.
"""

import os

from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri_net.importer import importer as petri_importer
from pm4py.objects.petri_net.utils.align_utils import pretty_print_alignments


def execute_script():
    examples_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(examples_dir, "..", "tests", "input_data")
    log = xes_importer.apply(os.path.join(data_dir, "running-example.xes"))
    net, initial_marking, final_marking = petri_importer.apply(
        os.path.join(data_dir, "running-example.pnml")
    )

    trace = log[0]
    activities = [event["concept:name"] for event in trace]

    result = alignments.apply(
        trace,
        net,
        initial_marking,
        final_marking,
        variant=alignments.Variants.APPROX_FIXED_HORIZON,
        parameters={
            # Search at most four synchronous-product moves before deciding
            # which prefix to commit.
            "horizon": 4,
            # Require a committed prefix to consume at least one log event.
            "min_progress": 1,
            # The algorithm may enlarge its horizon when the tail estimate
            # indicates that a short commitment would be poor.
            "max_horizon": 10,
            "max_prefix_states": 20000,
            "max_iterations": 100,
            "max_align_time_trace": 30,
            "enable_best_worst_cost": False,
        },
    )

    if result is None:
        print("No alignment was found within the configured resource limits.")
        return

    print("Observed trace:", activities)
    print("Initial horizon:", result["horizon"])
    print("Horizons used for committed prefixes:", result["committed_horizons"])
    print("Integer tail problems solved:", result["lp_solved"])
    print("Exact-search fallback used:", result["fallback_used"])
    if result["fallback_reason"] is not None:
        # For example, this can say ``no_lp_solver`` when no supported LP/ILP
        # backend is installed.  The fallback still returns a valid result.
        print("Fallback reason:", result["fallback_reason"])
    print("Valid complete alignment:", result["is_valid"])
    print("Alignment cost / upper bound:", result["upper_bound"])
    print("Alignment (top: log, bottom: model):")
    pretty_print_alignments(result)


if __name__ == "__main__":
    execute_script()
