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


import numpy as np
from typing import List, Union, Optional, Dict, Any
from pm4py.algo.transformation.to_embeddings.util import embed_sentence


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def apply(target_embedding: Union[str, List[float]], embeddings_list: List[List[float]], parameters: Optional[Dict[Any, Any]] = None) -> List[float]:
    """
    Computes the cosine similarity between the embeddings of a target sentence and a list of embeddings
    (at the case or event level)

    Parameters
    -----------------
    target_embedding
        Target sentence (embeddings)
    embeddings_list
        List of embeddings (at the case or event level)
    parameters
        Parameters of the method

    Returns
    ------------------
    similarity_list
        List containing the cosine similarities between each entry and the target sentence
    """
    if parameters is None:
        parameters = {}

    if isinstance(target_embedding, str):
        target_embedding = embed_sentence.apply(target_embedding, parameters=parameters)

    similarity_list = [cosine_similarity(target_embedding, emb) for emb in embeddings_list]

    return similarity_list
