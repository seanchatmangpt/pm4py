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


def apply(net, im, fm, parameters=None):
    """
    Converts an accepting Petri net into a BPMN diagram

    Parameters
    --------------
    accepting_petri_net
        Accepting Petri net (list containing net + im + fm)
    parameters
        Parameters of the algorithm

    Returns
    --------------
    bpmn_graph
        BPMN diagram
    """
    if parameters is None:
        parameters = {}

    from pm4py.objects.bpmn.obj import BPMN
    from pm4py.objects.bpmn.util import reduction

    bpmn_graph = BPMN()

    entering_dictio = {}
    exiting_dictio = {}

    for place in net.places:
        node = BPMN.ExclusiveGateway()
        bpmn_graph.add_node(node)
        entering_dictio[place] = node
        exiting_dictio[place] = node

    for trans in net.transitions:
        if trans.label is None:
            if len(trans.in_arcs) > 1:
                node = BPMN.ParallelGateway(
                    gateway_direction=BPMN.Gateway.Direction.CONVERGING
                )
            elif len(trans.out_arcs) > 1:
                node = BPMN.ParallelGateway(
                    gateway_direction=BPMN.Gateway.Direction.DIVERGING
                )
            else:
                node = BPMN.ExclusiveGateway(
                    gateway_direction=BPMN.Gateway.Direction.UNSPECIFIED
                )
            bpmn_graph.add_node(node)
            entering_dictio[trans] = node
            exiting_dictio[trans] = node
        else:
            if len(trans.in_arcs) > 1:
                entering_node = BPMN.ParallelGateway(
                    gateway_direction=BPMN.Gateway.Direction.CONVERGING
                )
            else:
                entering_node = BPMN.ExclusiveGateway(
                    gateway_direction=BPMN.Gateway.Direction.UNSPECIFIED
                )

            if len(trans.out_arcs) > 1:
                exiting_node = BPMN.ParallelGateway(
                    gateway_direction=BPMN.Gateway.Direction.DIVERGING
                )
            else:
                exiting_node = BPMN.ExclusiveGateway(
                    gateway_direction=BPMN.Gateway.Direction.UNSPECIFIED
                )

            task = BPMN.Task(name=trans.label)
            bpmn_graph.add_node(task)

            bpmn_graph.add_flow(BPMN.SequenceFlow(entering_node, task))
            bpmn_graph.add_flow(BPMN.SequenceFlow(task, exiting_node))

            entering_dictio[trans] = entering_node
            exiting_dictio[trans] = exiting_node

    for arc in net.arcs:
        bpmn_graph.add_flow(
            BPMN.SequenceFlow(
                exiting_dictio[arc.source], entering_dictio[arc.target]
            )
        )

    start_node = BPMN.StartEvent(name="start", isInterrupting=True)
    end_node = BPMN.NormalEndEvent(name="end")
    bpmn_graph.add_node(start_node)
    bpmn_graph.add_node(end_node)
    for place in im:
        bpmn_graph.add_flow(
            BPMN.SequenceFlow(start_node, entering_dictio[place])
        )
    for place in fm:
        bpmn_graph.add_flow(BPMN.SequenceFlow(exiting_dictio[place], end_node))

    bpmn_graph = reduction.apply(bpmn_graph)

    for node in bpmn_graph.get_nodes():
        node.set_process(bpmn_graph.get_process_id())

    for edge in bpmn_graph.get_flows():
        edge.set_process(bpmn_graph.get_process_id())

    return bpmn_graph
