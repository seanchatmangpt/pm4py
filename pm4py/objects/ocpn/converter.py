from pm4py.objects.ocpn.variants import to_oc_causal_net, to_alternative_format
from pm4py.util import exec_utils
from enum import Enum

class Variants(Enum):
    TO_OC_CAUSAL_NET = to_oc_causal_net
    TO_ALTERNATIVE_FORMAT =  to_alternative_format
    
def apply(ocpn, parameters=None, variant=Variants.TO_OC_CAUSAL_NET):
    """
    Method for converting an Object-centric Petri Net to Object-centric Causal Net

    Parameters
    -----------
    ocpn: OCPetriNet
        Object-centric Petri net
    parameters: dict, optional
        Parameters of the algorithm
    variant
        Chosen variant of the algorithm

    Returns
    -----------
    Conversion result
    """
    return exec_utils.get_variant(variant).apply(ocpn, parameters=parameters)