import warnings

warnings.warn(
    "pm4py.algo.transformation.log_to_features is deprecated; use "
    "pm4py.algo.transformation.trace_encodings instead.",
    FutureWarning,
    stacklevel=2,
)

from pm4py.algo.transformation.log_to_features import algorithm, variants
