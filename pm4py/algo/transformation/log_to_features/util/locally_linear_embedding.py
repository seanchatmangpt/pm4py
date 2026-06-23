import warnings

warnings.warn(
    "pm4py.algo.transformation.log_to_features.util.locally_linear_embedding "
    "is deprecated; use "
    "pm4py.algo.transformation.trace_encodings.util.locally_linear_embedding "
    "instead.",
    FutureWarning,
    stacklevel=2,
)

from pm4py.algo.transformation.trace_encodings.util.locally_linear_embedding import *  # noqa
