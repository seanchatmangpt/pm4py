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


import importlib
import importlib.util
from typing import Any, Optional, Tuple


def _has_module(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except ModuleNotFoundError:
        return False


def get_rustxes_backend_name() -> Optional[str]:
    if _has_module("r4pm.df"):
        return "r4pm"
    if _has_module("rustxes"):
        return "rustxes"
    return None


def import_rustxes_backend() -> Tuple[Any, str]:
    backend_name = get_rustxes_backend_name()
    if backend_name == "r4pm":
        return importlib.import_module("r4pm.df"), backend_name
    if backend_name == "rustxes":
        return importlib.import_module("rustxes"), backend_name
    raise ImportError("Neither `r4pm` nor `rustxes` is installed.")
