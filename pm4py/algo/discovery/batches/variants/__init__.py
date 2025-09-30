from pm4py.algo.discovery.batches.variants import pandas, log

import importlib.util

if importlib.util.find_spec("polars"):
    from pm4py.algo.discovery.batches.variants import polars  # type: ignore[F401]
