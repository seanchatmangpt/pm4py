from pm4py.statistics.concurrent_activities import log, pandas

import importlib.util
if importlib.util.find_spec("polars"):
    from pm4py.statistics.concurrent_activities import polars
