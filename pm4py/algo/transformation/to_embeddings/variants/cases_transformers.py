from pm4py.util import exec_utils, constants, xes_constants
from typing import Optional, Dict, Any, List, Tuple
from pm4py.objects.conversion.log import converter as log_converter
import pandas as pd
from enum import Enum
from sentence_transformers import SentenceTransformer


class Parameters(Enum):
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    EMBEDDING_MODEL = "embedding_model"
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY


def apply(log: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None) -> Tuple[List[str], List[List[float]]]:
    """
    Computes the embeddings of case, concatenating all the values of a specified attribute for the events of the case.

    Parameters
    -----------------
    log
        Pandas dataframe
    Parameters
        Parameters of the algorithm, including:
        - Parameters.CASE_ID_KEY => the case identifier column
        - Parameters.EMBEDDING_MODEL => the embedding to be used (default: all-MiniLM-L6-v2)
        - Parameters.ATTRIBUTE_KEY => the attribute to be used for the concatenation

    Returns
    ----------------
    cases_identifiers
        The list of all the case identifiers
    embeddings_list
        The list of embeddings for the considered cases
    """
    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    embedding_model = exec_utils.get_param_value(Parameters.EMBEDDING_MODEL, parameters,
                                                 constants.DEFAULT_EMBEDDING_MODEL)

    log = log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME)

    cases_identifiers = []
    sentences = []

    model = SentenceTransformer(embedding_model)

    cases = log.groupby(case_id_key)[attribute_key].agg(list)
    cases = cases.to_dict()

    for k, v in cases.items():
        cases_identifiers.append(k)
        sentences.append(" ".join(v))

    embeddings_list = list(model.encode(sentences))

    return cases_identifiers, embeddings_list
