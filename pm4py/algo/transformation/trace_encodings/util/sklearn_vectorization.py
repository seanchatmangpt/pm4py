from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.util import exec_utils
from pm4py.algo.transformation.trace_encodings.util.trace_text import (
    log_to_trace_tokens,
)


class Parameters(Enum):
    NGRAM_RANGE = "ngram_range"
    RETURN_SPARSE = "return_sparse"
    VECTORIZER = "vectorizer"
    FIT_VECTORIZER = "fit_vectorizer"


def _ngrams(tokens: List[str], ngram_range: Tuple[int, int]) -> List[str]:
    terms = []
    min_n, max_n = ngram_range
    for n in range(min_n, max_n + 1):
        if n <= 0:
            continue
        for i in range(0, len(tokens) - n + 1):
            terms.append(" >> ".join(tokens[i : i + n]))
    return terms


def apply(
    log: Union[EventLog, EventStream, pd.DataFrame],
    binary: bool = False,
    ngram_range: Tuple[int, int] = (1, 1),
    parameters: Optional[Dict[Any, Any]] = None,
):
    """
    Vectorizes trace token sequences through scikit-learn CountVectorizer.
    """
    if parameters is None:
        parameters = {}

    return_sparse = exec_utils.get_param_value(
        Parameters.RETURN_SPARSE, parameters, False
    )
    vectorizer = exec_utils.get_param_value(
        Parameters.VECTORIZER, parameters, None
    )
    fit_vectorizer = exec_utils.get_param_value(
        Parameters.FIT_VECTORIZER, parameters, True
    )
    ngram_range = exec_utils.get_param_value(
        Parameters.NGRAM_RANGE, parameters, ngram_range
    )

    _, traces = log_to_trace_tokens(log, parameters=parameters)

    if vectorizer is None:
        try:
            from sklearn.feature_extraction.text import CountVectorizer
        except ImportError as exc:
            raise ImportError(
                "The selected trace encoding uses scikit-learn. Please install "
                "scikit-learn to use this variant."
            ) from exc

        vectorizer = CountVectorizer(
            analyzer=lambda tokens: _ngrams(tokens, ngram_range),
            binary=binary,
            lowercase=False,
        )

    if not traces:
        return [], []

    try:
        if fit_vectorizer:
            matrix = vectorizer.fit_transform(traces)
        else:
            matrix = vectorizer.transform(traces)
    except ValueError as exc:
        if "empty vocabulary" not in str(exc):
            raise
        return [[] for _ in traces], []

    feature_names = list(vectorizer.get_feature_names_out())
    data = matrix if return_sparse else matrix.toarray().tolist()

    return data, feature_names


def apply_tfidf(
    log: Union[EventLog, EventStream, pd.DataFrame],
    ngram_range: Tuple[int, int] = (1, 1),
    parameters: Optional[Dict[Any, Any]] = None,
):
    """
    Vectorizes trace token sequences through scikit-learn TfidfVectorizer.
    """
    if parameters is None:
        parameters = {}

    return_sparse = exec_utils.get_param_value(
        Parameters.RETURN_SPARSE, parameters, False
    )
    vectorizer = exec_utils.get_param_value(
        Parameters.VECTORIZER, parameters, None
    )
    fit_vectorizer = exec_utils.get_param_value(
        Parameters.FIT_VECTORIZER, parameters, True
    )
    ngram_range = exec_utils.get_param_value(
        Parameters.NGRAM_RANGE, parameters, ngram_range
    )

    _, traces = log_to_trace_tokens(log, parameters=parameters)

    if vectorizer is None:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
        except ImportError as exc:
            raise ImportError(
                "The selected trace encoding uses scikit-learn. Please install "
                "scikit-learn to use this variant."
            ) from exc

        vectorizer = TfidfVectorizer(
            analyzer=lambda tokens: _ngrams(tokens, ngram_range),
            lowercase=False,
        )

    if not traces:
        return [], []

    try:
        if fit_vectorizer:
            matrix = vectorizer.fit_transform(traces)
        else:
            matrix = vectorizer.transform(traces)
    except ValueError as exc:
        if "empty vocabulary" not in str(exc):
            raise
        return [[] for _ in traces], []

    feature_names = list(vectorizer.get_feature_names_out())
    data = matrix if return_sparse else matrix.toarray().tolist()

    return data, feature_names
