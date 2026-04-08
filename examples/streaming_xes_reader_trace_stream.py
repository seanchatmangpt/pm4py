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

from pm4py.streaming.stream.live_trace_stream import LiveTraceStream
from pm4py.streaming.importer.xes import importer as streaming_xes_importer
from pm4py.streaming.util.trace_stream_printer import TraceStreamPrinter
import os, time


def execute_script():
    live_trace_stream = LiveTraceStream()
    trace_stream_printer = TraceStreamPrinter()
    live_trace_stream.register(trace_stream_printer)
    live_trace_stream.start()
    importer = streaming_xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"),
                                            variant=streaming_xes_importer.Variants.XES_TRACE_STREAM)
    importer.to_trace_stream(live_trace_stream)
    live_trace_stream.stop()


if __name__ == "__main__":
    execute_script()
