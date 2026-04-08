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


import importlib.util


def apply(input_path, validation_path, parameters=None):
    if not importlib.util.find_spec("lxml"):
        raise Exception(
            "please install lxml in order to validate an XMLOCEL file."
        )

    import lxml.etree

    if parameters is None:
        parameters = {}

    xml_file = lxml.etree.parse(input_path)
    xml_validator = lxml.etree.XMLSchema(file=validation_path)
    is_valid = xml_validator.validate(xml_file)
    return is_valid
