import numpy as np
from typing import List


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def apply(target_embedding: List[float], embeddings_list: List[List[float]]) -> List[float]:
    """
    Computes the cosine similarity between the embeddings of a target sentence and a list of embeddings
    (at the case or event level)

    Parameters
    -----------------
    target_embedding
        Target sentence (embeddings)
    embeddings_list
        List of embeddings (at the case or event level)

    Returns
    ------------------
    similarity_list
        List containing the cosine similarities between each entry and the target sentence
    """
    similarity_list = [cosine_similarity(target_embedding, emb) for emb in embeddings_list]

    return similarity_list
