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
import unittest
import importlib.util

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.util import  get_class_representation
from pm4py.algo.transformation.log_to_features import algorithm as log_to_features


class DecisionTreeTest(unittest.TestCase):
    def test_decisiontree_evattrvalue(self):
        if importlib.util.find_spec("sklearn"):
            from pm4py.util import ml_utils
            from pm4py.visualization.decisiontree import visualizer as dt_vis

            # to avoid static method warnings in tests,
            # that by construction of the unittest package have to be expressed in such way
            self.dummy_variable = "dummy_value"
            log_path = os.path.join("input_data", "roadtraffic50traces.xes")
            log = xes_importer.apply(log_path)
            data, feature_names = log_to_features.apply(log, variant=log_to_features.Variants.TRACE_BASED,
                                                        parameters={"str_tr_attr": [], "str_ev_attr": ["concept:name"],
                                                                    "num_tr_attr": [], "num_ev_attr": ["amount"]})
            target, classes = get_class_representation.get_class_representation_by_str_ev_attr_value_value(log,
                                                                                                           "concept:name")
            clf = ml_utils.DecisionTreeClassifier(max_depth=7)
            clf.fit(data, target)
            gviz = dt_vis.apply(clf, feature_names, classes,
                                parameters={dt_vis.Variants.CLASSIC.value.Parameters.FORMAT: "svg"})
            del gviz

    def test_decisiontree_traceduration(self):
        if importlib.util.find_spec("sklearn"):
            from pm4py.util import ml_utils
            from pm4py.visualization.decisiontree import visualizer as dt_vis

            # to avoid static method warnings in tests,
            # that by construction of the unittest package have to be expressed in such way
            self.dummy_variable = "dummy_value"
            log_path = os.path.join("input_data", "roadtraffic50traces.xes")
            log = xes_importer.apply(log_path)
            data, feature_names = log_to_features.apply(log, variant=log_to_features.Variants.TRACE_BASED,
                                                        parameters={"str_tr_attr": [], "str_ev_attr": ["concept:name"],
                                                                    "num_tr_attr": [], "num_ev_attr": ["amount"]})
            target, classes = get_class_representation.get_class_representation_by_trace_duration(log, 2 * 8640000)
            clf = ml_utils.DecisionTreeClassifier(max_depth=7)
            clf.fit(data, target)
            gviz = dt_vis.apply(clf, feature_names, classes,
                                parameters={dt_vis.Variants.CLASSIC.value.Parameters.FORMAT: "svg"})
            del gviz


if __name__ == "__main__":
    unittest.main()
