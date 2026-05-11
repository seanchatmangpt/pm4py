import warnings

warnings.warn(
    "pm4py.algo.transformation.to_embeddings.util.similarity is deprecated; "
    "use pm4py.algo.transformation.trace_encodings.util.similarity instead.",
    FutureWarning,
    stacklevel=2,
)

from pm4py.algo.transformation.trace_encodings.util.similarity import *  # noqa
