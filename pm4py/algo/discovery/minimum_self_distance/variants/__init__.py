from pm4py.algo.discovery.minimum_self_distance.variants import log, pandas

import importlib.util

if importlib.util.find_spec("polars"):
    from pm4py.algo.discovery.minimum_self_distance.variants import polars  # type: ignore[F401]
