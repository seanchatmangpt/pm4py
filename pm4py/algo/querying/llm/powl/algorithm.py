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

from pm4py.algo.querying.llm.powl.signatures import (
    ExplainPOWL,
    DiscoverPOWLFromDescription,
    ComparePOWLModels,
)


class POWLExplainer(dspy.Module):
    """
    DSPy module to explain a POWL model in plain language using Chain-of-Thought reasoning.
    """

    def __init__(self):
        super().__init__()
        self.explain = dspy.ChainOfThought(ExplainPOWL)

    def forward(self, powl_description: str):
        """
        Explain a POWL model.

        Parameters
        ----------
        powl_description : str
            String representation of the POWL model (from abstract_powl())

        Returns
        -------
        dspy.Prediction
            Prediction object with explanation field
        """
        return self.explain(powl_description=powl_description)


class POWLDiscoverer(dspy.Module):
    """
    DSPy module to discover a POWL model from natural language process description.
    """

    def __init__(self):
        super().__init__()
        self.discover = dspy.ChainOfThought(DiscoverPOWLFromDescription)

    def forward(self, process_description: str):
        """
        Discover a POWL model from a process description.

        Parameters
        ----------
        process_description : str
            Natural language description of the process

        Returns
        -------
        dspy.Prediction
            Prediction object with powl_model_string field
        """
        return self.discover(process_description=process_description)


class POWLComparator(dspy.Module):
    """
    DSPy module to compare two POWL models and identify structural differences.
    """

    def __init__(self):
        super().__init__()
        self.compare = dspy.ChainOfThought(ComparePOWLModels)

    def forward(self, powl_1_description: str, powl_2_description: str):
        """
        Compare two POWL models.

        Parameters
        ----------
        powl_1_description : str
            String representation of the first POWL model
        powl_2_description : str
            String representation of the second POWL model

        Returns
        -------
        dspy.Prediction
            Prediction object with comparison and confidence fields
        """
        return self.compare(
            powl_1_description=powl_1_description,
            powl_2_description=powl_2_description,
        )
