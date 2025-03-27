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
