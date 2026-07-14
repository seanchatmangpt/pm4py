"""Streaming approximate alignment factory."""

from enum import Enum

from pm4py.streaming.algo.conformance.alignments.variants import approx_iws
from pm4py.util import exec_utils


class Variants(Enum):
    APPROX_IWS = approx_iws


DEFAULT_VARIANT = Variants.APPROX_IWS


def apply(net, im, fm, variant=DEFAULT_VARIANT, parameters=None):
    """Create a streaming alignment object.

    The returned object accepts events through ``receive`` and exposes prefix
    alignments through ``get``.  Call ``finish(case_id)`` when a case ends to
    obtain a complete alignment.
    """
    return exec_utils.get_variant(variant).apply(
        net, im, fm, parameters=parameters
    )
