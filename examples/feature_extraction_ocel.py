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

import os
import pm4py
from pm4py.algo.transformation.ocel.features.events import algorithm as events_feature_extraction
from pm4py.util import pandas_utils, constants


def execute_script():
    ocel = pm4py.read_ocel(os.path.join("..", "tests", "input_data", "ocel", "example_log.jsonocel"))
    # extracts some features on the objects and embed them in a Pandas dataframe
    objects_features_df = pm4py.extract_ocel_features(ocel, "element")
    print(objects_features_df)
    # extracts some features on the events and embed them in a Pandas dataframe
    data_events, feature_names_events = events_feature_extraction.apply(ocel)
    events_features_df = pandas_utils.instantiate_dataframe(data_events, columns=feature_names_events)
    print(events_features_df)


if __name__ == "__main__":
    execute_script()
