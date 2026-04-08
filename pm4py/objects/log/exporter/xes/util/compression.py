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


import gzip
import os
import shutil
import tempfile


# this is ugly, should be done internally in the exporter...
def compress(file):
    """
    Compress a file in-place adding .gz suffix

    Parameters
    -----------
    file
        Uncompressed file

    Returns
    -----------
    compressed_file
        Compressed file path
    """
    extension = file.split(".")[-1] + ".gz"
    fp = tempfile.NamedTemporaryFile(suffix=extension)
    fp.close()
    with open(file, "rb") as f_in:
        with gzip.open(fp.name, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    shutil.move(fp.name, file + ".gz")
    os.remove(file)
    return file
