from pm4py.util import constants as pm4_constants

if pm4_constants.ENABLE_INTERNAL_IMPORTS:
    from pm4py.statistics.variants import log, pandas

    import importlib.util
    if importlib.util.find_spec("polars"):
        from pm4py.statistics.variants import polars
