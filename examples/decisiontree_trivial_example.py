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

from pm4py.util import ml_utils
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.util import get_class_representation
from pm4py.algo.transformation.log_to_features import algorithm as log_to_features
from examples import examples_conf
import importlib.util


def execute_script():
    log_path = os.path.join("..", "tests", "input_data", "roadtraffic50traces.xes")
    # log_path = os.path.join("..", "tests", "input_data", "receipt.xes")
    log = xes_importer.apply(log_path)
    # now, it is possible to get a default representation of an event log
    data, feature_names = log_to_features.apply(log, variant=log_to_features.Variants.TRACE_BASED)
    # gets classes representation by final concept:name value (end activity)
    target, classes = get_class_representation.get_class_representation_by_str_ev_attr_value_value(log, "concept:name")

    if importlib.util.find_spec("sklearn") and importlib.util.find_spec("graphviz"):
        # mine the decision tree given 'data' and 'target'
        clf = ml_utils.DecisionTreeClassifier(max_depth=7)
        clf.fit(data, target)

        # visualize the decision tree
        from pm4py.visualization.decisiontree import visualizer as dt_vis
        gviz = dt_vis.apply(clf, feature_names, classes, parameters={dt_vis.Variants.CLASSIC.value.Parameters.FORMAT: examples_conf.TARGET_IMG_FORMAT})
        dt_vis.view(gviz)

    # gets classes representation by trace duration (threshold between the two classes = 200D)
    target, classes = get_class_representation.get_class_representation_by_trace_duration(log, 2 * 8640000)

    if importlib.util.find_spec("sklearn") and importlib.util.find_spec("graphviz"):
        # mine the decision tree given 'data' and 'target'
        clf = ml_utils.DecisionTreeClassifier(max_depth=7)
        clf.fit(data, target)

        # visualize the decision tree
        from pm4py.visualization.decisiontree import visualizer as dt_vis
        gviz = dt_vis.apply(clf, feature_names, classes, parameters={dt_vis.Variants.CLASSIC.value.Parameters.FORMAT: examples_conf.TARGET_IMG_FORMAT})
        dt_vis.view(gviz)


if __name__ == "__main__":
    execute_script()
