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


from pm4py.objects.petri_net.obj import Marking


class DataMarking(Marking):
    def __init__(self, marking=None):
        Marking.__init__(self, marking)
        self.data_dict = {}

    def __repr__(self):
        # return str([str(p.name) + ":" + str(self.get(p)) for p in self.keys()])
        # The previous representation had a bug, it took into account the order
        # of the places with tokens
        return (
            str(
                [
                    str(p.name) + ":" + str(self.get(p))
                    for p in sorted(list(self.keys()), key=lambda x: x.name)
                ]
            )
            + " "
            + str(self.data_dict)
        )
