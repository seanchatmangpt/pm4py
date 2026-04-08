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


import shutil
import os
from pm4py.visualization.common import dot_util, html


def save(gviz, output_file_path, parameters=None):
    """
    Save the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    output_file_path
        Path where the GraphViz output should be saved
    """
    format = os.path.splitext(output_file_path)[1][1:].lower()
    is_dot_installed = dot_util.check_dot_installed()

    if format.startswith("html"):
        html.save(gviz, output_file_path, parameters=parameters)
    elif format == "gv":
        F = open(output_file_path, "w")
        F.write(str(gviz))
        F.close()
    else:
        render = gviz.render(cleanup=True)
        shutil.copyfile(render, output_file_path)
    """elif not is_dot_installed:
        raise Exception("impossible to save formats different from HTML without the Graphviz binary")"""
