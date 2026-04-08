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


def execute_script():
    """
    Example script to discover a DECLARE model from an event log,
    obtain its textual (LLM) abstraction, and perform conformance checking.
    """
    log = pm4py.read_xes("../tests/input_data/receipt.xes")

    declare_model = pm4py.discover_declare(log)
    print(declare_model)

    # prints a textual abstraction of the declare model that can be provided to GPT
    text_abstr = pm4py.llm.abstract_declare(declare_model)
    print(text_abstr)

    # provides conformance checking based on the DECLARE model
    conf_result = pm4py.conformance_declare(log, declare_model, return_diagnostics_dataframe=True)
    print(conf_result)


if __name__ == "__main__":
    execute_script()
