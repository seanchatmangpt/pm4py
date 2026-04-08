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


from numpy.random import choice


def pick_transition(et, smap):
    """
    Pick a transition in a set of transitions based on the weights
    specified by the stochastic map

    Parameters
    --------------
    et
        Enabled transitions
    smap
        Stochastic map

    Returns
    --------------
    trans
        Transition chosen according to the weights
    """
    wmap = {ct: smap[ct].get_weight() if ct in smap else 1.0 for ct in et}
    wmap_sv = sum(wmap.values())
    list_of_candidates = []
    probability_distribution = []
    for ct in wmap:
        list_of_candidates.append(ct)
        if wmap_sv == 0:
            probability_distribution.append(1.0 / float(len(wmap)))
        else:
            probability_distribution.append(wmap[ct] / wmap_sv)
    ct = list(choice(et, 1, p=probability_distribution))[0]
    return ct
