
# Author: Maximilian Josef Frank (https://orcid.org/0000-0002-0714-7748)

from pm4py.objects.conversion.genetic_matrix.variants import to_petri_net
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    TO_PETRI_NET = to_petri_net


def apply(genetic_matrix, parameters=None, variant=Variants.TO_PETRI_NET):
    """
    Converts a GeneticMatrix to a different type of object

    Parameters
    --------------
    genetic_matrix
        Genetic matrix
    parameters
        Possible parameters of the algorithm
    variant
        Variant of the algorithm:
            - Variants.TO_PETRI_NET
    """
    return exec_utils.get_variant(variant).apply(
        genetic_matrix, parameters=parameters
    )
