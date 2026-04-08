"""
Serialize POWL models to RDF using O* POWL ontology (powl-core.nt).

Converts pm4py POWL objects (Transition, StrictPartialOrder, OperatorPOWL,
DecisionGraph) to RDF Turtle triples using the vocabulary defined in:
  https://example.org/ostar/powl#

Usage:
    from pm4py.objects.powl.serializer import serialize_to_rdf
    rdf_turtle = serialize_to_rdf(powl_model)
"""

import uuid
from typing import Optional

from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef, XSD
from rdflib.namespace import OWL

from pm4py.objects.powl.obj import (
    DecisionGraph,
    OperatorPOWL,
    POWL,
    SilentTransition,
    StrictPartialOrder,
    Transition,
)
from pm4py.objects.process_tree.obj import Operator

POWL_NS = Namespace("https://example.org/ostar/powl#")
COORD_NS = Namespace("https://example.org/ostar/powl-coord#")


def serialize_to_rdf(
    powl_obj: POWL,
    base_iri: Optional[str] = None,
    label: Optional[str] = None,
    fmt: str = "turtle",
) -> str:
    """Serialize a POWL model to RDF using O* POWL ontology.

    Args:
        powl_obj: POWL object (Transition, StrictPartialOrder, OperatorPOWL, DecisionGraph)
        base_iri: Base IRI for generated nodes. Defaults to urn:powl:spec:{uuid}
        label: Optional label for the WorkflowSpecification
        fmt: Output format — "turtle" or "nt" (N-Triples, O* default)

    Returns:
        RDF serialization string
    """
    g = Graph()
    g.bind("powl", POWL_NS)

    if base_iri is None:
        base_iri = f"urn:powl:spec:{uuid.uuid4()}"
    if not base_iri.endswith((":") if ":" in base_iri else ("/")):
        base_iri = f"{base_iri}:"

    spec_iri = URIRef(base_iri.rstrip(":"))
    g.add((spec_iri, RDF.type, POWL_NS.WorkflowSpecification))
    g.add((spec_iri, RDFS.label, Literal(label or "Generated from POWL")))

    # Serialize the root node
    seen = {}  # id(node) -> IRI
    root_iri = _serialize_node(g, powl_obj, spec_iri, base_iri, seen)
    g.add((spec_iri, POWL_NS.root, root_iri))

    rdflib_fmt = "nt" if fmt == "nt" else "turtle"
    return g.serialize(format=rdflib_fmt)


def _node_iri(base_iri: str, node: POWL, seen: dict) -> URIRef:
    """Generate a stable IRI for a POWL node."""
    node_id = id(node)
    if node_id in seen:
        return seen[node_id]

    if isinstance(node, Transition) and node._label:
        # Use label-based IRI for named transitions
        slug = node._label.replace(" ", "-").replace("/", "-").lower()
        iri = URIRef(f"{base_iri}{slug}")
    else:
        iri = URIRef(f"{base_iri}node-{node_id}")

    seen[node_id] = iri
    return iri


def _serialize_node(
    g: Graph,
    node: POWL,
    parent_iri: URIRef,
    base_iri: str,
    seen: dict,
) -> URIRef:
    """Recursively serialize a POWL node. Returns the node's IRI."""
    node_iri = _node_iri(base_iri, node, seen)

    if isinstance(node, SilentTransition):
        g.add((node_iri, RDF.type, POWL_NS.SilentActivity))
        if parent_iri:
            g.add((parent_iri, POWL_NS.hasChild, node_iri))
        return node_iri

    if isinstance(node, Transition):
        g.add((node_iri, RDF.type, POWL_NS.Activity))
        if node._label:
            g.add((node_iri, RDFS.label, Literal(node._label)))
            g.add((node_iri, POWL_NS.activityLabel, Literal(node._label)))
        if parent_iri:
            g.add((parent_iri, POWL_NS.hasChild, node_iri))
        return node_iri

    if isinstance(node, StrictPartialOrder):
        g.add((node_iri, RDF.type, POWL_NS.PartialOrder))
        g.add((node_iri, RDFS.label, Literal("PartialOrder")))
        if parent_iri:
            g.add((parent_iri, POWL_NS.hasChild, node_iri))

        # Serialize children
        for child in node.order.nodes:
            _serialize_node(g, child, node_iri, base_iri, seen)

        # Serialize edges as Dependency nodes
        edge_idx = 0
        for src in node.order.nodes:
            for tgt in node.order.nodes:
                if node.order.is_edge(src, tgt):
                    src_iri = _node_iri(base_iri, src, seen)
                    tgt_iri = _node_iri(base_iri, tgt, seen)
                    dep_iri = URIRef(f"{base_iri}dep-{edge_idx}")
                    edge_idx += 1
                    g.add((dep_iri, RDF.type, POWL_NS.Dependency))
                    g.add((dep_iri, POWL_NS.source, src_iri))
                    g.add((dep_iri, POWL_NS.target, tgt_iri))
                    g.add((node_iri, POWL_NS.hasEdge, dep_iri))

        return node_iri

    if isinstance(node, OperatorPOWL):
        if node.operator == Operator.XOR:
            g.add((node_iri, RDF.type, POWL_NS.ExclusiveChoice))
            g.add((node_iri, RDFS.label, Literal("ExclusiveChoice")))
        elif node.operator == Operator.LOOP:
            g.add((node_iri, RDF.type, POWL_NS.Loop))
            g.add((node_iri, RDFS.label, Literal("Loop")))
            # Loop children: [0]=doBody, [1]=redoBody
            if len(node.children) >= 1:
                do_iri = _serialize_node(g, node.children[0], node_iri, base_iri, seen)
                g.add((node_iri, POWL_NS.doBody, do_iri))
            if len(node.children) >= 2:
                redo_iri = _serialize_node(g, node.children[1], node_iri, base_iri, seen)
                g.add((node_iri, POWL_NS.redoBody, redo_iri))
            return node_iri
        else:
            # Fallback: treat as generic composite
            g.add((node_iri, RDF.type, POWL_NS.CompositeElement))
            g.add((node_iri, RDFS.label, Literal(f"Operator({node.operator})")))

        if parent_iri:
            g.add((parent_iri, POWL_NS.hasChild, node_iri))

        # Serialize children
        for child in node.children:
            _serialize_node(g, child, node_iri, base_iri, seen)

        return node_iri

    if isinstance(node, DecisionGraph):
        # Serialize as a PartialOrder with start/end sentinel activities
        g.add((node_iri, RDF.type, POWL_NS.PartialOrder))
        g.add((node_iri, RDFS.label, Literal("DecisionGraph")))
        if parent_iri:
            g.add((parent_iri, POWL_NS.hasChild, node_iri))

        # Serialize children
        for child in node.children:
            _serialize_node(g, child, node_iri, base_iri, seen)

        # Serialize edges
        edge_idx = 0
        for src in node.order.nodes:
            for tgt in node.order.nodes:
                if node.order.is_edge(src, tgt):
                    # Skip sentinel edges
                    if isinstance(src, (DecisionGraph.StartNode, DecisionGraph.EndNode)):
                        continue
                    if isinstance(tgt, (DecisionGraph.StartNode, DecisionGraph.EndNode)):
                        continue
                    src_iri = _node_iri(base_iri, src, seen)
                    tgt_iri = _node_iri(base_iri, tgt, seen)
                    dep_iri = URIRef(f"{base_iri}dep-{edge_idx}")
                    edge_idx += 1
                    g.add((dep_iri, RDF.type, POWL_NS.Dependency))
                    g.add((dep_iri, POWL_NS.source, src_iri))
                    g.add((dep_iri, POWL_NS.target, tgt_iri))
                    g.add((node_iri, POWL_NS.hasEdge, dep_iri))

        return node_iri

    # Fallback: treat unknown as Activity
    g.add((node_iri, RDF.type, POWL_NS.Activity))
    if parent_iri:
        g.add((parent_iri, POWL_NS.hasChild, node_iri))
    return node_iri
