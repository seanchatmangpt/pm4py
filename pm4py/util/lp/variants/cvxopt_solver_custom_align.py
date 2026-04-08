"""
PM4Py – A Process Mining Library for Python
Copyright (C) 2024 Process Intelligence Solutions

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
"""


import sys
from threading import Lock

from cvxopt import blas
from cvxopt import glpk

LP_LOCK = Lock()

this_options = {}
this_options["LPX_K_MSGLEV"] = 0
this_options["msg_lev"] = "GLP_MSG_OFF"
this_options["show_progress"] = False
this_options["presolve"] = "GLP_ON"
this_options["tol_bnd"] = 10**-5
this_options["tol_piv"] = 10**-5
this_options["obj_ll"] = 10**-5
this_options["obj_ul"] = 10**-5
this_options["obj_ul"] = 10**-5


def custom_solve_lp(c, G, h, A, b):
    with LP_LOCK:
        status, x, z, y = glpk.lp(c, G, h, A, b, options=this_options)

    if status == 'optimal':
        pcost = blas.dot(c, x)
    else:
        pcost = None

    return {'status': status, 'x': x, 'primal objective': pcost}


def apply(c, Aub, bub, Aeq, beq, parameters=None):
    """
    Gets the overall solution of the problem

    Parameters
    ------------
    c
        c parameter of the algorithm
    Aub
        A_ub parameter of the algorithm
    bub
        b_ub parameter of the algorithm
    Aeq
        A_eq parameter of the algorithm
    beq
        b_eq parameter of the algorithm
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    sol
        Solution of the LP problem by the given algorithm
    """
    sol = custom_solve_lp(c, Aub, bub, Aeq, beq)

    return sol


def get_prim_obj_from_sol(sol, parameters=None):
    """
    Gets the primal objective from the solution of the LP problem

    Parameters
    -------------
    sol
        Solution of the ILP problem by the given algorithm
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    prim_obj
        Primal objective
    """
    return sol["primal objective"]


def get_points_from_sol(sol, parameters=None):
    """
    Gets the points from the solution

    Parameters
    -------------
    sol
        Solution of the LP problem by the given algorithm
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    points
        Point of the solution
    """
    if parameters is None:
        parameters = {}

    maximize = parameters["maximize"] if "maximize" in parameters else False
    return_when_none = parameters["return_when_none"] if "return_when_none" in parameters else False
    var_corr = parameters["var_corr"] if "var_corr" in parameters else {}

    if sol and 'x' in sol and sol['x'] is not None:
        return list(sol['x'])
    else:
        if return_when_none:
            if maximize:
                return [sys.float_info.max] * len(list(var_corr.keys()))
            return [sys.float_info.min] * len(list(var_corr.keys()))
