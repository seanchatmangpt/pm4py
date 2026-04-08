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
import os
import traceback


def execute_script():
    try:
        ocel = pm4py.read_ocel2("../tests/input_data/ocel/ocel20_example.sqlite")
        pm4py.write_ocel2(ocel, "ocel20_example_bis.sqlite")
        pm4py.write_ocel2(ocel, "ocel20_example_bis.xmlocel")
        ocel = pm4py.read_ocel2("../tests/input_data/ocel/ocel20_example.xmlocel")
        pm4py.write_ocel2(ocel, "ocel20_example_tris.sqlite")
        pm4py.write_ocel2(ocel, "ocel20_example_tris.xmlocel")
    except:
        traceback.print_exc()

    if os.path.exists("ocel20_example_bis.sqlite"):
        os.remove("ocel20_example_bis.sqlite")

    if os.path.exists("ocel20_example_bis.xmlocel"):
        os.remove("ocel20_example_bis.xmlocel")

    if os.path.exists("ocel20_example_tris.sqlite"):
        os.remove("ocel20_example_tris.sqlite")

    if os.path.exists("ocel20_example_tris.xmlocel"):
        os.remove("ocel20_example_tris.xmlocel")


if __name__ == "__main__":
    execute_script()
