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



from collections import Counter
from typing import Optional, Dict, Any

from pm4py.algo.discovery.inductive.fall_through.tau_loop import TauLoopUVCL
from pm4py.algo.discovery.powl.inductive.fall_through.strict_tau_loop import (
    POWLStrictTauLoopUVCL,
)
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL


class POWLTauLoopUVCL(POWLStrictTauLoopUVCL, TauLoopUVCL):

    @classmethod
    def _get_projected_log(
        cls, log: UVCL, parameters: Optional[Dict[str, Any]] = None
    ) -> UVCL:
        start_activities = comut.get_start_activities(log)
        proj = Counter()
        for t in log:
            x = 0
            for i in range(1, len(t)):
                if t[i] in start_activities:
                    proj.update({t[x:i]: log[t]})
                    x = i
            proj.update({t[x: len(t)]: log[t]})
        return proj
