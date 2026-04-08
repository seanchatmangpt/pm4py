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
import os
from examples import examples_conf
import importlib.util


def execute_script():
    dataframe = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"), return_legacy_log_object=True)

    # define a K-Means with 3 clusters
    from pm4py.util import ml_utils
    clusterer = ml_utils.KMeans(n_clusters=3, random_state=0, n_init="auto")

    for clust_log in pm4py.cluster_log(dataframe, sklearn_clusterer=clusterer):
        print(clust_log)
        process_tree = pm4py.discover_process_tree_inductive(clust_log)

        if importlib.util.find_spec("graphviz"):
            pm4py.view_process_tree(process_tree, format=examples_conf.TARGET_IMG_FORMAT)


if __name__ == "__main__":
    execute_script()
