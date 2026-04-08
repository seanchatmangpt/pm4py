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

import pm4py
from pm4py.algo.label_splitting import algorithm as label_splitter


def execute_script():
    log = pm4py.read_xes("../tests/input_data/receipt.xes")
    log = log[["case:concept:name", "concept:name", "time:timestamp"]]

    # relabeling with the default options
    rlog1 = label_splitter.apply(log, variant=label_splitter.Variants.CONTEXTUAL)
    print(rlog1)

    # relabeling with a single activity allowed in the prefix and suffix,
    # plus the relabeling only applies to a given activity
    rlog2 = label_splitter.apply(log, variant=label_splitter.Variants.CONTEXTUAL,
                                 parameters={"prefix_length": 1, "suffix_length": 1,
                                             "target_activities": ["Confirmation of receipt"]})
    print(rlog2)


if __name__ == "__main__":
    execute_script()
