
from pm4py.algo.anonymization import trace_variant_query
import importlib.util

if importlib.util.find_spec("diffprivlib"):
    # import pripel only if the diffprivlib package is installed
    from pm4py.algo.anonymization import pripel
