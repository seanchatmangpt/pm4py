from pm4py.statistics.attributes import common, log, pandas

import importlib.util
if importlib.util.find_spec("polars"):
    from pm4py.statistics.attributes import polars
