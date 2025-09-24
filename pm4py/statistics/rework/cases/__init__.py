from pm4py.statistics.rework.cases import log, pandas

import importlib.util
if importlib.util.find_spec("polars"):
    from pm4py.statistics.rework.cases import polars
