from pm4py.algo.discovery.dfg.adapters import pandas

import importlib.util

if importlib.util.find_spec("polars"):
    from pm4py.algo.discovery.dfg.adapters import polars
