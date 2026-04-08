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


# This algorithm was copied at 16/Nov/2018 from
# https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python and applied to activity
# sequences
delimiter = "@"


def length(s):
    return s.count(delimiter) + 1


def enumerateSequence(s):
    list = s.split(delimiter)
    return enumerate(list, 0)


def trace_levenshtein(s1, s2):
    if length(s1) < length(s2):
        return trace_levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if length(s2) == 0:
        return length(s1)

    previous_row = range(length(s2) + 1)
    for i, c1 in enumerateSequence(s1):
        current_row = [i + 1]
        for j, c2 in enumerateSequence(s2):
            insertions = previous_row[
                             j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]
