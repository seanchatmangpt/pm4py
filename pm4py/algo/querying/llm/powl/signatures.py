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

try:
    import dspy
except ImportError:
    raise ImportError(
        "DSPy is required for POWL v2 functionality. Install it with: pip install dspy"
    )


class ExplainPOWL(dspy.Signature):
    """Explain a POWL process model in plain language."""
    powl_description: str = dspy.InputField(
        desc="String representation of POWL model (output from abstract_powl())"
    )
    explanation: str = dspy.OutputField(
        desc="Natural language explanation of the model's structure and semantics"
    )


class DiscoverPOWLFromDescription(dspy.Signature):
    """Infer a POWL model string from a natural language process description."""
    process_description: str = dspy.InputField(
        desc="Natural language description of a business process"
    )
    powl_model_string: str = dspy.OutputField(
        desc="POWL model string in the format: PO=(nodes={...}, order={...}) or X(...) or *(...)"
    )


class ComparePOWLModels(dspy.Signature):
    """Compare two POWL models and identify structural differences."""
    powl_1_description: str = dspy.InputField(desc="First POWL model as text")
    powl_2_description: str = dspy.InputField(desc="Second POWL model as text")
    comparison: str = dspy.OutputField(
        desc="Detailed comparison of model structures, differences, and similarities"
    )
    confidence: float = dspy.OutputField(
        desc="Confidence in the comparison (0.0 to 1.0)"
    )
