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



from typing import Set


def pre_set(elem, object_type: str = None) -> Set:
    """
    Returns the set of predecessors of an element (place or transition) in an object-centric Petri net.
    Restricted to predecessors connected using arcs of the object type, if specified.

    Parameters
    ----------
    elem
        Element (place or transition) for which to get the predecessors
    object_type
        Object type to restrict the predecessors to (optional)

    Returns
    -------
    Set
        Set of predecessor elements (places or transitions) of the specified object type.
    """
    pre = set()
    for a in elem.in_arcs:
        if object_type is None or a.object_type == object_type:
            pre.add(a.source)
    return pre

def post_set(elem, object_type: str = None) -> Set:
    """
    Returns the set of successors of an element (place or transition) in an object-centric Petri net.
    Restricted to successors connected using arcs of the object type, if specified.

    Parameters
    ----------
    elem
        Element (place or transition) for which to get the successors
    object_type
        Object type to restrict the successors to (optional)

    Returns
    -------
    Set
        Set of successor elements (places or transitions) of the specified object type.
    """
    post = set()
    for a in elem.out_arcs:
        if object_type is None or a.object_type == object_type:
            post.add(a.target)
    return post