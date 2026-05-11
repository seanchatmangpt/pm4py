import warnings

warnings.warn(
    "pm4py.algo.transformation.log_to_features.variants.trace_based is "
    "deprecated; use "
    "pm4py.algo.transformation.trace_encodings.variants.trace_based instead.",
    FutureWarning,
    stacklevel=2,
)

from pm4py.algo.transformation.trace_encodings.variants.trace_based import *  # noqa
