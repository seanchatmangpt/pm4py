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


from collections import Counter
import uuid
from pm4py.objects.ocpn.obj import OCMarking, OCPetriNet
from typing import Dict, Any

from pm4py.objects.petri_net.obj import PetriNet


def create(ocpn: Dict[str, Any]) -> OCPetriNet:
    """
    Creates an Object-centric Petri net object from its dictionary representation
    specified in pm4py.algo.discovery.ocel.ocpn.variants.classic.
    Only considers the properties `activities`, `petri_nets`, and `double_arcs_on_activity`.
    All other information is ignored.

    Parameters
    -----------------
    ocpn
        Dictionary containing the properties of the Object-centric Petri net

    Returns
    ----------------
    OCPetriNet
        Object-centric Petri net object
    """
    activities = ocpn["activities"]
    petri_nets = ocpn["petri_nets"]
    double_arcs_on_activity = ocpn["double_arcs_on_activity"]

    places = dict()
    unlabeled_transitions = dict()
    arcs = []
    initial_marking = OCMarking()
    final_marking = OCMarking()

    # Labeled transitions
    labeled_transitions = {label: OCPetriNet.Transition(label=label, name=str(uuid.uuid4())) for label in activities}

    for ot, net in petri_nets.items():
        pn, im, fm = net

        # transitions
        for t in pn.transitions:
            if not t.label:
                # labeled transitions are already in labeled_transitions
                name = f"{ot}_{t.name}" # make name unique
                unlabeled_transitions[name] = OCPetriNet.Transition(name=name)

        # places 
        for p in pn.places:
            name = f"{ot}_{p.name}" # make name unique
            places[name] = OCPetriNet.Place(name=name, object_type=ot)

        # arcs
        for arc in pn.arcs:
            is_double = False
            if isinstance(arc.source, PetriNet.Transition):
                if arc.source.label:
                    source = labeled_transitions[arc.source.label]
                    is_double = double_arcs_on_activity[ot][arc.source.label]
                else:
                    source = unlabeled_transitions[f"{ot}_{arc.source.name}"]
                target = places[f"{ot}_{arc.target.name}"]
            elif isinstance(arc.source, PetriNet.Place):
                source = places[f"{ot}_{arc.source.name}"]
                if arc.target.label:
                    target = labeled_transitions[arc.target.label]
                    is_double = double_arcs_on_activity[ot][arc.target.label]
                else:
                    target = unlabeled_transitions[f"{ot}_{arc.target.name}"]
            else:
                raise ValueError("Unknown arc source type")

            # check for double arc

            a = OCPetriNet.Arc(source=source, target=target, object_type=ot, is_variable=is_double)
            arcs.append(a)
            source.add_out_arc(a)
            target.add_in_arc(a)

        # markings
        for p in im:
            initial_marking += OCMarking({places[f"{ot}_{p.name}"]: Counter([f"{ot}_{i}" for i in range(im[p])])})
        for p in fm:
            final_marking += OCMarking({places[f"{ot}_{p.name}"]: Counter([f"{ot}_{i}" for i in range(fm[p])])})

    # create the OCPetriNet object
    ocpn_obj = OCPetriNet(
        places = set(places.values()),
        transitions = set(labeled_transitions.values()) | set(unlabeled_transitions.values()),
        arcs = set(arcs),
        initial_marking=initial_marking,
        final_marking=final_marking,
    )
    return ocpn_obj