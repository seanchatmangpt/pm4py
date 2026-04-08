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


from sentence_transformers import SentenceTransformer
from typing import List, Optional, Dict, Any
from enum import Enum
from pm4py.util import exec_utils, constants


class Parameters(Enum):
    EMBEDDING_MODEL = "embedding_model"


def apply(sentence: str, parameters: Optional[Dict[Any, Any]] = None) -> List[float]:
    """
    Encodes a sentence to embeddings

    Parameters
    ----------
    sentence
        Sentence to be encoded
    parameters
        Parameters of the method, including:
        - Parameters.EMBEDDING_MODEL => embedding model to be used (default: all-MiniLM-L6-v2)

    Returns
    -------
    embeddings
        List of numerical embeddings
    """
    if parameters is None:
        parameters = {}

    embedding_model = exec_utils.get_param_value(Parameters.EMBEDDING_MODEL, parameters,
                                                 constants.DEFAULT_EMBEDDING_MODEL)

    model = SentenceTransformer(embedding_model)

    return model.encode([sentence])[0]
