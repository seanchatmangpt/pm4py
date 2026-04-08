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

"""
Natural Language → POWL → BPMN Example
======================================

Demonstrates the full pipeline:
1. Describe a process in natural language
2. LLM generates a POWL model
3. Dr. van der Aalst Judge verifies structural soundness
4. POWL is converted to BPMN 2.0 XML
5. BPMN can be opened in any BPMN editor (Camunda, Signavio, etc.)

Usage:
    # From natural language string:
    python -m pm4py.cli DiscoverPOWLFromText "A customer orders a product..." output.powl

    # From a text file containing the process description:
    python -m pm4py.cli DiscoverPOWLFromText process_description.txt output.powl

    # Full pipeline: text → BPMN
    python -m pm4py.cli DiscoverPOWLToBPMN "A customer orders a product..." output.bpmn

    # From event log (programmatic discovery):
    python -m pm4py.cli DiscoverPOWL running-example.xes output.powl
"""

import pm4py


def example_hospital():
    """Hospital patient admission → POWL → BPMN."""
    description = """
    A hospital handles patient admissions:
    1. Patient arrives and registers at the front desk.
    2. A nurse triages the patient (assigns urgency level).
    3. If high urgency, go straight to the emergency room.
    4. If low urgency, wait in the lobby then see a doctor.
    5. The doctor may order lab tests (give blood, wait for results).
    6. The doctor reviews results and either prescribes medication or recommends surgery.
    7. If surgery, schedule surgery then recovery.
    8. After treatment, the patient is discharged.
    9. Sometimes patients leave without being seen.
    """

    from pm4py.algo.dspy.powl.natural_language import generate_powl_from_text

    print("=== Hospital Patient Admission ===\n")
    result = generate_powl_from_text(description, max_refinements=1)
    print(f"Verdict: {result['verdict']}")
    print(f"Refinements: {result['refinements']}")
    print(f"\nPOWL Model:\n{result['powl']}")

    # Convert to BPMN
    from pm4py.objects.powl.parser import parse_powl_model_string
    parsed = parse_powl_model_string(result["powl"])
    try:
        bpmn_model = pm4py.convert_to_bpmn(parsed)
    except Exception:
        net, im, fm = pm4py.convert_to_petri_net(parsed)
        bpmn_model = pm4py.convert_to_bpmn(net, im, fm)
    pm4py.write_bpmn(bpmn_model, "hospital_admission.bpmn")
    print(f"\nBPMN written to hospital_admission.bpmn")

    return result


def example_a2a_swarm():
    """Human-in-the-Swarm A2A+MCP → POWL → BPMN."""
    description = """
    Human-in-the-Swarm Multi-Agent Orchestration:
    1. Human submits task to swarm orchestrator.
    2. Orchestrator analyzes task and broadcasts to agents via A2A.
    3. Agents report capabilities via MCP tool discovery.
    4. Orchestrator assigns subtasks based on capabilities.
    5. Agents execute subtasks (may delegate via A2A, request tools via MCP).
    6. Orchestrator monitors heartbeats. If agent silent, escalate to human.
    7. Human decides: reassign, retry, or cancel.
    8. Agents publish results via A2A event broadcast.
    9. Orchestrator aggregates results and performs consistency check.
    10. If inconsistent, agents re-execute until consistent.
    11. Final result submitted to human for approval.
    12. Human approves (archive) or requests revision (re-dispatch with feedback).
    """

    from pm4py.algo.dspy.powl.natural_language import generate_powl_from_text

    print("=== Human-in-the-Swarm A2A+MCP ===\n")
    result = generate_powl_from_text(description, max_refinements=1)
    print(f"Verdict: {result['verdict']}")
    print(f"Refinements: {result['refinements']}")
    print(f"\nPOWL Model:\n{result['powl']}")

    from pm4py.objects.powl.parser import parse_powl_model_string
    parsed = parse_powl_model_string(result["powl"])
    try:
        bpmn_model = pm4py.convert_to_bpmn(parsed)
    except Exception:
        net, im, fm = pm4py.convert_to_petri_net(parsed)
        bpmn_model = pm4py.convert_to_bpmn(net, im, fm)
    pm4py.write_bpmn(bpmn_model, "a2a_swarm.bpmn")
    print(f"\nBPMN written to a2a_swarm.bpmn")

    return result


def example_from_event_log():
    """Event log → POWL (programmatic) → BPMN."""
    log = pm4py.read_xes("tests/input_data/running-example.xes")
    powl_model = pm4py.discover_powl(log)
    bpmn_model = pm4py.convert_to_bpmn(powl_model)
    pm4py.write_bpmn(bpmn_model, "running_example.bpmn")
    print("POWL discovered from running-example.xes, BPMN written to running_example.bpmn")
    return powl_model


if __name__ == "__main__":
    example_hospital()
    print("\n" + "=" * 60 + "\n")
    example_a2a_swarm()
