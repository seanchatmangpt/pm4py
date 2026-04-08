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

import runpy
from os.path import dirname, join
from pathlib import Path
from setuptools import setup, find_packages


# Import only the metadata of the pm4py to use in the setup. We cannot import it directly because
# then we need to import packages that are about to be installed by the setup itself.
meta_path = Path(__file__).parent.absolute() / "pm4py" / "meta.py"
meta = runpy.run_path(str(meta_path))


def read_file(filename):
    with open(join(dirname(__file__), filename)) as f:
        return f.read()


setup(
    name=meta['__name__'],
    version=meta['__version__'],
    description=meta['__doc__'].strip(),
    long_description=read_file('README.md'),
    author=meta['__author__'],
    author_email=meta['__author_email__'],
    py_modules=['pm4py'],
    include_package_data=True,
    packages=[x for x in find_packages() if x.startswith("pm4py")],
    url='https://processintelligence.solutions/',
    license='Apache 2.0',
    install_requires=read_file("requirements.txt").split("\n"),
    extras_require={
        "powl": ["powl>=2.3.3"],
        "healthcare": [],  # Healthcare vertical - no extra dependencies
        "finance": [],    # Finance vertical - no extra dependencies
        "manufacturing": [],  # Manufacturing vertical - no extra dependencies
        "verticals": [],  # All verticals - no extra dependencies
    },
    project_urls={
        'Documentation': 'https://processintelligence.solutions/pm4py/',
        'Source': 'https://github.com/process-intelligence-solutions/pm4py',
        'Tracker': 'https://github.com/process-intelligence-solutions/pm4py/issues',
    }
)
