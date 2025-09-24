from pm4py.statistics.rework import log, pandas, cases

import importlib.util
if importlib.util.find_spec("polars"):
    from pm4py.statistics.rework import polars
