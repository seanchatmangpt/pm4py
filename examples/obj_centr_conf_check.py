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
    ocel = pm4py.read_ocel("../tests/input_data/ocel/ocel_order_simulated.csv")

    # subset that we consider as normative
    ocel1 = pm4py.sample_ocel_connected_components(ocel, 1)
    # subset that we use to extract the 'normative' behavior
    ocel2 = pm4py.sample_ocel_connected_components(ocel, 1)

    # object-centric DFG from OCEL2
    ocdfg2 = pm4py.discover_ocdfg(ocel2)
    # OTG (object-type-graph) from OCEL2
    otg2 = pm4py.discover_otg(ocel2)
    # ETOT (ET-OT graph) from OCEL2
    etot2 = pm4py.discover_etot(ocel2)

    # conformance checking
    print("== OCDFG")
    diagn_ocdfg = pm4py.conformance_ocdfg(ocel1, ocdfg2)
    print(diagn_ocdfg)

    print("\n\n== OTG")
    diagn_otg = pm4py.conformance_otg(ocel1, otg2)
    print(diagn_otg)

    print("\n\n== ETOT")
    diagn_etot = pm4py.conformance_etot(ocel1, etot2)
    print(diagn_etot)


if __name__ == "__main__":
    execute_script()
