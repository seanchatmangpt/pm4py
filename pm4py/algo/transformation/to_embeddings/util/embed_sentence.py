import warnings

warnings.warn(
    "pm4py.algo.transformation.to_embeddings.util.embed_sentence is "
    "deprecated; use "
    "pm4py.algo.transformation.trace_encodings.util.embed_sentence instead.",
    FutureWarning,
    stacklevel=2,
)

from pm4py.algo.transformation.trace_encodings.util.embed_sentence import *  # noqa
