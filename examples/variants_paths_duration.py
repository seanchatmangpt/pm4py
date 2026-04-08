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


def execute_script():
    log = pm4py.read_xes("../tests/input_data/receipt.xes")
    var_paths_durs = pm4py.get_variants_paths_duration(log)
    print(var_paths_durs.columns)

    # gets for each variant the average times (between all the cases of the given variant)
    # between the activities 'Confirmation of receipt' and 'T02 Check confirmation of receipt'
    df1 = var_paths_durs[(var_paths_durs["concept:name"] == "Confirmation of receipt") & (var_paths_durs["concept:name_2"] == "T02 Check confirmation of receipt")]
    print(df1[["@@variant_column", "@@flow_time"]])

    # gets the paths which are repeated in some variants, along with the number of variants for which they are repeated
    df2 = var_paths_durs[var_paths_durs["@@cumulative_occ_path_column"] == 1]
    print(df2.groupby(["concept:name", "concept:name_2"]).size())


if __name__ == "__main__":
    execute_script()
