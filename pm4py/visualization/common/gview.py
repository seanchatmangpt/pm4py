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


import tempfile

from pm4py.util import vis_utils, constants
from pm4py.visualization.common import dot_util, html
from io import BytesIO
from graphviz import Digraph


def view(gviz, parameters=None):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    if constants.DEFAULT_ENABLE_VISUALIZATIONS_VIEW:
        if constants.DEFAULT_GVIZ_VIEW == "matplotlib_view":
            return matplotlib_view(gviz, parameters=parameters)

        format = str(gviz.format).lower().replace("plain-ext", "html")

        is_dot_installed = dot_util.check_dot_installed()

        if format.startswith("html"):
            html.view(gviz, parameters=parameters)
        elif vis_utils.check_visualization_inside_jupyter():
            vis_utils.view_image_in_jupyter(gviz.render())
        elif format == "gv":
            print(str(gviz))
        else:
            return gviz.view(cleanup=True)


def matplotlib_view(gviz, parameters=None):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    gviz
        Graphviz
    """
    if constants.DEFAULT_ENABLE_VISUALIZATIONS_VIEW:
        format = str(gviz.format).lower()
        is_dot_installed = dot_util.check_dot_installed()

        from pm4py.visualization.common import save
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg

        file_name = tempfile.NamedTemporaryFile(suffix="." + format)
        file_name.close()

        save.save(gviz, file_name.name)

        img = mpimg.imread(file_name.name)
        plt.axis("off")
        plt.tight_layout(pad=0, w_pad=0, h_pad=0)
        plt.imshow(img)
        plt.show()


def serialize_dot(gviz: Digraph, parameters=None) -> bytes:
    """
    Serialize the DOT instructions of a Graphviz object

    Parameters
    --------------
    gviz
        Graphviz object

    Returns
    --------------
    bytes_string
        String containing the DOT instructions
    """
    dot = str(gviz)
    f = BytesIO()
    f.write(dot.encode(constants.DEFAULT_ENCODING))
    return f.getvalue()


def serialize(gviz: Digraph, parameters=None) -> bytes:
    """
    Serialize the image rendered from a Graphviz object

    Parameters
    ---------------
    gviz
        Graphviz object

    Returns
    ---------------
    bytes_string
        String containing the picture
    """
    render = gviz.render(cleanup=True)
    with open(render, "rb") as f1:
        return f1.read()
