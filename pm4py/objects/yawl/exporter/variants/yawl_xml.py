'''
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see this software project's root or
visit <https://www.gnu.org/licenses/>.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
'''

'''
YAWL XML serialization for pm4py.

This module converts YAWL specification objects to YAWL XML format,
following the YAWL schema specification for compatibility with YAWL7
and other YAWL engines.

Reference:
- YAWL Foundation: https://www.yawlfoundation.org/
- YAWL Schema: http://www.yawlfoundation.org/yawlschema.xsd
'''

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional

from pm4py.objects.yawl.obj import (
    YAWLSpecification,
    YAWLMetadata,
    YAWLDecomposition,
    YAWLTask,
    YAWLFlow,
)


@dataclass
class Parameters:
    """Parameters for YAWL XML export."""
    pretty_print: bool = True
    indent: str = "  "
    encoding: str = "UTF-8"
    xml_declaration: bool = True


class ParametersYAML:
    """YAML-compatible parameters for backwards compatibility."""
    def __init__(self, pretty_print=True, indent="  ", encoding="UTF-8"):
        self.pretty_print = pretty_print
        self.indent = indent
        self.encoding = encoding


def apply(yawl_spec: YAWLSpecification, parameters=None) -> str:
    """Serialize YAWL specification to XML string.

    Parameters
    -----------
    yawl_spec : YAWLSpecification
        YAWL specification object
    parameters
        Export parameters (optional)

    Returns
    --------
    str
        XML string representation
    """
    if parameters is None:
        parameters = Parameters()

    # Build XML tree
    root = _build_xml_tree(yawl_spec)

    # Serialize to string
    if parameters.pretty_print:
        xml_str = _pretty_print(root, indent=parameters.indent)
    else:
        xml_str = ET.tostring(root, encoding=parameters.encoding)

    if parameters.xml_declaration:
        xml_declaration = f'<?xml version="1.0" encoding="{parameters.encoding}"?>\n'
        return xml_declaration + xml_str

    return xml_str


def _build_xml_tree(yawl_spec: YAWLSpecification) -> ET.Element:
    """Build XML element tree from YAWL specification.

    YAWL XML structure:
    <specification xmlns="http://www.yawlfoundation.org/yawlschema">
      <specificationSet>
        <specification uri="...">
          <metadata>...</metadata>
          <decomposition id="root" isRootNet="true">
            <inputCondition id="input"/>
            <outputCondition id="output"/>
            <task id="t1">...</task>
            <flow source="input" target="t1"/>
          </decomposition>
        </specification>
      </specificationSet>
    </specification>
    """
    # Root element
    root = ET.Element("specification")
    root.set("xmlns", "http://www.yawlfoundation.org/yawlschema")
    root.set("version", "2.0")

    # Specification set
    spec_set = ET.SubElement(root, "specificationSet")

    # Specification element
    spec_elem = ET.SubElement(spec_set, "specification")
    spec_elem.set("uri", yawl_spec.uri)

    # Metadata
    _add_metadata(spec_elem, yawl_spec.metadata)

    # Decompositions
    for decomp in yawl_spec.decompositions:
        _add_decomposition(spec_elem, decomp)

    return root


def _add_metadata(parent: ET.Element, metadata: YAWLMetadata):
    """Add metadata element to parent."""
    metadata_elem = ET.SubElement(parent, "metadata")

    # Title (required)
    title_elem = ET.SubElement(metadata_elem, "title")
    title_elem.text = metadata.title

    # Description (optional)
    if metadata.description:
        desc_elem = ET.SubElement(metadata_elem, "description")
        desc_elem.text = metadata.description

    # Version (optional)
    if metadata.version:
        version_elem = ET.SubElement(metadata_elem, "version")
        version_elem.text = metadata.version

    # Author (optional)
    if metadata.author:
        author_elem = ET.SubElement(metadata_elem, "author")
        author_elem.text = metadata.author

    # Created timestamp (optional)
    if metadata.created:
        created_elem = ET.SubElement(metadata_elem, "created")
        created_elem.text = metadata.created


def _add_decomposition(parent: ET.Element, decomp: YAWLDecomposition):
    """Add decomposition element to parent."""
    decomp_elem = ET.SubElement(parent, "decomposition")
    decomp_elem.set("id", decomp.id)
    decomp_elem.set("isRootNet", str(decomp.is_root_net).lower())

    # Input condition
    input_elem = ET.SubElement(decomp_elem, "inputCondition")
    input_elem.set("id", decomp.input_condition)

    # Output condition
    output_elem = ET.SubElement(decomp_elem, "outputCondition")
    output_elem.set("id", decomp.output_condition)

    # Tasks
    for task in decomp.tasks:
        _add_task(decomp_elem, task)

    # Flows
    for flow in decomp.flows:
        _add_flow(decomp_elem, flow)


def _add_task(parent: ET.Element, task: YAWLTask):
    """Add task element to parent."""
    task_elem = ET.SubElement(parent, "task")
    task_elem.set("id", task.id)

    # Name (required)
    name_elem = ET.SubElement(task_elem, "name")
    if task.name:
        name_elem.text = task.name

    # Join type
    join_elem = ET.SubElement(task_elem, "join")
    join_elem.set("type", task.join_type)

    # Split type
    split_elem = ET.SubElement(task_elem, "split")
    split_elem.set("type", task.split_type)

    # Decomposition reference (if composite task)
    if task.decomposition_id:
        decomp_elem = ET.SubElement(task_elem, "decomposition")
        decomp_elem.set("id", task.decomposition_id)


def _add_flow(parent: ET.Element, flow: YAWLFlow):
    """Add flow element to parent."""
    flow_elem = ET.SubElement(parent, "flow")
    flow_elem.set("source", flow.source)
    flow_elem.set("target", flow.target)


def _pretty_print(element: ET.Element, indent: str = "  ") -> str:
    """Pretty-print XML element with proper indentation.

    Uses minidom for consistent pretty-printing.
    """
    xml_str = ET.tostring(element, encoding="unicode")

    from xml.dom import minidom
    parsed = minidom.parseString(xml_str)
    pretty = parsed.toprettyxml(indent=indent)

    # Remove XML declaration (we add it separately if needed)
    lines = pretty.split('\n')
    if lines and lines[0].startswith('<?xml'):
        lines = lines[1:]

    # Remove trailing whitespace from each line
    lines = [line.rstrip() for line in lines]

    # Remove empty lines
    lines = [line for line in lines if line.strip()]

    return '\n'.join(lines)
