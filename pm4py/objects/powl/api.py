"""
Top-level API functions compatible with official POWL package.

Provides discover(), convert_to_bpmn(), convert_to_petri_net(), view(),
and save_visualization() functions that delegate to PM4Py's existing
implementation.

All functions are independently implemented to maintain Apache 2.0 license compatibility.
"""
'''
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see this software project's root or
visit <https://www.gnu.org/licenses/>.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
'''



from typing import Any, Dict, Optional, Union
from pathlib import Path

# Import PM4Py's existing functions
from pm4py.discovery import discover_powl
from pm4py import convert as pm4py_convert
from pm4py.visualization.powl import visualizer as pm4py_powl_visualizer

# Import PM4Py's event log types
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.objects.powl.obj import POWL
import pandas as pd


def discover(
    log: Union[EventLog, EventStream, pd.DataFrame, str],
    variant: Optional[str] = None,
    **kwargs
) -> POWL:
    """
    Discover a POWL model from an event log.

    Shim for powl.discover() - wraps pm4py.discover_powl().

    Args:
        log: Event log (EventLog, EventStream, DataFrame, or file path)
        variant: Discovery variant (default: maximal)
        **kwargs: Additional arguments passed to discover_powl()

    Returns:
        Discovered POWL model
    """
    return discover_powl(log, variant=variant, **kwargs)


def discover_from_dfg(
    dfg: Dict[Tuple[str, str], int],
    start_activities: Dict[str, int],
    end_activities: Dict[str, int],
    activities: Dict[str, int],
    **kwargs
) -> POWL:
    """
    Discover a POWL model from a directly-follows graph.

    Args:
        dfg: Directly-follows graph (edges with frequencies)
        start_activities: Start activities with frequencies
        end_activities: End activities with frequencies
        activities: All activities with frequencies
        **kwargs: Additional arguments

    Returns:
        Discovered POWL model
    """
    from pm4py.discovery import discover_powl_dfg
    return discover_powl_dfg(dfg, start_activities, end_activities, activities, **kwargs)


def discover_from_partially_ordered_log(
    log: Union[EventLog, EventStream],
    **kwargs
) -> POWL:
    """
    Discover a POWL model from a partially ordered event log.

    Args:
        log: Partially ordered event log
        **kwargs: Additional arguments

    Returns:
        Discovered POWL model
    """
    # PM4Py has a specific function for partially ordered logs
    from pm4py.discovery import discover_powl_from_partially_ordered_log
    return discover_powl_from_partially_ordered_log(log, **kwargs)


def convert_to_bpmn(
    powl_model: POWL,
    **kwargs
) -> str:
    """
    Convert a POWL model to BPMN 2.0 XML.

    Shim for powl.convert_to_bpmn() - wraps pm4py.convert().

    Args:
        powl_model: POWL model to convert
        **kwargs: Additional arguments

    Returns:
        BPMN 2.0 XML string
    """
    return pm4py_convert(powl_model, target='bpmn', **kwargs)


def convert_to_petri_net(
    powl_model: POWL,
    **kwargs
) -> tuple:
    """
    Convert a POWL model to a Petri net.

    Shim for powl.convert_to_petri_net() - wraps pm4py.convert().

    Args:
        powl_model: POWL model to convert
        **kwargs: Additional arguments

    Returns:
        Tuple of (net, initial_marking, final_marking)
    """
    return pm4py_convert(powl_model, target='petri_net', **kwargs)


def view(
    powl_model: POWL,
    **kwargs
) -> None:
    """
    Visualize a POWL model.

    Shim for powl.view() - wraps pm4py visualization.

    Args:
        powl_model: POWL model to visualize
        **kwargs: Additional arguments (format, bgcolor)
    """
    # Generate SVG content
    svg_content = pm4py_powl_visualizer.apply(powl_model, **kwargs)
    # View the SVG
    pm4py_powl_visualizer.view(svg_content, **kwargs)


def save_visualization(
    powl_model: POWL,
    file_path: str,
    **kwargs
) -> None:
    """
    Save a POWL model visualization to file.

    Shim for powl.save_visualization() - wraps pm4py visualization.

    Args:
        powl_model: POWL model to visualize
        file_path: Output file path
        **kwargs: Additional arguments (format, bgcolor)
    """
    # Generate SVG content
    svg_content = pm4py_powl_visualizer.apply(powl_model, **kwargs)
    # Save the SVG
    pm4py_powl_visualizer.save(svg_content, file_path, **kwargs)


__all__ = [
    "discover",
    "discover_from_dfg",
    "discover_from_partially_ordered_log",
    "convert_to_bpmn",
    "convert_to_petri_net",
    "view",
    "save_visualization",
]
