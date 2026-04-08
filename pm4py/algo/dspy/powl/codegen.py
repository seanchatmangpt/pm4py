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
'''

"""
Code generation for orchestrators from POWL models.

This module converts POWL v2 models to executable code for various
orchestration platforms:
- n8n JSON workflow format
- Temporal Go workflow code
- Camunda BPMN XML (via existing converter)
- YAWL v6 XML (via existing converter)
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field


def _sanitize_name(name: str) -> str:
    """Sanitize activity name for use as identifier in code."""
    # Remove special characters, replace spaces with underscores
    sanitized = re.sub(r'[^\w\s-]', '', name)
    sanitized = re.sub(r'[\s-]+', '_', sanitized.strip())
    # Ensure it starts with a letter
    if sanitized and sanitized[0].isdigit():
        sanitized = 'Activity_' + sanitized
    return sanitized or 'Activity'


def _extract_activities(powl_string: str) -> List[str]:
    """Extract activity names from POWL string."""
    # Find all single-quoted strings
    activities = re.findall(r"'([^']+)'", powl_string)
    # Filter out operator names and duplicates
    reserved = {'X', 'PO', 'tau', 'nodes', 'order'}
    activities = [a for a in activities if a not in reserved]
    return list(dict.fromkeys(activities))  # Preserve order, remove duplicates


def _get_activity_metadata(powl_string: str) -> List[Dict[str, str]]:
    """Extract metadata about activities from POWL string."""
    activities = _extract_activities(powl_string)
    metadata = []
    for i, activity in enumerate(activities):
        metadata.append({
            'id': f"activity_{i}",
            'name': activity,
            'sanitized': _sanitize_name(activity),
            'index': i
        })
    return metadata


def generate_n8n_json(powl_string: str, workflow_name: str = "Generated Workflow") -> dict:
    """Generate n8n workflow JSON from POWL model.

    Parameters
    ----------
    powl_string : str
        The POWL model string.
    workflow_name : str
        Name for the n8n workflow.

    Returns
    -------
    dict
        n8n workflow JSON structure ready for import.
    """
    activities = _extract_activities(powl_string)
    activity_meta = _get_activity_metadata(powl_string)

    # Build n8n nodes
    nodes = []
    node_map = {}

    # Start node
    start_node = {
        "parameters": {},
        "id": "start-node",
        "name": "Start",
        "type": "n8n-nodes-base.manualTrigger",
        "typeVersion": 1,
        "position": [250, 300]
    }
    nodes.append(start_node)
    node_map['start'] = 'start-node'

    # Activity nodes
    x_offset = 400
    for meta in activity_meta:
        node = {
            "parameters": {
                "activityName": meta['name'],
                "assignee": "{{$json['assignee']}}",
            },
            "id": meta['id'],
            "name": meta['name'],
            "type": "n8n-nodes-base.manualTrigger",
            "typeVersion": 1,
            "position": [x_offset, 300 + len(nodes) * 150]
        }
        nodes.append(node)
        node_map[meta['sanitized']] = meta['id']
        x_offset += 200

    # End node
    end_node = {
        "parameters": {},
        "id": "end-node",
        "name": "End",
        "type": "n8n-nodes-base.noOp",
        "typeVersion": 1,
        "position": [x_offset, 300 + len(nodes) * 150]
    }
    nodes.append(end_node)
    node_map['end'] = 'end-node'

    # Build connections based on POWL structure
    connections = _parse_powl_structure(powl_string, node_map)

    # n8n workflow structure
    workflow = {
        "name": workflow_name,
        "nodes": nodes,
        "connections": connections,
        "settings": {
            "executionOrder": "v1"
        },
        "staticData": None,
        "tags": [],
        "pinData": {},
        "versionId": "1"
    }

    return workflow


def _parse_powl_structure(powl_string: str, node_map: Dict[str, str]) -> Dict:
    """Parse POWL structure to build n8n connections.

    This is a simplified parser that extracts the control flow
    from the POWL string and maps it to n8n node connections.
    """
    connections = {}

    # Extract order relations
    order_match = re.search(r'order=\{([^}]+)\}', powl_string, re.DOTALL)
    if order_match:
        order_content = order_match.group(1)
        # Find all A-->B patterns
        edges = re.findall(r"'([^']+?)'-->'([^']+?)'", order_content)

        for source, target in edges:
            source_sanitized = _sanitize_name(source)
            target_sanitized = _sanitize_name(target)

            # Handle special cases
            if source_sanitized == 'tau' or target_sanitized == 'tau':
                continue  # Skip silent transitions

            # XOR operators need special handling
            if source.startswith('X(') or target.startswith('X('):
                # This is an XOR boundary - connect to/from it
                continue

            # Get node IDs
            source_id = node_map.get(source_sanitized)
            target_id = node_map.get(target_sanitized)

            if source_id and target_id:
                if source_id not in connections:
                    connections[source_id] = {}
                if 'main' not in connections[source_id]:
                    connections[source_id]['main'] = []
                connections[source_id]['main'].append([{"node": target_id, "type": "main", "index": 0}])

    return connections


def generate_temporal_go(powl_string: str, workflow_name: str = "Workflow") -> str:
    """Generate Temporal Go workflow code from POWL model.

    Parameters
    ----------
    powl_string : str
        The POWL model string.
    workflow_name : str
        Name for the Temporal workflow.

    Returns
    -------
    str
        Go code implementing the Temporal workflow.
    """
    activities = _extract_activities(powl_string)
    activity_meta = _get_activity_metadata(powl_string)

    # Generate Go code
    go_code = f'''package workflow

import (
    "context"
    "fmt"
    "go.temporal.io/sdk/workflow"
    "go.temporal.io/sdk/workflow/service"
)

// {workflow_name} workflow
func {workflow_name}(ctx workflow.Context, input WorkflowInput) (WorkflowOutput, error) {{
    var result WorkflowOutput

    // Workflow activities
'''

    # Add activity declarations and calls
    for i, meta in enumerate(activity_meta):
        sanitized = meta['sanitized']
        go_code += f'''
    // Activity {i+1}: {meta['name']}
    {{
        err := workflow.ExecuteActivity(ctx, {sanitized}Activity, input.{sanitized}Input)
        if err != nil {{
            return result, fmt.Errorf("activity {sanitized} failed: %w", err)
        }}
    }}
'''

    # Add closing
    go_code += f'''
    return result, nil
}}

// Activities interface
type {workflow_name}Activities interface {{
'''

    for meta in activity_meta:
        sanitized = meta['sanitized']
        go_code += f'    {sanitized}(ctx context.Context, input interface{{) (interface{{{{}}}}, error)\n'

    go_code += f'''}}

// Register workflow
func init() {{
    workflow.Register({workflow_name})
    service.RegisterOptions(service.Options{{
        Name: "{workflow_name}-task-queue",
    }})
}}
'''

    return go_code


def generate_camunda_bpmn(powl, workflow_name: str = "Process") -> str:
    """Generate Camunda BPMN XML from POWL model.

    This is a wrapper around the existing POWL to BPMN converter.

    Parameters
    ----------
    powl
        The POWL model object.
    workflow_name : str
        Name for the BPMN process.

    Returns
    -------
    str
        BPMN 2.0 XML string.
    """
    from pm4py.objects.conversion.powl.variants.to_bpmn import apply as powl_to_bpmn

    bpmn_graph = powl_to_bpmn(powl)

    # Convert to XML string
    from pm4py.objects.bpmn.exporter import variables as bpmn_exporter
    from io import StringIO

    output = StringIO()
    bpmn_exporter.export_xml(bpmn_graph, output)

    return output.getvalue()


def generate_yawl_xml(powl, specification_name: str = "Process") -> str:
    """Generate YAWL v6 XML from POWL model.

    This is a wrapper around the existing POWL to YAWL converter.

    Parameters
    ----------
    powl
        The POWL model object.
    specification_name : str
        Name for the YAWL specification.

    Returns
    -------
    str
        YAWL XML string.
    """
    from pm4py.objects.conversion.yawl.variants.from_powl import apply as powl_to_yawl

    yawl_spec = powl_to_yawl(powl)

    # Export to XML
    from pm4py.objects.yawl.exporter.exporter import apply as yawl_exporter

    xml_string = yawl_exporter(yawl_spec)

    return xml_string


@dataclass
class CodeGenerationResult:
    """Result of code generation from POWL model."""
    powl_string: str
    n8n_json: Optional[dict] = None
    temporal_go: Optional[str] = None
    camunda_bpmn: Optional[str] = None
    yawl_xml: Optional[str] = None
    errors: List[str] = field(default_factory=list)


def generate_all_orchestrator_code(
    powl_string: str,
    workflow_name: str = "GeneratedWorkflow",
    formats: List[str] = None
) -> CodeGenerationResult:
    """Generate code for all requested orchestrator formats.

    Parameters
    ----------
    powl_string : str
        The POWL model string.
    workflow_name : str
        Base name for the generated workflows.
    formats : list of str, optional
        List of formats to generate. Options: 'n8n', 'temporal', 'bpmn', 'yawl'.
        If None, generates all formats.

    Returns
    -------
    CodeGenerationResult
        Result containing generated code for each requested format.
    """
    if formats is None:
        formats = ['n8n', 'temporal', 'bpmn', 'yawl']

    result = CodeGenerationResult(powl_string=powl_string)

    try:
        # Parse POWL to get model object for BPMN/YAWL conversion
        from pm4py.objects.powl.parser import parse_powl_model_string
        parsed_powl = parse_powl_model_string(powl_string)

        if 'n8n' in formats:
            try:
                result.n8n_json = generate_n8n_json(powl_string, workflow_name)
            except Exception as e:
                result.errors.append(f"n8n generation failed: {str(e)}")

        if 'temporal' in formats:
            try:
                result.temporal_go = generate_temporal_go(powl_string, workflow_name)
            except Exception as e:
                result.errors.append(f"Temporal Go generation failed: {str(e)}")

        if 'bpmn' in formats:
            try:
                result.camunda_bpmn = generate_camunda_bpmn(parsed_powl, workflow_name)
            except Exception as e:
                result.errors.append(f"BPMN generation failed: {str(e)}")

        if 'yawl' in formats:
            try:
                result.yawl_xml = generate_yawl_xml(parsed_powl, workflow_name)
            except Exception as e:
                result.errors.append(f"YAWL generation failed: {str(e)}")

    except Exception as e:
        result.errors.append(f"POWL parsing failed: {str(e)}")

    return result


def generate_from_text(
    process_description: str,
    workflow_name: str = "GeneratedWorkflow",
    formats: List[str] = None,
    model: str = "groq/openai/gpt-oss-20b",
    max_refinements: int = 1
) -> CodeGenerationResult:
    """Generate orchestrator code directly from natural language description.

    This combines NL → POWL generation with code generation in one step.

    Parameters
    ----------
    process_description : str
        Natural language description of the business process.
    workflow_name : str
        Base name for the generated workflows.
    formats : list of str, optional
        List of formats to generate. Options: 'n8n', 'temporal', 'bpmn', 'yawl'.
    model : str
        LLM model identifier for NL → POWL generation.
    max_refinements : int
        Maximum judge-and-refine iterations.

    Returns
    -------
    CodeGenerationResult
        Result containing POWL model and generated code.
    """
    from pm4py.algo.dspy.powl.natural_language import generate_powl_from_text

    # Generate POWL from natural language
    powl_result = generate_powl_from_text(
        process_description=process_description,
        model=model,
        max_refinements=max_refinements
    )

    if not powl_result.get('verdict'):
        result = CodeGenerationResult(powl_string=powl_result.get('powl', ''))
        result.errors.append(f"POWL generation failed: {powl_result.get('reasoning', 'Unknown error')}")
        return result

    # Generate orchestrator code from POWL
    return generate_all_orchestrator_code(
        powl_string=powl_result['powl'],
        workflow_name=workflow_name,
        formats=formats
    )
