import warnings

warnings.warn(
    "pm4py.algo.transformation.log_to_features.variants.event_based is "
    "deprecated; use "
    "pm4py.algo.transformation.trace_encodings.variants.event_based instead.",
    FutureWarning,
    stacklevel=2,
)

from pm4py.algo.transformation.trace_encodings.variants.event_based import *  # noqa
