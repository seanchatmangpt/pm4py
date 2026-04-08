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
from pm4py.streaming.connectors.windows.click_key_logger import WindowsEventLogger
from pm4py.streaming.util.event_stream_printer import EventStreamPrinter
import time


def execute_script():
    stream = LiveEventStream()
    wel = WindowsEventLogger(stream, screenshots_folder="output")
    printer = EventStreamPrinter()
    stream.register(printer)
    stream.start()
    wel.start()

    print("listening")

    # listen only for 5 seconds
    time.sleep(5)

    wel.stop()
    stream.stop()

    print("stopped")


if __name__ == "__main__":
    execute_script()
