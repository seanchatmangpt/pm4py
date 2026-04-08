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

from pm4py.util.business_hours import BusinessHours
from pm4py.util.dt_parsing.variants import strpfromiso
import datetime
from workalendar.europe import Italy
from pm4py.util import constants


def execute_script():
    ts1 = 100000000
    ts2 = 110000000
    d1 = strpfromiso.fix_naivety(datetime.datetime.fromtimestamp(ts1))
    d2 = strpfromiso.fix_naivety(datetime.datetime.fromtimestamp(ts2))
    print(ts2-ts1)
    # default business hours: all the days of the week except Saturday and Sunday are working days.
    bh1 = BusinessHours(d1, d2, business_hour_slots=constants.DEFAULT_BUSINESS_HOUR_SLOTS)
    print(bh1.get_seconds())
    # let's calculate the business hours using a proper work calendar.
    bh2 = BusinessHours(d1, d2, business_hour_slots=constants.DEFAULT_BUSINESS_HOUR_SLOTS, workcalendar=Italy())
    print(bh2.get_seconds())


if __name__ == "__main__":
    execute_script()
