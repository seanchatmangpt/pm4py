from enum import Enum
from typing import Any, Dict, Optional

from pm4py.algo.transformation.ocel.olap.fold.variants import classic
from pm4py.objects.ocel.obj import OCEL
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic


def apply(
    ocel: OCEL,
    variant=Variants.CLASSIC,
    parameters: Optional[Dict[Any, Any]] = None,
) -> OCEL:
    """
    Applies the fold OLAP operation on an object-centric event log,
    collapsing a previously unfolded tuple-style event type back to its
    parent event type. Inverse of unfold.

    Reference: Khayatbashi, Miri, Jalali. "Advancing Object-Centric Process
    Mining with Multi-Dimensional Data Operations." CAiSE Forum 2025
    (arXiv:2412.00393).

    Parameters
    --------------
    ocel
        Object-centric event log
    variant
        Variant of the algorithm to be used, possible values:
        - Variants.CLASSIC
    parameters
        Variant-specific parameters

    Returns
    --------------
    new_ocel
        A new object-centric event log with the folded event type.
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(ocel, parameters=parameters)
