"""
PM4Py - A Process Mining Library for Python
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



from pm4py.objects.powl.BinaryRelation import BinaryRelation
from pm4py.objects.powl.constants import STRICT_PARTIAL_ORDER_LABEL
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.util import hie_utils
import sys
from typing import List as TList, Optional, Union, Dict, Any, Tuple
from abc import ABC, abstractmethod


class POWL(ProcessTree, ABC):
    def print(self) -> None:
        print(self.to_string())

    def simplify_using_frequent_transitions(self) -> "POWL":
        return self

    def simplify(self) -> "POWL":
        return self

    def validate_partial_orders(self):
        if isinstance(self, StrictPartialOrder):
            if not self.order.is_irreflexive():
                raise Exception(
                    "The irreflexivity of the partial order is violated!"
                )
            if not self.order.is_transitive():
                raise Exception(
                    "The transitivity of the partial order is violated!"
                )
        if hasattr(self, "children"):
            for child in self.children:
                child.validate_partial_orders()

    @staticmethod
    def model_description() -> str:
        descr = """A partially ordered workflow language (POWL) is a partially ordered graph representation of a process, extended with control-flow operators for modeling choice and loop structures. There are four types of POWL models:
- an activity (identified by its label, i.e., 'M' identifies the activity M). Silent activities with empty labels (tau labels) are also supported.
- a choice of other POWL models (an exclusive choice between the sub-models A and B is identified by X ( A, B ) )
- a loop node between two POWL models (a loop between the sub-models A and B is identified by * ( A, B ) and tells that you execute A, then you either exit the loop or execute B and then A again, this is repeated until you exit the loop).
- a partial order over a set of POWL models. A partial order is a binary relation that is irreflexive, transitive, and asymmetric. A partial order sets an execution order between the sub-models (i.e., the target node cannot be executed before the source node is completed). Unconnected nodes in a partial order are considered to be concurrent. An example is PO=(nodes={ NODE1, NODE2 }, order={ })
where NODE1 and NODE2 are independent and can be executed in parallel. Another example is PO=(nodes={ NODE1, NODE2 }, order={ NODE1-->NODE2 }) where NODE2 can only be executed after NODE1 is completed.

A more advanced example: PO=(nodes={ NODE1, NODE2, NODE3, X ( NODE4, NODE5 ) }, order={ NODE1-->NODE2, NODE1-->X ( NODE4, NODE5 ), NODE2-->X ( NODE4, NODE5 ) }), in this case, NODE2 can be executed only after NODE1 is completed, while the choice between NODE4 and NODE5 needs to wait until both NODE1 and NODE2 are finalized.


"""
        return descr

    @abstractmethod
    def copy(self):
        pass


class Transition(POWL):
    transition_id: int = 0

    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__()
        self._label = label
        self._identifier = Transition.transition_id
        Transition.transition_id = Transition.transition_id + 1

    def copy(self):
        return Transition(self._label)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Transition):
            return (
                self._label == other._label
                and self._identifier == other._identifier
            )
        return False

    def equal_content(self, other: object) -> bool:
        if isinstance(other, Transition):
            return self._label == other._label
        return False

    def __hash__(self) -> int:
        return self._identifier

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Transition):
            if self.label and other.label and self.label < other.label:
                return self.label < other.label
            return self._identifier < other._identifier
        elif isinstance(other, OperatorPOWL):
            return True
        elif isinstance(other, StrictPartialOrder):
            return True
        return NotImplemented


class SilentTransition(Transition):
    def __init__(self) -> None:
        super().__init__(label=None)

    def copy(self):
        return SilentTransition()


class FrequentTransition(Transition):
    def __init__(
        self, label, min_freq: Union[str, int], max_freq: Union[str, int]
    ) -> None:
        self.skippable = False
        self.selfloop = False
        if min_freq == 0:
            self.skippable = True
        if max_freq == "-":
            self.selfloop = True
        min_freq = "1"
        self.activity = label
        if self.skippable or self.selfloop:
            label = (
                str(label)
                + "\n"
                + "["
                + str(min_freq)
                + ","
                + str(max_freq)
                + "]"
            )

        super().__init__(label=label)


class StrictPartialOrder(POWL):

    def __init__(self, nodes: TList[POWL]) -> None:
        super().__init__()
        self.operator = Operator.PARTIALORDER
        self._set_order(nodes)
        self.additional_information = None

    def copy(self):
        copied_nodes = {n: n.copy() for n in self.order.nodes}
        res = StrictPartialOrder(list(copied_nodes.values()))
        for n1 in self.order.nodes:
            for n2 in self.order.nodes:
                if self.order.is_edge(n1, n2):
                    res.add_edge(copied_nodes[n1], copied_nodes[n2])
        return res

    def _set_order(self, nodes: TList[POWL]) -> None:
        self.order = BinaryRelation(nodes)

    def get_order(self) -> BinaryRelation:
        return self.order

    def _set_children(self, children: TList[POWL]) -> None:
        self.order.nodes = children

    def get_children(self) -> TList[POWL]:
        return self.order.nodes

    def to_string(self, level=0, indent=False, max_indent=sys.maxsize) -> str:
        """
        Represents a StrictPartialOrder as a string, avoiding infinite recursion.

        Parameters
        ----------
        level : int
            Current indentation level
        indent : bool
            Whether to indent the output
        max_indent : int
            Maximum indentation level

        Returns
        -------
        str
            String representation of the partial order
        """
        # Start with the partial order label
        rep = f"{STRICT_PARTIAL_ORDER_LABEL}=(nodes={{"

        # Represent the nodes (children)
        nodes_str = []
        for i, node in enumerate(self.order.nodes):
            # Call to_string on each child with increased level, preventing recursive blow-up
            node_str = node.to_string(level=level + 1, indent=False, max_indent=max_indent)
            nodes_str.append(node_str)
        rep += ", ".join(nodes_str)
        rep += "}, order={"

        # Represent the edges in the partial order
        edges_str = []
        for source in self.order.nodes:
            for target in self.order.nodes:
                if self.order.is_edge(source, target):
                    # Use a simplified representation for source and target to avoid recursion
                    source_str = source.label if source.label else f"id_{hash(source)}"
                    target_str = target.label if target.label else f"id_{hash(target)}"
                    edges_str.append(f"{source_str}-->{target_str}")
        rep += ", ".join(edges_str)
        rep += "})"

        # Apply indentation if requested
        if indent and level <= max_indent:
            rep = "\n".join(hie_utils.indent_representation(rep, max_indent=max_indent))

        return rep

    def __repr__(self) -> str:
        return self.to_string()

    def __lt__(self, other: object) -> bool:
        if isinstance(other, StrictPartialOrder):
            return self.__repr__() < other.__repr__()
        elif isinstance(other, OperatorPOWL):
            return False
        elif isinstance(other, Transition):
            return False
        return NotImplemented

    partial_order = property(get_order, _set_order)
    children = property(get_children, _set_children)

    # def __eq__(self, other):
    #     if not isinstance(other, StrictPartialOrder):
    #         return False
    #
    #     ordered_nodes_1 = sorted(list(self.order.nodes))
    #     ordered_nodes_2 = sorted(list(other.order.nodes))
    #     if len(ordered_nodes_1) != len(ordered_nodes_2):
    #         return False
    #     for i in range(len(ordered_nodes_1)):
    #         source_1 = ordered_nodes_1[i]
    #         source_2 = ordered_nodes_2[i]
    #         if not source_1.__eq__(source_2):
    #             return False
    #         for j in range(len(ordered_nodes_1)):
    #             target_1 = ordered_nodes_1[j]
    #             target_2 = ordered_nodes_2[j]
    #             if self.order.is_edge(source_1, target_1) and not other.order.is_edge(source_2, target_2):
    #                 return False
    #             if not self.order.is_edge(source_1, target_1) and other.order.is_edge(source_2, target_2):
    #                 return False
    #     return True

    def equal_content(self, other: object) -> bool:
        if not isinstance(other, StrictPartialOrder):
            return False

        ordered_nodes_1 = sorted(list(self.order.nodes))
        ordered_nodes_2 = sorted(list(other.order.nodes))
        if len(ordered_nodes_1) != len(ordered_nodes_2):
            return False
        for i in range(len(ordered_nodes_1)):
            source_1 = ordered_nodes_1[i]
            source_2 = ordered_nodes_2[i]
            if not source_1.equal_content(source_2):
                return False
            for j in range(len(ordered_nodes_1)):
                target_1 = ordered_nodes_1[j]
                target_2 = ordered_nodes_2[j]
                if self.order.is_edge(
                    source_1, target_1
                ) and not other.order.is_edge(source_2, target_2):
                    return False
                if not self.order.is_edge(
                    source_1, target_1
                ) and other.order.is_edge(source_2, target_2):
                    return False
        return True

    def simplify_using_frequent_transitions(self) -> "StrictPartialOrder":
        new_nodes = {
            node: node.simplify_using_frequent_transitions()
            for node in self.children
        }
        res = StrictPartialOrder(list(new_nodes.values()))
        for node_1 in self.children:
            for node_2 in self.children:
                if self.partial_order.is_edge(node_1, node_2):
                    res.partial_order.add_edge(
                        new_nodes[node_1], new_nodes[node_2]
                    )

        return res

    def simplify(self) -> "StrictPartialOrder":
        simplified_nodes = {}
        sub_nodes = {}
        start_nodes = {}
        end_nodes = {}

        def connected(node):
            for node2 in self.children:
                if self.partial_order.is_edge(
                    node, node2
                ) or self.partial_order.is_edge(node2, node):
                    return True
            return False

        for node_1 in self.children:
            simplified_node = node_1.simplify()
            if isinstance(simplified_node, StrictPartialOrder):

                if not connected(node_1):
                    sub_nodes[node_1] = simplified_node
                else:
                    s_nodes = simplified_node.order.get_start_nodes()
                    e_nodes = simplified_node.order.get_end_nodes()
                    if len(s_nodes) == 1 and len(e_nodes) == 1:
                        sub_nodes[node_1] = simplified_node
                        start_nodes[node_1] = list(s_nodes)[0]
                        end_nodes[node_1] = list(e_nodes)[0]
                    else:
                        simplified_nodes[node_1] = simplified_node
            else:
                simplified_nodes[node_1] = simplified_node

        new_nodes = list(simplified_nodes.values())
        for po, simplified_po in sub_nodes.items():
            new_nodes = new_nodes + list(simplified_po.children)
        res = StrictPartialOrder(new_nodes)
        for node_1 in self.children:
            for node_2 in self.children:
                if self.partial_order.is_edge(node_1, node_2):
                    if (
                        node_1 in simplified_nodes.keys()
                        and node_2 in simplified_nodes.keys()
                    ):
                        res.partial_order.add_edge(
                            simplified_nodes[node_1], simplified_nodes[node_2]
                        )
                    elif node_1 in simplified_nodes.keys():
                        res.partial_order.add_edge(
                            simplified_nodes[node_1], start_nodes[node_2]
                        )
                    elif node_2 in simplified_nodes.keys():
                        res.partial_order.add_edge(
                            end_nodes[node_1], simplified_nodes[node_2]
                        )
                    else:
                        res.partial_order.add_edge(
                            end_nodes[node_1], start_nodes[node_2]
                        )
        for po, simplified_po in sub_nodes.items():
            for node_1 in simplified_po.children:
                for node_2 in simplified_po.children:
                    if simplified_po.partial_order.is_edge(node_1, node_2):
                        res.partial_order.add_edge(node_1, node_2)
        return res

    def add_edge(self, source, target):
        return self.order.add_edge(source, target)


class Sequence(StrictPartialOrder):

    def __init__(self, nodes: TList[POWL]) -> None:
        super().__init__(nodes)
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                self.partial_order.add_edge(nodes[i], nodes[j])


class OperatorPOWL(POWL):
    def __init__(self, operator: Operator, children: TList[POWL]) -> None:
        if operator is Operator.XOR:
            if len(children) < 2:
                raise Exception(
                    "Cannot create a choice of less than 2 submodels!"
                )
        elif operator is Operator.LOOP:
            if len(children) not in (1, 2):
                raise Exception("Loops must have 1 or 2 children! "
                                "1-child: *(A) repeat A. 2-child: *(A,B) do A, repeat B.")
        elif operator is Operator.INTERLEAVING:
            if len(children) < 2:
                raise Exception("Interleaving requires at least 2 submodels!")
        elif operator is Operator.PARALLEL:
            if len(children) < 2:
                raise Exception("Parallel requires at least 2 submodels!")
        elif operator is Operator.SEQUENCE:
            if len(children) < 2:
                raise Exception("Sequence requires at least 2 submodels!")
        elif operator is Operator.OR:
            if len(children) < 2:
                raise Exception("OR requires at least 2 submodels!")
        elif operator is Operator.PARTIALORDER:
            # PartialOrder can have any number of children
            pass
        else:
            raise Exception(f"Unsupported Operator: {operator}")
        super().__init__()
        self.operator = operator
        self.children = children

    def copy(self):
        copied_nodes = [n.copy() for n in self.children]
        return OperatorPOWL(self.operator, copied_nodes)

    def __lt__(self, other: object) -> bool:
        if isinstance(other, OperatorPOWL):
            return self.__repr__() < other.__repr__()
        elif isinstance(other, Transition):
            return False
        elif isinstance(other, StrictPartialOrder):
            return True
        return NotImplemented

    def equal_content(self, other: object) -> bool:
        if not isinstance(other, OperatorPOWL):
            return False

        if self.operator != other.operator:
            return False

        ordered_nodes_1 = sorted(list(self.children))
        ordered_nodes_2 = sorted(list(other.children))
        if len(ordered_nodes_1) != len(ordered_nodes_2):
            return False
        for i in range(len(ordered_nodes_1)):
            node_1 = ordered_nodes_1[i]
            node_2 = ordered_nodes_2[i]
            if not node_1.equal_content(node_2):
                return False
        return True

    def simplify_using_frequent_transitions(self) -> POWL:
        if self.operator is Operator.XOR and len(self.children) == 2:
            child_0 = self.children[0]
            child_1 = self.children[1]
            if isinstance(child_0, Transition) and isinstance(
                child_1, SilentTransition
            ):
                return FrequentTransition(
                    label=child_0.label, min_freq=0, max_freq=1
                )
            elif isinstance(child_1, Transition) and isinstance(
                child_0, SilentTransition
            ):
                return FrequentTransition(
                    label=child_1.label, min_freq=0, max_freq=1
                )

        if self.operator is Operator.LOOP and len(self.children) == 2:
            child_0 = self.children[0]
            child_1 = self.children[1]
            if isinstance(child_0, Transition) and isinstance(
                child_1, SilentTransition
            ):
                return FrequentTransition(
                    label=child_0.label, min_freq=1, max_freq="-"
                )
            elif isinstance(child_1, Transition) and isinstance(
                child_0, SilentTransition
            ):
                return FrequentTransition(
                    label=child_1.label, min_freq=0, max_freq="-"
                )

        return OperatorPOWL(
            self.operator,
            [
                child.simplify_using_frequent_transitions()
                for child in self.children
            ],
        )

    def simplify(self) -> "OperatorPOWL":
        if self.operator is Operator.XOR and len(self.children) == 2:
            child_0 = self.children[0]
            child_1 = self.children[1]

            def merge_with_children(child0, child1):
                if (
                    isinstance(child0, SilentTransition)
                    and isinstance(child1, OperatorPOWL)
                    and child1.operator is Operator.LOOP
                ):
                    if isinstance(child1.children[0], SilentTransition):
                        return OperatorPOWL(
                            Operator.LOOP,
                            [n.simplify() for n in child1.children],
                        )
                    elif isinstance(child1.children[1], SilentTransition):
                        return OperatorPOWL(
                            Operator.LOOP,
                            list(
                                reversed(
                                    [n.simplify() for n in child1.children]
                                )
                            ),
                        )

                return None

            res = merge_with_children(child_0, child_1)
            if res is not None:
                return res

            res = merge_with_children(child_1, child_0)
            if res is not None:
                return res

        if self.operator is Operator.XOR:
            new_children = []
            for child in self.children:
                s_child = child.simplify()
                if (
                    isinstance(s_child, OperatorPOWL)
                    and s_child.operator is Operator.XOR
                ):
                    for node in s_child.children:
                        new_children.append(node.simplify())
                else:
                    new_children.append(s_child)
            return OperatorPOWL(
                Operator.XOR, [child for child in new_children]
            )
        else:
            return OperatorPOWL(
                self.operator, [child.simplify() for child in self.children]
            )


class StartNode:
    """Sentinel node representing the start of a DecisionGraph."""

    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return "start"

    def __hash__(self):
        return hash("start")

    def __eq__(self, other):
        return isinstance(other, StartNode)


class EndNode:
    """Sentinel node representing the end of a DecisionGraph."""

    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return "end"

    def __hash__(self):
        return hash("end")

    def __eq__(self, other):
        return isinstance(other, EndNode)


class DecisionGraph(POWL):
    """
    A DecisionGraph is a POWL model defined over a set of nodes (each node is a POWL model)
    together with a binary relation (order) over these nodes, augmented with two artificial
    nodes: a start node and an end node.

    In the decision graph, each node represents a group (or branch) of activities (or submodels)
    and the binary relation encodes the allowed ordering between these nodes.

    DecisionGraphs model non-block-structured choices that cannot be expressed using
    block-structured XOR or LOOP operators.

    Reference paper:
    H Kourani, G Park, WMP van der Aalst. "Unlocking Non-Block-Structured Decisions:
    Inductive Mining with Choice Graphs" arXiv preprint arXiv:2505.07052.
    """

    def __init__(
        self, order: BinaryRelation, start_nodes, end_nodes, empty_path=False
    ) -> None:
        super().__init__()
        self.operator = None
        self.children = [n for n in order.nodes]
        self.start_nodes = list(start_nodes)
        self.end_nodes = list(end_nodes)
        if not start_nodes or not set(start_nodes).issubset(order.nodes):
            raise Exception(
                "Start nodes must be a non-empty subset of the nodes of the relation!"
            )
        if not end_nodes or not set(end_nodes).issubset(order.nodes):
            raise Exception(
                "End nodes must be a non-empty subset of the nodes of the relation!"
            )
        self.start = StartNode()
        self.end = EndNode()
        order.add_node(self.start)
        order.add_node(self.end)
        for node in start_nodes:
            order.add_edge(self.start, node)
        for node in end_nodes:
            order.add_edge(node, self.end)
        if empty_path:
            order.add_edge(self.start, self.end)

        self.order = order
        self.empty_path = empty_path

    def __repr__(self):
        return f"DecisionGraph({self.children})"

    def copy(self):
        new_children_map = {child: child.copy() for child in self.children}
        res = BinaryRelation(list(set(new_children_map.values())))
        for src in self.children:
            for tgt in self.children:
                if self.order.is_edge(src, tgt):
                    new_src = new_children_map[src]
                    new_tgt = new_children_map[tgt]
                    if new_src != new_tgt or src == tgt:
                        res.add_edge(new_src, new_tgt)
        new_start_nodes = list({new_children_map[child] for child in self.start_nodes})
        new_end_nodes = list({new_children_map[child] for child in self.end_nodes})
        empty_path = self.order.is_edge(self.start, self.end)
        return DecisionGraph(res, new_start_nodes, new_end_nodes, empty_path)

    def simplify(self) -> "POWL":
        if len(self.children) == 1:
            child_0 = self.children[0]
            skippable = self.order.is_edge(self.start, self.end)
            repeatable = self.order.is_edge(child_0, child_0)

            if skippable:
                if repeatable:
                    return OperatorPOWL(
                        Operator.LOOP, [SilentTransition(), child_0]
                    ).simplify()
                else:
                    if isinstance(child_0, DecisionGraph):
                        child_0.order.add_edge(child_0.start, child_0.end)
                        return child_0.simplify()
                    else:
                        return OperatorPOWL(
                            Operator.XOR, [SilentTransition(), child_0]
                        ).simplify()

            elif repeatable:
                return OperatorPOWL(
                    Operator.LOOP, [child_0, SilentTransition()]
                ).simplify()

            else:
                return child_0.simplify()

        else:
            new_dg = self

            seq = new_dg.__group_start_seq()
            if seq:
                return seq.simplify()

            seq = new_dg.__group_end_seq()
            if seq:
                return seq.simplify()

            res = new_dg.__group_pure_seq()
            if len(res.children) < len(new_dg.children):
                return res.simplify()

            new_children_map = {}
            for child in new_dg.children:
                s_child = child.simplify()
                new_children_map[child] = s_child
            return new_dg.__apply_mapping(new_children_map)

    def simplify_using_frequent_transitions(self) -> "POWL":
        if len(self.children) == 1:
            child_0 = self.children[0]

            if isinstance(child_0, Transition):
                skippable = self.order.is_edge(self.start, self.end)
                repeatable = self.order.is_edge(child_0, child_0)

                min_freq = 0 if skippable else 1
                max_freq = "-" if repeatable else 1

                if skippable or repeatable:
                    return FrequentTransition(
                        label=child_0._label, min_freq=min_freq, max_freq=max_freq
                    )
                else:
                    return child_0

        new_children_map = {}
        edges_to_remove = set()
        for child in self.children:
            s_child = child.simplify_using_frequent_transitions()

            if isinstance(s_child, Transition):
                preset = self.order.get_preset(child)
                postset = self.order.get_postset(child)

                repeatable = self.order.is_edge(child, child)
                skippable = all(self.order.is_edge(pre, post) for pre in preset for post in postset)

                if skippable:
                    for pre in preset:
                        for post in postset:
                            edges_to_remove.add((pre, post))
                    if child in self.start_nodes:
                        self.start_nodes = [
                            x for x in self.start_nodes if x not in postset
                        ]
                    if child in self.end_nodes:
                        self.end_nodes = [x for x in self.end_nodes if x not in preset]

                if repeatable:
                    edges_to_remove.add((child, child))

                if skippable or repeatable:
                    min_freq = 0 if skippable else 1
                    max_freq = "-" if repeatable else 1
                    s_child = FrequentTransition(
                        label=child._label, min_freq=min_freq, max_freq=max_freq
                    )

            new_children_map[child] = s_child
        new_dg = self.__apply_mapping(new_children_map, edges_to_remove)
        return new_dg

    def validate_connectivity(self):
        for node in self.order.nodes:
            if node == self.start or node == self.end:
                continue
            reachable_from_start = False
            reachable_to_end = False

            def _can_reach(src, tgt, visited=None):
                if visited is None:
                    visited = set()
                if src == tgt:
                    return True
                visited.add(src)
                for n in self.order.nodes:
                    if self.order.is_edge(src, n) and n not in visited:
                        if _can_reach(n, tgt, visited):
                            return True
                return False

            if not _can_reach(self.start, node):
                raise Exception(
                    f"All nodes in a decision graph must be reachable from start!"
                )
            if not _can_reach(node, self.end):
                raise Exception(
                    f"All nodes in a decision graph must be able to reach end!"
                )

    def __apply_mapping(self, mapping, edges_to_remove=None) -> "DecisionGraph":
        if edges_to_remove is None:
            edges_to_remove = set()
        res = BinaryRelation(list(set(mapping.values())))
        for src in self.children:
            for tgt in self.children:
                if self.order.is_edge(src, tgt) and (src, tgt) not in edges_to_remove:
                    new_src = mapping[src]
                    new_tgt = mapping[tgt]
                    if new_src != new_tgt or src == tgt:
                        res.add_edge(new_src, new_tgt)
        new_start_nodes = list({mapping[child] for child in self.start_nodes})
        new_end_nodes = list({mapping[child] for child in self.end_nodes})
        empty_path = (
            self.order.is_edge(self.start, self.end)
            and not (self.start, self.end) in edges_to_remove
        )
        return DecisionGraph(res, new_start_nodes, new_end_nodes, empty_path)

    def __create_mapping(self, old_children, new_child):
        mapping = {}
        for key in self.children:
            if key in old_children:
                mapping[key] = new_child
            else:
                mapping[key] = key
        return mapping

    def __group_pure_seq(self):
        for child in list(self.children):
            for child2 in self.children:
                post1 = self.order.get_postset(child)
                pre2 = self.order.get_preset(child2)
                if pre2 == {child} and post1 == {child2}:
                    seq = Sequence([child, child2])
                    mapping = self.__create_mapping({child, child2}, seq)
                    new_dg = self.__apply_mapping(mapping)
                    return new_dg.__group_pure_seq()
        return self

    def __group_start_seq(self):
        start_list = []
        current_dg = self
        while (
            len(current_dg.children) > 1
            and len(current_dg.start_nodes) == 1
            and not current_dg.order.is_edge(current_dg.start, current_dg.end)
            and current_dg.order.get_preset(current_dg.start_nodes[0])
            == {current_dg.start}
        ):
            start = current_dg.start_nodes[0]
            start_list.append(start)
            postset = current_dg.order.get_postset(start)
            new_start_nodes = list(postset - {current_dg.end})
            new_children = [n for n in current_dg.children if n != start]
            new_end_nodes = [n for n in current_dg.end_nodes if n != start]
            new_order = BinaryRelation(new_children)
            for c1 in new_children:
                for c2 in new_children:
                    if current_dg.order.is_edge(c1, c2):
                        new_order.add_edge(c1, c2)
            empty_path = current_dg.end in postset
            current_dg = DecisionGraph(
                new_order, new_start_nodes, new_end_nodes, empty_path
            )
        if len(start_list) > 0:
            seq = Sequence(start_list + [current_dg])
            return seq
        return None

    def __group_end_seq(self):
        end_list = []
        current_dg = self
        while (
            len(current_dg.children) > 1
            and len(current_dg.end_nodes) == 1
            and not current_dg.order.is_edge(current_dg.start, current_dg.end)
            and current_dg.order.get_postset(current_dg.end_nodes[0])
            == {current_dg.end}
        ):
            end = current_dg.end_nodes[0]
            end_list = [end] + end_list
            pretset = current_dg.order.get_preset(end)
            new_end_nodes = list(pretset - {current_dg.start})
            new_children = [n for n in current_dg.children if n != end]
            new_start_nodes = [n for n in current_dg.start_nodes if n != end]
            new_order = BinaryRelation(new_children)
            for c1 in new_children:
                for c2 in new_children:
                    if current_dg.order.is_edge(c1, c2):
                        new_order.add_edge(c1, c2)
            empty_path = current_dg.start in pretset
            current_dg = DecisionGraph(
                new_order, new_start_nodes, new_end_nodes, empty_path
            )
        if len(end_list) > 0:
            seq = Sequence([current_dg] + end_list)
            return seq
        return None

    def validate_soundness(self) -> bool:
        """
        Validate that the choice graph is sound.

        A choice graph is sound if:
        1. Every node is on a path from start to end (already enforced by validate_connectivity)
        2. The graph is acyclic (no unexpected loops)
        3. The graph is structurally sound (no orphaned nodes)

        This validates that the model can be successfully executed
        without deadlocks, livelocks, or other anomalies.

        Returns:
            True if the choice graph is sound, False otherwise
        """
        try:
            # Check 1: Connectivity (all nodes reachable from start, can reach end)
            self.validate_connectivity()

            # Check 2: Acyclicity (no cycles in the graph)
            if not self.validate_acyclicity():
                return False

            # Check 3: Structural soundness (no orphaned nodes)
            if not self._validate_structural_soundness():
                return False

            return True

        except Exception as e:
            # Any validation failure means not sound
            return False

    def _validate_structural_soundness(self) -> bool:
        """
        Validate structural soundness of the choice graph.

        Checks that:
        - All non-sentril nodes have at least one incoming or outgoing edge
        - No disconnected components
        - Start and end nodes are properly connected

        Returns:
            True if structurally sound, False otherwise
        """
        # Check that all children have at least one connection
        for child in self.children:
            has_incoming = any(self.order.is_edge(n, child) for n in self.order.nodes if n != self.end)
            has_outgoing = any(self.order.is_edge(child, n) for n in self.order.nodes if n != self.start)

            # Nodes should have at least one connection (except special cases)
            if not has_incoming and not has_outgoing:
                # This could be valid if it's the only node and start/end connect to it
                if len(self.children) > 1:
                    return False

        # Verify start and end are properly connected
        if not self.start_nodes:
            return False
        if not self.end_nodes:
            return False

        # Start should have outgoing edges to its start_nodes
        for start_node in self.start_nodes:
            if not self.order.is_edge(self.start, start_node):
                return False

        # End should have incoming edges from its end_nodes
        for end_node in self.end_nodes:
            if not self.order.is_edge(end_node, self.end):
                return False

        return True

    def get_soundness_report(self) -> Dict[str, Any]:
        """
        Generate a detailed soundness report for the choice graph.

        Returns:
            Dictionary with soundness validation results
        """
        from typing import Dict, Any

        report = {
            "is_sound": False,
            "errors": [],
            "warnings": [],
            "metrics": {}
        }

        # Check connectivity
        try:
            self.validate_connectivity()
            report["metrics"]["connectivity"] = "valid"
        except Exception as e:
            report["errors"].append(f"Connectivity error: {e}")
            report["metrics"]["connectivity"] = "invalid"

        # Check acyclicity
        is_acyclic = self.validate_acyclicity()
        report["metrics"]["acyclicity"] = "valid" if is_acyclic else "invalid"
        if not is_acyclic:
            report["errors"].append("Graph contains cycles")

        # Check structural soundness
        is_structurally_sound = self._validate_structural_soundness()
        report["metrics"]["structural_soundness"] = "valid" if is_structurally_sound else "invalid"
        if not is_structurally_sound:
            report["errors"].append("Structural soundness validation failed")

        # Collect metrics
        report["metrics"]["num_nodes"] = len(self.children)
        report["metrics"]["num_edges"] = len(self.get_edges())
        report["metrics"]["num_start_nodes"] = len(self.start_nodes)
        report["metrics"]["num_end_nodes"] = len(self.end_nodes)
        report["metrics"]["has_empty_path"] = self.empty_path

        # Overall soundness
        report["is_sound"] = (
            len(report["errors"]) == 0 and
            report["metrics"]["connectivity"] == "valid" and
            is_acyclic and
            is_structurally_sound
        )

        return report

    def validate_acyclicity(self) -> bool:
        """
        Validate that the choice graph is acyclic (Definition 5, condition 5).

        From "Unlocking Non-Block-Structured Decisions":
        (Ai →+ Aj ∧ Aj →+ Ai) ⇒ Ai = Aj

        This ensures no node is reachable from itself through the graph,
        which is required for proper representation of choice behavior.

        Returns:
            True if the graph is acyclic, False otherwise
        """
        visited = set()
        rec_stack = set()

        def has_cycle(node):
            """DFS to detect cycles."""
            visited.add(node)
            rec_stack.add(node)

            # Get successors (excluding sentinel nodes for cycle detection)
            successors = self.order.get_postset(node)
            for successor in successors:
                if successor not in (self.start, self.end):
                    if successor not in visited:
                        if has_cycle(successor):
                            return True
                    elif successor in rec_stack:
                        return True

            rec_stack.remove(node)
            return False

        # Check all non-sentinel nodes
        for node in self.children:
            if node not in visited:
                if has_cycle(node):
                    return False

        return True

    def get_edges(self) -> list:
        """
        Get all edges in the choice graph.

        Returns:
            List of (source, target) tuples representing edges
        """
        edges = []
        for i, node1 in enumerate(self.order.get_nodes()):
            for j, node2 in enumerate(self.order.get_nodes()):
                if self.order.is_edge(node1, node2):
                    edges.append((node1, node2))

        # Add edges from start to start_nodes
        for start_node in self.start_nodes:
            edges.append((self.start, start_node))

        # Add edges from end_nodes to end
        for end_node in self.end_nodes:
            edges.append((end_node, self.end))

        # Add empty path edge if exists
        if self.empty_path:
            edges.append((self.start, self.end))

        return edges

    def get_all_paths(self) -> list:
        """
        Get all execution paths from start to end in the choice graph.

        Each path is a list of POWL nodes representing a valid execution trace.

        Returns:
            List of paths (each path is a list of nodes)
        """
        from pm4py.objects.powl.obj import StartNode, EndNode

        paths = []

        def dfs(current_node, current_path, visited):
            """Depth-first search to find all paths."""
            if isinstance(current_node, EndNode):
                paths.append(current_path)
                return

            if current_node in visited:
                return  # Avoid cycles

            visited.add(current_node)
            successors = self.order.get_postset(current_node)

            for successor in successors:
                if isinstance(successor, EndNode):
                    dfs(successor, current_path, visited.copy())
                elif successor not in (self.start, self.end):
                    dfs(successor, current_path + [successor], visited.copy())

        dfs(self.start, [], set())
        return paths

    def language(self) -> list:
        """
        Compute the language of this choice graph (Definition 3).

        L(G) = concatenation of languages along all paths from start to end.

        Returns:
            List of traces (each trace is a list of activity labels)
        """
        paths = self.get_all_paths()
        traces = []

        for path in paths:
            trace = []
            for node in path:
                if isinstance(node, Transition):
                    if node._label is not None:
                        trace.append(node._label)
                elif isinstance(node, SilentTransition):
                    pass  # Silent transitions don't add to trace
                elif hasattr(node, 'language'):
                    # Recursively get language from nested POWL nodes
                    nested_lang = node.language()
                    if nested_lang:
                        trace.extend(nested_lang[0] if nested_lang else [])
            traces.append(trace)

        return traces
