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
from pm4py.algo.clustering.trace_attribute_driven import algorithm as clust_algorithm


def recursive_print_clusters(cluster_tree, rec_depth=0):
    if rec_depth > 0:
        # print the values belonging to the current part of the tree
        # (this allows filtering the event log on a given part of the tree)
        print("\t"*rec_depth, cluster_tree["name"].split("-"))

    for child in cluster_tree["children"]:
        recursive_print_clusters(child, rec_depth+1)

    if not cluster_tree["children"]:
        # there are no children, explicitly tell that
        print("\t"*(rec_depth+1), "END")


def execute_script():
    log = pm4py.read_xes("../tests/input_data/receipt.xes", return_legacy_log_object=True)
    log = pm4py.sample_cases(log, num_cases=20)
    # perform hierarchical clustering on the 'responsible' attribute of the log
    cluster_tree = clust_algorithm.apply(log, "responsible")[0]
    recursive_print_clusters(cluster_tree)


if __name__ == "__main__":
    execute_script()
