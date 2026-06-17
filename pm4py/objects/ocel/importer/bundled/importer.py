from enum import Enum
from typing import Optional, Dict, Any

from pm4py.objects.ocel.importer.bundled.variants import ocel20
from pm4py.objects.ocel.obj import OCEL
from pm4py.util import exec_utils


class Variants(Enum):
    OCEL20 = ocel20


def apply(
    file_path: str,
    variant=Variants.OCEL20,
    parameters: Optional[Dict[Any, Any]] = None,
) -> OCEL:
    """
    Imports an OCEL 2.0 log from the bundled CSV/Parquet format.
    """
    return exec_utils.get_variant(variant).apply(file_path, parameters=parameters)
