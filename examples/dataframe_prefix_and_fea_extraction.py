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

from pm4py.objects.log.util import dataframe_utils
from pm4py.util import pandas_utils, constants


def execute_script():
    # loads a dataframe. setup dates
    df = pandas_utils.read_csv("../tests/input_data/receipt.csv")
    df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
    print(df)
    # insert the case index in the dataframe
    df = pandas_utils.insert_ev_in_tr_index(df, case_id="case:concept:name", column_name="@@index_in_trace")
    # filter all the prefixes of length 5 from the dataframe
    df = df[df["@@index_in_trace"] <= 5]
    print(df)
    # performs the automatic feature extraction
    fea_df = dataframe_utils.automatic_feature_extraction_df(df)
    print("\nfea_df =")
    print(fea_df)
    print(fea_df.columns)


if __name__ == "__main__":
    execute_script()
