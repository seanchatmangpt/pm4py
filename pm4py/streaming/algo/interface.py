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


import abc
from threading import Lock
import traceback


class StreamingAlgorithm(abc.ABC):
    def __init__(self, parameters=None):
        self._lock = Lock()

    @abc.abstractmethod
    def _process(self, event):
        pass

    @abc.abstractmethod
    def _current_result(self):
        pass

    def get(self):
        self._lock.acquire()
        try:
            ret = self._current_result()
        except BaseException:
            traceback.print_exc()
            ret = None
        self._lock.release()
        return ret

    def receive(self, event):
        self._lock.acquire()
        try:
            self._process(event)
        except BaseException:
            traceback.print_exc()
        self._lock.release()
