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


import re


ref_stri_1 = "ordabcchr"
ref_stri_2 = "ordabc"

re1 = re.compile(r"([^a-zA-Z0-9]+)")
re2 = re.compile(ref_stri_1)


def mask_non_alphanumeric(stri):
    stri_split = re1.split(stri)
    ret = []
    for el in stri_split:
        for char in el:
            if (
                char.isalnum()
                or char == " "
                or char
                in [
                    "(",
                    ")",
                    "*",
                    ".",
                    ",",
                    "'",
                    '"',
                    "=",
                    "<",
                    ">",
                    "_",
                    "+",
                    "-",
                    "!",
                ]
            ):
                ret.append(char)
            else:
                ret.append(
                    ref_stri_1 + ref_stri_2 + str(ord(char)) + ref_stri_1
                )
    return "".join(ret)


def restore_non_alphanumeric(stri):
    stri_split = re2.split(stri)
    ret = []
    for el in stri_split:
        if el.startswith(ref_stri_2):
            ret.append(chr(int(el[len(ref_stri_2):])))
        else:
            ret.append(el)
    return "".join(ret)
