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



def check_dot_installed():
    """
    Check if Graphviz's dot is installed correctly in the system

    Returns
    -------
    boolean
        Boolean telling if Graphviz's dot is installed correctly
    """
    import subprocess

    try:
        val = subprocess.run(
            ["dot", "-V"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return val.returncode == 0
    except BaseException:
        return False
