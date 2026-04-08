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

import unittest
import pm4py
import os


class OcelFilteringTest(unittest.TestCase):
    def test_ocel_import_csv_export_csv(self):
        input_path = os.path.join("input_data", "ocel", "example_log.csv")
        output_path = os.path.join("test_output_data", "example_log.csv")
        ocel = pm4py.read_ocel(input_path)
        pm4py.write_ocel(ocel, output_path)
        os.remove(output_path)

    def test_ocel_import_csv_export_jsonocel(self):
        input_path = os.path.join("input_data", "ocel", "example_log.csv")
        output_path = os.path.join("test_output_data", "example_log.jsonocel")
        ocel = pm4py.read_ocel(input_path)
        pm4py.write_ocel(ocel, output_path)
        os.remove(output_path)

    def test_ocel_import_csv_export_xmlocel(self):
        input_path = os.path.join("input_data", "ocel", "example_log.csv")
        output_path = os.path.join("test_output_data", "example_log.xmlocel")
        ocel = pm4py.read_ocel(input_path)
        pm4py.write_ocel(ocel, output_path)
        os.remove(output_path)

    def test_ocel_import_jsonocel_export_csv(self):
        input_path = os.path.join("input_data", "ocel", "example_log.jsonocel")
        output_path = os.path.join("test_output_data", "example_log.csv")
        ocel = pm4py.read_ocel(input_path)
        pm4py.write_ocel(ocel, output_path)
        os.remove(output_path)

    def test_ocel_import_jsonocel_export_jsonocel(self):
        input_path = os.path.join("input_data", "ocel", "example_log.jsonocel")
        output_path = os.path.join("test_output_data", "example_log.jsonocel")
        ocel = pm4py.read_ocel(input_path)
        pm4py.write_ocel(ocel, output_path)
        os.remove(output_path)

    def test_ocel_import_jsonocel_export_xmlocel(self):
        input_path = os.path.join("input_data", "ocel", "example_log.jsonocel")
        output_path = os.path.join("test_output_data", "example_log.xmlocel")
        ocel = pm4py.read_ocel(input_path)
        pm4py.write_ocel(ocel, output_path)
        os.remove(output_path)

    def test_ocel_import_xmlocel_export_csv(self):
        input_path = os.path.join("input_data", "ocel", "example_log.xmlocel")
        output_path = os.path.join("test_output_data", "example_log.csv")
        ocel = pm4py.read_ocel(input_path)
        pm4py.write_ocel(ocel, output_path)
        os.remove(output_path)

    def test_ocel_import_xmlocel_export_jsonocel(self):
        input_path = os.path.join("input_data", "ocel", "example_log.xmlocel")
        output_path = os.path.join("test_output_data", "example_log.jsonocel")
        ocel = pm4py.read_ocel(input_path)
        pm4py.write_ocel(ocel, output_path)
        os.remove(output_path)

    def test_ocel_import_xmlocel_export_xmlocel(self):
        input_path = os.path.join("input_data", "ocel", "example_log.xmlocel")
        output_path = os.path.join("test_output_data", "example_log.xmlocel")
        ocel = pm4py.read_ocel(input_path)
        pm4py.write_ocel(ocel, output_path)
        os.remove(output_path)

    def test_ocel_statistic_object_type_activities(self):
        input_path = os.path.join("input_data", "ocel", "example_log.jsonocel")
        ocel = pm4py.read_ocel(input_path)
        pm4py.ocel_object_type_activities(ocel)


    def test_ocel_objects_ot_count(self):
        input_path = os.path.join("input_data", "ocel", "example_log.jsonocel")
        ocel = pm4py.read_ocel(input_path)
        pm4py.ocel_objects_ot_count(ocel)

    def test_ocel_filter_event_attribute(self):
        input_path = os.path.join("input_data", "ocel", "example_log.jsonocel")
        ocel = pm4py.read_ocel(input_path)
        pm4py.filter_ocel_event_attribute(ocel, "ocel:activity", ["Create Order"])


    def test_ocel_filter_object_attribute(self):
        input_path = os.path.join("input_data", "ocel", "example_log.jsonocel")
        ocel = pm4py.read_ocel(input_path)
        pm4py.filter_ocel_object_attribute(ocel, "ocel:type", ["order", "delivery"])

    def test_ocel_filter_object_type_allowed_activities(self):
        input_path = os.path.join("input_data", "ocel", "example_log.jsonocel")
        ocel = pm4py.read_ocel(input_path)
        pm4py.filter_ocel_object_types_allowed_activities(ocel, {"order": {"Create Order"}, "element": {"Create Order"}})

    def test_ocel_filter_start_events(self):
        input_path = os.path.join("input_data", "ocel", "example_log.jsonocel")
        ocel = pm4py.read_ocel(input_path)
        pm4py.filter_ocel_start_events_per_object_type(ocel, "order")

    def test_ocel_filter_end_events(self):
        input_path = os.path.join("input_data", "ocel", "example_log.jsonocel")
        ocel = pm4py.read_ocel(input_path)
        pm4py.filter_ocel_end_events_per_object_type(ocel, "order")

    def test_ocel_filter_object_per_type_count(self):
        input_path = os.path.join("input_data", "ocel", "example_log.jsonocel")
        ocel = pm4py.read_ocel(input_path)
        pm4py.filter_ocel_object_per_type_count(ocel, {"order": 1, "element": 2})

    def test_ocel_filter_timestamp(self):
        input_path = os.path.join("input_data", "ocel", "example_log.jsonocel")
        ocel = pm4py.read_ocel(input_path)
        pm4py.filter_ocel_events_timestamp(ocel, "1981-01-01 00:00:00", "1982-01-01 00:00:00")


if __name__ == "__main__":
    unittest.main()
