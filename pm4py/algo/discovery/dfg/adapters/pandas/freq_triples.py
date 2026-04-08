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


from pm4py.util import constants, pandas_utils


def get_freq_triples(
    df,
    activity_key="concept:name",
    case_id_glue="case:concept:name",
    timestamp_key="time:timestamp",
    sort_caseid_required=True,
    sort_timestamp_along_case_id=True,
):
    """
    Gets the frequency triples out of a dataframe

    Parameters
    ------------
    df
        Dataframe
    activity_key
        Activity key
    case_id_glue
        Case ID glue
    timestamp_key
        Timestamp key
    sort_caseid_required
        Determine if sort by case ID is required (default: True)
    sort_timestamp_along_case_id
        Determine if sort by timestamp is required (default: True)

    Returns
    -------------
    freq_triples
        Frequency triples from the dataframe
    """
    import pandas as pd

    if sort_caseid_required:
        if sort_timestamp_along_case_id:
            df = df.sort_values([case_id_glue, timestamp_key])
        else:
            df = df.sort_values(case_id_glue)
    df_reduced = df[[case_id_glue, activity_key]]
    # shift the dataframe by 1
    df_reduced_1 = df_reduced.shift(-1)
    # shift the dataframe by 2
    df_reduced_2 = df_reduced.shift(-2)
    # change column names to shifted dataframe
    df_reduced_1.columns = [str(col) + "_2" for col in df_reduced_1.columns]
    df_reduced_2.columns = [str(col) + "_3" for col in df_reduced_2.columns]

    df_successive_rows = pandas_utils.concat(
        [df_reduced, df_reduced_1, df_reduced_2], axis=1
    )
    df_successive_rows = df_successive_rows[
        df_successive_rows[case_id_glue]
        == df_successive_rows[case_id_glue + "_2"]
    ]
    df_successive_rows = df_successive_rows[
        df_successive_rows[case_id_glue]
        == df_successive_rows[case_id_glue + "_3"]
    ]
    all_columns = set(df_successive_rows.columns)
    all_columns = list(
        all_columns
        - set([activity_key, activity_key + "_2", activity_key + "_3"])
    )
    directly_follows_grouping = df_successive_rows.groupby(
        [activity_key, activity_key + "_2", activity_key + "_3"]
    )
    if all_columns:
        directly_follows_grouping = directly_follows_grouping[all_columns[0]]
    freq_triples = directly_follows_grouping.size().to_dict()
    return freq_triples
