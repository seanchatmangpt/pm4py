import warnings

warnings.warn(
    "pm4py.algo.transformation.log_to_features.variants.temporal is "
    "deprecated; use "
    "pm4py.algo.transformation.trace_encodings.variants.temporal instead.",
    FutureWarning,
    stacklevel=2,
)

from pm4py.algo.transformation.trace_encodings.variants.temporal import *  # noqa
