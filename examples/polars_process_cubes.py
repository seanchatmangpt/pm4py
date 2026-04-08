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
import polars as pl
from pm4py.statistics.process_cube.polars import algorithm as process_cube_builder
import traceback


def execute_script():
    dataframe = pm4py.read_xes("../tests/input_data/receipt.xes")
    dataframe = pl.LazyFrame(dataframe)

    # builds a complete feature table, including the case ID as first column
    enriched_df = pl.LazyFrame(pm4py.extract_outcome_enriched_dataframe(dataframe).collect())
    feature_table = pm4py.extract_features_dataframe(enriched_df, include_case_id=True).collect()

    parameters = {}
    parameters["aggregation_function"] = "max"

    try:
        # builds a first process cube
        # let's put as rows the different activities, as columns the different resources, and a value aggregated
        # the total time of the case
        cube_df, cell_case_dict = process_cube_builder.apply(feature_table, x_col="concept:name", y_col="org:resource", agg_col="@@sojourn_time", parameters=parameters)

        print(cube_df)
    except:
        traceback.print_exc()

    try:
        # let's build another process cube!
        # as rows, I want the presence (or not) of the activity 'T06 Determine necessity of stop advice'
        # as columns, I want the channel used to submit the request

        cube_df2, cell_case_dict2 = process_cube_builder.apply(feature_table, x_col="concept:name_T06Determinenecessityofstopadvice", y_col="case:channel", agg_col="@@sojourn_time", parameters=parameters)

        print(cube_df2)
    except:
        traceback.print_exc()

    try:
        # let's try to build another process cube
        # as rows, we divide cases based on their arrival rate (time between start of the current case and the start of the previously started case)
        # as columns, we divide cases based on their finish rate (time between end of the nextly terminated case and the end of the current case)

        cube_df3, cell_case_dict3 = process_cube_builder.apply(feature_table, x_col="@@arrival_rate", y_col="@@finish_rate", agg_col="@@sojourn_time", parameters=parameters)

        print(cube_df3)
    except:
        traceback.print_exc()

    try:
        # let's try to build another process cube
        # as rows, we divide cases based on their arrival rate (time between start of the current case and the start of the previously started case)
        # as columns, we divide cases based on their finish rate (time between end of the nextly terminated case and the end of the current case)

        cube_df3, cell_case_dict3 = process_cube_builder.apply(feature_table, x_col="@@arrival_rate", y_col="@@finish_rate", agg_col="@@sojourn_time", parameters={
            "x_bins": [0, 200000, 500000, 800000, 1000000],
            "y_bins": [0, 300000, 600000, 900000, 1000000]
        })

        print(cube_df3)
    except:
        traceback.print_exc()

    try:
        cube_df4, cell_case_dict4 = process_cube_builder.apply(feature_table, x_col=("@@arrival_rate", "concept:name"), y_col="@@finish_rate", agg_col="@@sojourn_time")

        print(cube_df4)
    except:
        traceback.print_exc()

    try:
        cube_df5, cell_case_dict5 = process_cube_builder.apply(feature_table, x_col=("@@arrival_rate", "@@arrival_rate"), y_col="@@finish_rate", agg_col="@@sojourn_time")

        print(cube_df5)
    except:
        traceback.print_exc()

    try:
        cube_df6, cell_case_dict6 = process_cube_builder.apply(feature_table, x_col=("@@arrival_rate", "@@arrival_rate"), y_col=("@@finish_rate", "@@finish_rate"), agg_col="@@sojourn_time", parameters={
            "x_bins": [[0, 200000, 500000, 800000, 1000000], [0, 250000, 500000, 750000, 1000000]],
            "y_bins": [[0, 300000, 600000, 900000, 1000000], [0, 350000, 650000, 950000, 1000000]]
        })

        print(cube_df6)
    except:
        traceback.print_exc()


if __name__ == "__main__":
    execute_script()
