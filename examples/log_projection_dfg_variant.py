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
from pm4py.algo.conformance.alignments.dfg.variants import classic as dfg_alignments
from pm4py.algo.conformance.alignments.edit_distance.variants import edit_distance


def execute_script():
    log = pm4py.read_xes("../tests/input_data/receipt.xes", return_legacy_log_object=True)

    filtered_log = pm4py.filter_variants_top_k(log, 1)
    dfg, sa, ea = pm4py.discover_dfg(filtered_log)
    projected_log = dfg_alignments.project_log_on_dfg(log, dfg, sa, ea)
    print(projected_log)

    variant = ('Confirmation of receipt', 'T02 Check confirmation of receipt', 'T04 Determine confirmation of receipt',
               'T05 Print and send confirmation of receipt', 'T06 Determine necessity of stop advice',
               'T10 Determine necessity to stop indication')
    projected_log2 = edit_distance.project_log_on_variant(log, variant)
    print(projected_log2)


if __name__ == "__main__":
    execute_script()
