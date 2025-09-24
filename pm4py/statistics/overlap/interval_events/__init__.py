from pm4py.statistics.overlap.interval_events import log, pandas

import importlib.util
if importlib.util.find_spec("polars"):
    from pm4py.statistics.overlap.interval_events import polars
