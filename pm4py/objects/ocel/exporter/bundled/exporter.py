from enum import Enum
from typing import Optional, Dict, Any

from pm4py.objects.ocel.exporter.bundled.variants import ocel20
from pm4py.objects.ocel.obj import OCEL
from pm4py.util import exec_utils


class Variants(Enum):
    OCEL20 = ocel20


def apply(
    ocel: OCEL,
    target_path: str,
    variant=Variants.OCEL20,
    parameters: Optional[Dict[Any, Any]] = None,
):
    """
    Exports an OCEL 2.0 log to the bundled CSV/Parquet format.
    """
    return exec_utils.get_variant(variant).apply(
        ocel, target_path, parameters=parameters
    )
