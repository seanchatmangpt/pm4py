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


def get_corr_hex(num):
    """
    Gets correspondence between a number
    and an hexadecimal string

    Parameters
    -------------
    num
        Number

    Returns
    -------------
    hex_string
        Hexadecimal string
    """
    if num < 10:
        return str(int(num))
    elif num < 11:
        return "A"
    elif num < 12:
        return "B"
    elif num < 13:
        return "C"
    elif num < 14:
        return "D"
    elif num < 15:
        return "E"
    elif num < 16:
        return "F"


def get_transitions_color(count_move_on_model, count_fit):
    """
    Gets the color associated to the transition

    Parameters
    ------------
    count_move_on_model
        Number of move on models
    count_fit
        Number of fit moves

    Returns
    -----------
    color
        Color associated to the transition
    """
    factor = int(
        255.0
        * float(count_fit)
        / float(count_move_on_model + count_fit + 0.00001)
    )
    first = get_corr_hex(int(factor / 16))
    second = get_corr_hex(factor % 16)
    return "#FF" + first + second + first + second


def get_string_from_int_below_255(factor):
    """
    Gets a string from an integer below 255

    Parameters
    ---------------
    factor
        Factor

    Returns
    ---------------
    stru
        Length 2 string
    """
    first = get_corr_hex(int(factor / 16))
    second = get_corr_hex(factor % 16)
    return first + second
