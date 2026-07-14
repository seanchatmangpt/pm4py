"""Align events online with the IWS proxy trie and decay mechanism.

Run this example from the ``examples`` directory:

    python approx_align_iws_streaming.py

IWS stores a finite proxy of complete model behavior in a trie.  As each event
arrives, look-ahead creates alternative alignment states; decay and a maximum
state count discard stale alternatives.  ``get()`` reports prefix alignments,
and ``finish(case_id)`` completes a case to a proxy final node.
"""

from pm4py.objects.log.obj import Event, EventLog, Trace
from pm4py.objects.petri_net.obj import Marking, PetriNet
from pm4py.objects.petri_net.utils import petri_utils
from pm4py.objects.petri_net.utils.align_utils import pretty_print_alignments
from pm4py.streaming.algo.conformance.alignments import (
    algorithm as streaming_alignments,
)


def create_sequence_model():
    """Create an accepting Petri net for the sequence A, B, C."""
    net = PetriNet("IWS example")
    places = [PetriNet.Place(f"p{index}") for index in range(4)]
    net.places.update(places)

    for index, label in enumerate(["A", "B", "C"]):
        transition = PetriNet.Transition(f"do {label}", label)
        net.transitions.add(transition)
        petri_utils.add_arc_from_to(places[index], transition, net)
        petri_utils.add_arc_from_to(transition, places[index + 1], net)

    return net, Marking({places[0]: 1}), Marking({places[-1]: 1})


def execute_script():
    net, initial_marking, final_marking = create_sequence_model()

    # The proxy log supplies complete behavior used to build the trie.  For a
    # large model it can be a representative sample; if omitted, the variant
    # simulates complete model traces instead.
    proxy_trace = Trace(
        [Event({"concept:name": activity}) for activity in ["A", "B", "C"]]
    )
    proxy_log = EventLog([proxy_trace])

    online_aligner = streaming_alignments.apply(
        net,
        initial_marking,
        final_marking,
        variant=streaming_alignments.Variants.APPROX_IWS,
        parameters={
            "proxy_log": proxy_log,
            # Look up to three trie edges ahead.  This lets the event C match
            # even when the observed stream omits B.
            "look_ahead": 3,
            # Alternatives lose one unit of decay per event.  Deviating paths
            # receive an additional discounted decay allowance.
            "decay_time": 5,
            "discount_factor": 0.8,
            "max_states": 10,
        },
    )

    # X is not in the proxy behavior, while B is missing from this case.  IWS
    # can explain those observations with a log move for X and a model move
    # for B, without waiting for the case to finish.
    case_id = "case-1"
    for activity in ["A", "X", "C"]:
        online_aligner.receive(
            {
                "case:concept:name": case_id,
                "concept:name": activity,
            }
        )
        prefix = online_aligner.get()[case_id]
        print(
            f"After {activity}: cost={prefix['standard_cost']}, "
            f"active states={prefix['active_states']}, "
            f"best decay={prefix['decay']:.2f}"
        )

    prefix = online_aligner.get()[case_id]
    print("\nCurrent prefix alignment:")
    pretty_print_alignments(prefix)

    # Explicitly close the case so any remaining model suffix is appended.
    # An event carrying ``@@complete=True`` can also trigger completion.
    complete = online_aligner.finish(case_id)
    print("Complete alignment is valid:", complete["is_valid"])
    print("Complete alignment cost / upper bound:", complete["upper_bound"])
    print("Complete alignment (top: log, bottom: model):")
    pretty_print_alignments(complete)


if __name__ == "__main__":
    execute_script()
