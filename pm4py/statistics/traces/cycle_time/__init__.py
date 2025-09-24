from pm4py.statistics.traces.cycle_time import log, pandas, util

import importlib.util
if importlib.util.find_spec("polars"):
    from pm4py.statistics.traces.cycle_time import polars
