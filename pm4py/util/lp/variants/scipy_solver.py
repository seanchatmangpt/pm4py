import numpy as np
import warnings
from scipy.optimize import linprog, OptimizeResult
from typing import Optional, Dict, Any, List
from pm4py.util import exec_utils
from threading import Lock
from scipy.optimize import OptimizeWarning


warnings.filterwarnings('ignore', category=OptimizeWarning)
LP_LOCK = Lock()


class Parameters:
    INTEGRALITY = "integrality"
    METHOD = "method"
    BOUNDS = "bounds"


def apply(
        c: list,
        Aub: np.ndarray,
        bub: np.matrix,
        Aeq: np.matrix,
        beq: np.matrix,
        parameters: Optional[Dict[Any, Any]] = None,
) -> OptimizeResult:
    if parameters is None:
        parameters = {}

    integrality = exec_utils.get_param_value(
        Parameters.INTEGRALITY, parameters, None
    )
    method = exec_utils.get_param_value(Parameters.METHOD, parameters, "revised simplex")
    bounds = exec_utils.get_param_value(Parameters.BOUNDS, parameters, None)

    with LP_LOCK:
        sol = linprog(
            c,
            A_ub=Aub,
            b_ub=bub,
            A_eq=Aeq,
            b_eq=beq,
            integrality=integrality,
            bounds=bounds,
            method=method,
        )

    return sol


def get_prim_obj_from_sol(
        sol: OptimizeResult, parameters: Optional[Dict[Any, Any]] = None
) -> Optional[int]:
    if sol is not None and sol.fun is not None:
        return round(sol.fun)
    return None


def get_points_from_sol(
        sol: OptimizeResult, parameters: Optional[Dict[Any, Any]] = None
) -> Optional[List[int]]:
    if sol is not None and sol.x is not None:
        return [round(y) for y in sol.x]
    return None
