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

from pm4py.streaming.stream.live_event_stream import LiveEventStream
from pm4py.streaming.importer.csv import importer as streaming_csv_importer
from pm4py.streaming.util.event_stream_printer import EventStreamPrinter
import os, time


def execute_script():
    live_event_stream = LiveEventStream()
    event_stream_printer = EventStreamPrinter()
    live_event_stream.register(event_stream_printer)
    live_event_stream.start()
    importer = streaming_csv_importer.apply(os.path.join("..", "tests", "input_data", "running-example.csv"))
    importer.to_event_stream(live_event_stream)
    live_event_stream.stop()


if __name__ == "__main__":
    execute_script()
