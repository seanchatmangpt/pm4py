"""Approximate log alignments using subset selection and edit distance.

Run this example from the ``examples`` directory:

    python approx_align_subset_edit_distance.py

Only representative trace variants are aligned through the Petri-net state
space.  Every other variant is mapped to its nearest representative with
insertion/deletion edit distance.  The result includes a concrete executable
alignment as well as lower and upper fitness bounds for every trace.
"""

import os

from pm4py.algo.conformance.alignments.edit_distance import (
    algorithm as edit_distance_alignments,
)
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

    summary = edit_distance_alignments.apply_approximation_with_summary(
        log,
        net,
        initial_marking,
        final_marking,
        parameters={
            # Select the two most frequent variants and align those exactly.
            # Alternatives are ``random``, ``k_medoids``, and ``simulation``.
            "selection_method": "frequency",
            "subset_size": 2,
            "max_align_time_trace": 30,
            "max_expansions": 100000,
        },
    )

    results = summary["alignments"]
    print("Traces aligned:", len(results))
    print(
        "Approximate log fitness and bounds: "
        f"{summary['log_fitness']:.3f} "
        f"[{summary['fitness_lower_bound']:.3f}, "
        f"{summary['fitness_upper_bound']:.3f}]"
    )
    print("Aggregate deviations:", summary["deviation_counts"])

    for index, (trace, result) in enumerate(zip(log, results), start=1):
        activities = [event["concept:name"] for event in trace]
        print("\nTrace", index, activities)
        print("  selected and aligned exactly:", result["selected_exact"])
        print("  representative model trace:", result["representative_variant"])
        print("  valid complete alignment:", result["is_valid"])
        print(
            "  fitness estimate and bounds: "
            f"{result['approximated_fitness']:.3f} "
            f"[{result['fitness_lower_bound']:.3f}, "
            f"{result['fitness_upper_bound']:.3f}]"
        )

    # Print one non-representative alignment, when available, to make the edit
    # distance materialization visible.  ``>>`` denotes a log or model move.
    example = next(
        (result for result in results if not result["selected_exact"]),
        results[0],
    )
    print("\nExample alignment (top: log, bottom: model):")
    pretty_print_alignments(example)


if __name__ == "__main__":
    execute_script()
