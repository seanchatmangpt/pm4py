from pm4py.statistics.eventually_follows import log, uvcl, pandas

import importlib.util
if importlib.util.find_spec("polars"):
    from pm4py.statistics.eventually_follows import polars
