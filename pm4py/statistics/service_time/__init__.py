from pm4py.statistics.service_time import log, pandas

import importlib.util
if importlib.util.find_spec("polars"):
    from pm4py.statistics.service_time import polars
