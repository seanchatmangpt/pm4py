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

from pm4py.util import constants as pm4_constants

if pm4_constants.ENABLE_INTERNAL_IMPORTS:
    from pm4py.objects.powl import *
    from pm4py.objects.powl.extensions import (
        GuardOperator,
        GuardCondition,
        ChoiceRegionWithGuards,
        CancellationScope,
        ExtendedPOWL,
        add_guard_to_choice,
        add_cancellation_scope,
    )
    # Enhanced POWL with frequency, serialization, and graph traversal
    from pm4py.objects.powl.enhanced import (
        EnhancedPOWL,
        EnhancedTransition,
        EnhancedSilentTransition,
        EnhancedFrequentTransition,
        EnhancedStrictPartialOrder,
        EnhancedSequence,
        EnhancedOperatorPOWL,
        EnhancedChoiceGraph,
    )
    # API-compatible compatibility layer
    from pm4py.objects.powl.compat import (
        Activity,
        PartialOrder,
        ChoiceGraph,
        TaggedPOWL,
    )
    from pm4py.objects.powl.types import ModelType
    # Top-level API functions compatible with official POWL package
    from pm4py.objects.powl.api import (
        discover,
        discover_from_dfg,
        discover_from_partially_ordered_log,
        convert_to_bpmn,
        convert_to_petri_net,
        view,
        save_visualization,
    )
