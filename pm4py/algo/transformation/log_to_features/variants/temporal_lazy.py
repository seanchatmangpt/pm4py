import warnings

warnings.warn(
    "pm4py.algo.transformation.log_to_features.variants.temporal_lazy is "
    "deprecated; use "
    "pm4py.algo.transformation.trace_encodings.variants.temporal_lazy instead.",
    FutureWarning,
    stacklevel=2,
)

from pm4py.algo.transformation.trace_encodings.variants.temporal_lazy import *  # noqa
