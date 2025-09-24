from pm4py.statistics.traces.generic import common, log, pandas

import importlib.util
if importlib.util.find_spec("polars"):
    from pm4py.statistics.traces.generic import polars
