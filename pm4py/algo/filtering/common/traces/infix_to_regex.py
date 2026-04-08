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


from re import escape


def translate_infix_to_regex(infix):
    regex = "^"
    for i, act in enumerate(infix):
        is_last_activity = i == (len(infix) - 1)
        if act == "...":
            if is_last_activity:
                regex = f"{regex[:-1]}(,[^,]*)*"
            else:
                regex = f"{regex}([^,]*,)*"
        else:
            if act:
                act = escape(act)

            if is_last_activity:
                regex = f"{regex}{act}"
            else:
                regex = f"{regex}{act},"

    regex = f"{regex}$"
    return regex
