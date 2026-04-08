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


def get_new_char(label, shared_obj):
    """
    Get a new single character describing the activity, for the regex

    Parameters
    ------------
    label
        Label of the transition
    shared_obj
        Shared object
    """
    list_to_avoid = [
        "[",
        "]",
        "(",
        ")",
        "*",
        "+",
        "^",
        "?",
        "\r",
        "\n",
        " ",
        "\t",
        "$",
        '"',
        "!",
        "#",
        "&",
        "%",
        "|",
        ".",
        ",",
        ";",
        "-",
        "'",
        "\\",
        "/",
        "{",
        "}",
        "$",
    ]
    shared_obj.count_char = shared_obj.count_char + 1
    while chr(shared_obj.count_char) in list_to_avoid:
        shared_obj.count_char = shared_obj.count_char + 1
    shared_obj.mapping_dictio[label] = chr(shared_obj.count_char)


class SharedObj:
    def __init__(self):
        self.mapping_dictio = None
        if self.mapping_dictio is None:
            self.mapping_dictio = {}
        self.count_char = 0
