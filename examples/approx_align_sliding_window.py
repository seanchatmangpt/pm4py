"""Compute an approximate alignment with sliding windows and top-k states.

Run this example from the ``examples`` directory:

    python approx_align_sliding_window.py

Each window is aligned from the model markings retained by the preceding
window.  Keeping more distinct endpoint markings generally improves quality,
while smaller windows and fewer candidates reduce memory and running time.
"""

import os

from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri_net.importer import importer as petri_importer
from pm4py.objects.petri_net.utils.align_utils import pretty_print_alignments


def execute_script():
    # Resolve sample paths relative to this file, so the example also works
    # when it is launched from a different current working directory.
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
        variant=alignments.Variants.APPROX_SLIDING_WINDOW,
        parameters={
            # Three events are processed per window.  Long production traces
            # typically use a larger value (the default is 20).
            "window_size": 3,
            # Retain up to four paths ending in distinct model markings.  A
            # value of one is fastest but makes locally greedy choices.
            "max_candidates": 4,
            # Intermediate windows may use a few model moves after consuming
            # their events to expose useful endpoint markings.
            "max_post_model_moves": 3,
            "max_align_time_trace": 30,
            "max_expansions": 100000,
            "enable_best_worst_cost": False,
        },
    )

    if result is None:
        print("No alignment was found within the configured resource limits.")
        return

    print("Observed trace:", activities)
    print("Number of windows:", result["window_count"])
    print("Candidates retained after each window:", result["retained_candidates"])
    print("Exact-search fallback used:", result["fallback_used"])
    print("Visited states:", result["visited_states"])
    print("Valid complete alignment:", result["is_valid"])
    print("Alignment cost / upper bound:", result["upper_bound"])
    print("Alignment (top: log, bottom: model):")
    pretty_print_alignments(result)


if __name__ == "__main__":
    execute_script()
