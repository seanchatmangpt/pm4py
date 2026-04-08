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


from pm4py.util import deprecation


class Semantics(object):
    @deprecation.deprecated(
        "2.3.0",
        "3.0.0",
        details="this method will be removed, use PetriNetSemantics.is_enabled() instead",
    )
    def is_enabled(self, t, pn, m, **kwargs):
        pass

    @deprecation.deprecated(
        "2.3.0",
        "3.0.0",
        details="this method will be removed, use PetriNetSemantics.fire() instead",
    )
    def execute(self, t, pn, m, **kwargs):
        pass

    @deprecation.deprecated(
        "2.3.0",
        "3.0.0",
        details="this method will be removed, use PetriNetSemantics.fire() instead",
    )
    def weak_execute(self, t, pn, m, **kwargs):
        pass

    @deprecation.deprecated(
        "2.3.0", "3.0.0", details="this method will be removed"
    )
    def enabled_transitions(self, pn, m, **kwargs):
        pass
