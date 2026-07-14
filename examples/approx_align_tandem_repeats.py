"""Approximate a long, repetitive trace by compressing tandem repeats.

Run this example from the ``examples`` directory:

    python approx_align_tandem_repeats.py

The model below contains the loop A -> B.  The observed trace executes that
loop six times before taking C to the final marking.  The tandem-repeat
variant aligns only the first and last copies of the repeated block and then
expands the executable model loop in the returned alignment.
"""

from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
from pm4py.objects.log.obj import Event, Trace
from pm4py.objects.petri_net.obj import Marking, PetriNet
from pm4py.objects.petri_net.utils import petri_utils
from pm4py.objects.petri_net.utils.align_utils import pretty_print_alignments


def create_loop_model():
    """Create an accepting Petri net for (A, B)* followed by C."""
    net = PetriNet("tandem-repeat example")
    start = PetriNet.Place("start")
    between_a_and_b = PetriNet.Place("between A and B")
    end = PetriNet.Place("end")
    net.places.update({start, between_a_and_b, end})

    transition_a = PetriNet.Transition("do A", "A")
    transition_b = PetriNet.Transition("do B", "B")
    transition_c = PetriNet.Transition("finish with C", "C")
    net.transitions.update({transition_a, transition_b, transition_c})

    petri_utils.add_arc_from_to(start, transition_a, net)
    petri_utils.add_arc_from_to(transition_a, between_a_and_b, net)
    petri_utils.add_arc_from_to(between_a_and_b, transition_b, net)
    petri_utils.add_arc_from_to(transition_b, start, net)
    petri_utils.add_arc_from_to(start, transition_c, net)
    petri_utils.add_arc_from_to(transition_c, end, net)

    return net, Marking({start: 1}), Marking({end: 1})


def execute_script():
    net, initial_marking, final_marking = create_loop_model()

    # Six consecutive copies of (A, B) form one tandem repeat.  The algorithm
    # keeps two copies during its search, so it aligns A, B, A, B, C instead of
    # all thirteen events.  At least three copies are needed for compression.
    activities = ["A", "B"] * 6 + ["C"]
    trace = Trace([Event({"concept:name": activity}) for activity in activities])

    result = alignments.apply(
        trace,
        net,
        initial_marking,
        final_marking,
        variant=alignments.Variants.APPROX_TANDEM_REPEATS,
        parameters={
            # Skip the optional best-worst-cost calculation in this example;
            # it is only needed when normalized alignment fitness is required.
            "enable_best_worst_cost": False,
            # Bound the underlying state-space search for production use.
            "max_align_time_trace": 30,
            "max_expansions": 100000,
        },
    )

    if result is None:
        print("No alignment was found within the configured resource limits.")
        return

    print("Observed trace:", activities)
    print("Original trace length:", result["original_trace_length"])
    print("Reduced trace length:", result["reduced_trace_length"])
    print("Detected tandem repeats:", result["tandem_repeats"])
    print("Temporarily removed events:", result["removed_events"])
    print("Expanded model-loop copies:", result["model_loop_expansions"])
    print("Valid complete alignment:", result["is_valid"])
    print("Alignment cost / upper bound:", result["upper_bound"])
    print("Alignment (top: log, bottom: model):")
    pretty_print_alignments(result)


if __name__ == "__main__":
    execute_script()
