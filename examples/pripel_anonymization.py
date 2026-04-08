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

import pm4py
from pm4py.algo.anonymization.trace_variant_query import algorithm as trace_variant_query
from pm4py.algo.anonymization.pripel import algorithm as pripel
from pm4py.objects.log.obj import EventLog


def execute_script():
    log = pm4py.read_xes(
        "../tests/input_data/receipt.xes", return_legacy_log_object=True
    )
    log = EventLog(log[0:100])

    epsilon = 0.5
    sacofa_result = trace_variant_query.apply(log=log, variant=trace_variant_query.Variants.SACOFA,
                                              parameters={"epsilon": epsilon, "k": 30, "p": 4})
    anonymized_log = pripel.apply(log=log, trace_variant_query=sacofa_result, epsilon=epsilon)

    dfg, sa, ea = pm4py.discover_dfg(log)
    pm4py.view_dfg(dfg, sa, ea, format="svg")

    dfg, sa, ea = pm4py.discover_dfg(anonymized_log)
    pm4py.view_dfg(dfg, sa, ea, format="svg")


if __name__ == "__main__":
    execute_script()
