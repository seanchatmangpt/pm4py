from pm4py.algo.discovery.footprints.log.variants import (
    entire_event_log,
    trace_by_trace,
    entire_dataframe,
)

import importlib.util

if importlib.util.find_spec("polars"):
    from pm4py.algo.discovery.footprints.log.variants import polars_lazyframes  # type: ignore[F401]
