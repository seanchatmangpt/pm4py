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

from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.util import sampling, sorting, index_attribute
from pm4py.util import constants, pandas_utils
from tests.constants import INPUT_DATA_DIR, OUTPUT_DATA_DIR


class CsvImportExportTest(unittest.TestCase):
    def test_importExportCSVtoXES(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        df = pandas_utils.read_csv(os.path.join(INPUT_DATA_DIR, "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        event_log = log_conversion.apply(df, variant=log_conversion.TO_EVENT_STREAM)
        event_log = sorting.sort_timestamp(event_log)
        event_log = sampling.sample(event_log)
        event_log = index_attribute.insert_event_index_as_event_attribute(event_log)
        log = log_conversion.apply(event_log, variant=log_conversion.Variants.TO_EVENT_LOG)
        log = sorting.sort_timestamp(log)
        log = sampling.sample(log)
        log = index_attribute.insert_trace_index_as_event_attribute(log)
        xes_exporter.apply(log, os.path.join(OUTPUT_DATA_DIR, "running-example-exported.xes"))
        log_imported_after_export = xes_importer.apply(
            os.path.join(OUTPUT_DATA_DIR, "running-example-exported.xes"))
        self.assertEqual(len(log), len(log_imported_after_export))
        os.remove(os.path.join(OUTPUT_DATA_DIR, "running-example-exported.xes"))

    def test_importExportCSVtoCSV(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        df = pandas_utils.read_csv(os.path.join(INPUT_DATA_DIR, "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        event_log = log_conversion.apply(df, variant=log_conversion.TO_EVENT_STREAM)
        event_log = sorting.sort_timestamp(event_log)
        event_log = sampling.sample(event_log)
        event_log = index_attribute.insert_event_index_as_event_attribute(event_log)
        log = log_conversion.apply(event_log, variant=log_conversion.Variants.TO_EVENT_LOG)
        log = sorting.sort_timestamp(log)
        log = sampling.sample(log)
        log = index_attribute.insert_trace_index_as_event_attribute(log)
        event_log_transformed = log_conversion.apply(log, variant=log_conversion.TO_EVENT_STREAM)
        df = log_conversion.apply(event_log_transformed, variant=log_conversion.TO_DATA_FRAME)
        df.to_csv(os.path.join(OUTPUT_DATA_DIR, "running-example-exported.csv"))
        df = pandas_utils.read_csv(os.path.join(OUTPUT_DATA_DIR, "running-example-exported.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        event_log_imported_after_export = log_conversion.apply(df, variant=log_conversion.TO_EVENT_STREAM)
        log_imported_after_export = log_conversion.apply(
            event_log_imported_after_export, variant=log_conversion.Variants.TO_EVENT_LOG)
        self.assertEqual(len(log), len(log_imported_after_export))
        os.remove(os.path.join(OUTPUT_DATA_DIR, "running-example-exported.csv"))


if __name__ == "__main__":
    unittest.main()
