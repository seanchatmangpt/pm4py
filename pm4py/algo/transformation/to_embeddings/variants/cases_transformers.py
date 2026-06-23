import warnings

warnings.warn(
    "pm4py.algo.transformation.to_embeddings.variants.cases_transformers is "
    "deprecated; use "
    "pm4py.algo.transformation.trace_encodings.variants.cases_transformers "
    "instead.",
    FutureWarning,
    stacklevel=2,
)

from pm4py.algo.transformation.trace_encodings.variants.cases_transformers import *  # noqa
