from pm4py.statistics.end_activities import common, log, pandas

import importlib.util
if importlib.util.find_spec("polars"):
    from pm4py.statistics.end_activities import polars
