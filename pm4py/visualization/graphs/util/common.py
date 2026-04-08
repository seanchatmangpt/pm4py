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
import tempfile

from pm4py.util import vis_utils, constants


def get_temp_file_name(format):
    """
    Gets a temporary file name for the image

    Parameters
    ------------
    format
        Format of the target image
    """
    filename = tempfile.NamedTemporaryFile(suffix="." + format)

    name = filename.name

    filename.close()

    return name


def save(temp_file_name, target_path):
    """
    Saves the temporary image associated to the graph to the specified path

    Parameters
    --------------
    temp_file_name
        Path to the temporary file hosting the graph
    target_path
        Path where the image shall eventually be saved
    """
    shutil.copyfile(temp_file_name, target_path)
    return ""


def view(temp_file_name):
    """
    View the graph

    Parameters
    ------------
    temp_file_name
        Path to the temporary file hosting the graph
    """
    if constants.DEFAULT_ENABLE_VISUALIZATIONS_VIEW:
        if constants.DEFAULT_GVIZ_VIEW == "matplotlib_view":
            import matplotlib.pyplot as plt
            import matplotlib.image as mpimg

            img = mpimg.imread(temp_file_name)
            plt.axis("off")
            plt.tight_layout(pad=0, w_pad=0, h_pad=0)
            plt.imshow(img)
            plt.show()
            return
        if vis_utils.check_visualization_inside_jupyter():
            vis_utils.view_image_in_jupyter(temp_file_name)
        else:
            vis_utils.open_opsystem_image_viewer(temp_file_name)


def matplotlib_view(temp_file_name):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    temp_file_name
        Path to the temporary file hosting the graph
    """
    if constants.DEFAULT_ENABLE_VISUALIZATIONS_VIEW:
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg

        img = mpimg.imread(temp_file_name)
        plt.imshow(img)
        plt.show()


def serialize(temp_file_name: str) -> bytes:
    """
    Serializes the graph

    Parameters
    ------------
    temp_file_name
        Path to the temporary file hosting the graph
    """
    with open(temp_file_name, "rb") as f:
        return f.read()
