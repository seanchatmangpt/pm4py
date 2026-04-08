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


import datetime


def apply(dt):
    if dt.endswith("Z"):
        # Z at the end of date means UTC, but that is not ISO format.
        # Replace "Z" with "+00:00" that is also UTC
        dt = dt[:-1] + "+00:00"
    dt0 = dt.split("T")
    datepart = dt0[0].split("-")
    dt2 = dt0[1].split("+")
    hourpart = dt2[0].split(":")
    year = int(datepart[0])
    month = int(datepart[1])
    day = int(datepart[2])
    hour = int(hourpart[0])
    minute = int(hourpart[1])
    sms = hourpart[2].split(".")
    second = int(sms[0])
    if len(sms) > 1:
        microseconds = int(sms[1]) * 1000
    else:
        microseconds = 0

    return datetime.datetime(
        year, month, day, hour, minute, second, microseconds
    )
