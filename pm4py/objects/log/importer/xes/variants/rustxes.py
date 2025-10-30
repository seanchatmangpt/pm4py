from enum import Enum
from pm4py.util import exec_utils, constants
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog
from pm4py.objects.conversion.log import converter as log_converter
import pandas as pd
from copy import copy
from pm4py.util.dt_parsing.variants import strpfromiso
import importlib.util


class Parameters(Enum):
    RETURN_LEGACY_LOG_OBJECT = "return_legacy_log_object"
    RETURN_PL_LAZYFRAME = "return_pl_lazyframe"


def apply(
    log_path: str, parameters: Optional[Dict[Any, Any]] = None
) -> Union[EventLog, pd.DataFrame]:
    if parameters is None:
        parameters = {}

    return_legacy_log_object = exec_utils.get_param_value(
        Parameters.RETURN_LEGACY_LOG_OBJECT, parameters, True
    )
    return_pl_lazyframe = exec_utils.get_param_value(Parameters.RETURN_PL_LAZYFRAME, parameters, False)

    import rustxes

    log = rustxes.import_xes(log_path)
    log = log[0]

    if not return_pl_lazyframe:
        log = log.to_pandas()
        for col in log.columns:
            if "date" in str(log[col].dtype) or "time" in str(log[col].dtype):
                log[col] = strpfromiso.fix_dataframe_column(log[col])
    else:
        import polars as pl

        log = log.lazy()

        schema = log.collect_schema()
        datetime_expressions = []
        for col_name, dtype in schema.items():
            dtype_str = str(dtype).lower()
            if "date" in dtype_str or "time" in dtype_str:
                expr = pl.col(col_name)
                has_timezone = "time_zone=" in dtype_str and "time_zone=none" not in dtype_str
                if constants.ENABLE_DATETIME_COLUMNS_AWARE:
                    expr = (
                        expr.dt.convert_time_zone("UTC")
                        if has_timezone
                        else expr.dt.replace_time_zone("UTC")
                    )
                    datetime_expressions.append(expr.alias(col_name))
                elif has_timezone:
                    datetime_expressions.append(expr.dt.replace_time_zone(None).alias(col_name))
        if datetime_expressions:
            log = log.with_columns(datetime_expressions)

        log = log.collect().lazy()

    if importlib.util.find_spec("cudf") and not return_pl_lazyframe:
        import cudf

        log = cudf.DataFrame(log)

    if return_legacy_log_object:
        this_parameters = copy(parameters)
        this_parameters["stream_postprocessing"] = True

        log = log_converter.apply(
            log,
            variant=log_converter.Variants.TO_EVENT_LOG,
            parameters=this_parameters,
        )

    return log
