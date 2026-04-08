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


from threading import Lock
from typing import Optional, Dict, Any, Union


class ThreadSafeDict(dict):
    def __init__(self, *args, **kw):
        super(ThreadSafeDict, self).__init__(*args, **kw)
        self.lock = Lock()
        self.itemlist = super(ThreadSafeDict, self).keys()

    def __setitem__(self, key, value):
        # TODO: what should happen to the order if
        #       the key is already in the dict
        self.lock.acquire()
        super(ThreadSafeDict, self).__setitem__(key, value)
        self.lock.release()

    def __iter__(self):
        self.lock.acquire()
        ret = iter(self.itemlist)
        self.lock.release()
        return ret

    def keys(self):
        self.lock.acquire()
        ret = set(self.itemlist)
        self.lock.release()
        return ret

    def values(self):
        self.lock.acquire()
        ret = [self[key] for key in self]
        self.lock.release()
        return ret

    def itervalues(self):
        self.lock.acquire()
        ret = (self[key] for key in self)
        self.lock.release()
        return ret


def apply(parameters: Optional[Dict[Any, Any]] = None):
    return ThreadSafeDict()
