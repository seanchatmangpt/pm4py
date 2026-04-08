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
    fea_df = pm4py.extract_features_dataframe(log, include_case_id=True)
    # sets the case ID as index for the dataframe, so a row for a specific case
    # can be retrieved
    fea_df = fea_df.set_index("case:concept:name")
    # identifies the features for the case with identifier "case-10017"
    features_per_case = fea_df.loc["case-10017"].to_dict()
    print(features_per_case)


if __name__ == "__main__":
    execute_script()
