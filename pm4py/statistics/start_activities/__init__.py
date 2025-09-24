from pm4py.statistics.start_activities import common, log, pandas

import importlib.util
if importlib.util.find_spec("polars"):
    from pm4py.statistics.start_activities import polars
