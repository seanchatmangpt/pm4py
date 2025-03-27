from pm4py.util import exec_utils, constants, xes_constants
from typing import Optional, Dict, Any, List
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.obj import EventLog
import pandas as pd
from enum import Enum
from sentence_transformers import SentenceTransformer


class Parameters(Enum):
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    EMBEDDING_MODEL = "embedding_model"
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY


def apply(log: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, List[float]]:
    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    embedding_model = exec_utils.get_param_value(Parameters.EMBEDDING_MODEL, parameters, 'all-MiniLM-L6-v2')

    log = log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME)

    cases_identifiers = []
    sentences = []

    model = SentenceTransformer(embedding_model)

    cases = log.groupby(case_id_key)[attribute_key].agg(list)
    cases = cases.to_dict()

    for k, v in cases.items():
        cases_identifiers.append(k)
        sentences.append(" ".join(v))

    embeddings_list = model.encode(sentences)

    return cases_identifiers, embeddings_list
