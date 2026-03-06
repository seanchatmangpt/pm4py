from pm4py.objects.oc_causal_net.variants import to_ocpn
from pm4py.util import exec_utils
from enum import Enum

class Variants(Enum):
    TO_OCPN = to_ocpn
    
def apply(oc_causal_net, parameters=None, variant=Variants.TO_OCPN):
    """
    Method for converting from Object-centric Causal Net Object-centric Petri Net

    Parameters
    -----------
    oc_causal_net
        Object-centric Causal net
    parameters
        Parameters of the algorithm
    variant
        Chosen variant of the algorithm:
            - Variants.TO_OCPN

    Returns
    -----------
    OCPetriNet
        Object-centric Petri net converted from the Object-centric Causal Net
    """
    return exec_utils.get_variant(variant).apply(oc_causal_net, parameters=parameters)