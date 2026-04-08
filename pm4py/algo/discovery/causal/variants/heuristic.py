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


from typing import Dict, Tuple


def apply(dfg: Dict[Tuple[str, str], int]) -> Dict[Tuple[str, str], float]:
    """
    Computes a causal graph based on a directly follows graph according to the heuristics miner

    Parameters
    ----------
    dfg: :class:`dict` directly follows relation, should be a dict of the form (activity,activity) -> num of occ.

    Returns
    -------
    :return: dictionary containing all causal relations as keys (with value inbetween -1 and 1 indicating that
    how strong it holds)
    """
    causal_heur = {}
    for f, t in dfg:
        if (f, t) not in causal_heur:
            rev = dfg[(t, f)] if (t, f) in dfg else 0
            causal_heur[(f, t)] = float(
                (dfg[(f, t)] - rev) / (dfg[(f, t)] + rev + 1)
            )
            causal_heur[(t, f)] = -1 * causal_heur[(f, t)]
    return causal_heur
