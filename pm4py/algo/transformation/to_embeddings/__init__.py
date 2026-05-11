import warnings

warnings.warn(
    "pm4py.algo.transformation.to_embeddings is deprecated; use "
    "pm4py.algo.transformation.trace_encodings instead.",
    FutureWarning,
    stacklevel=2,
)

from pm4py.algo.transformation.to_embeddings import algorithm, variants, util
