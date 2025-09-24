from pm4py.algo.transformation.ocel.description.variants import variant1, variant2
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any, Tuple, Union
from pm4py.util import exec_utils
from enum import Enum


class Variants(Enum):
    VARIANT1 = variant1
    VARIANT2 = variant2


def apply(
    ocel: OCEL,
    variant=Variants.VARIANT1,
    parameters: Optional[Dict[Any, Any]] = None,
) -> Union[str, Tuple[Tuple[str, ...], Tuple[str, ...]]]:
    """
    Gets a textual representation from an object-centric event log

    Parameters
    --------------
    ocel
        Object-centric event log
    variant
        Variant of the algorithm to be used, possible values:
        - Variants.VARIANT1
        - Variants.VARIANT2
    parameters
        Variant-specific parameters

    Returns
    --------------
    result
        A textual representation of the object-centric event log
        (string or tuple-based, depending on the variant)
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(ocel, parameters=parameters)
