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



from pm4py.objects.oc_causal_net.obj import OCCausalNet
import networkx as nx


def create_oc_causal_net(marker_groups):
    """
    Create an object-centric causal net from a list of marker groups.
    Does not consider activity counts or the relative occurrence threshold.
    May mutate the input data.

    Parameters
    ----------
    marker_groups : dict[str, ]
        Dict of marker groups per activity. Syntax::

        {
            "activity_name": {
                "img": [
                    [
                        (activity, object_type, (min_count, max_count), marker_key),
                        // -1 for max_count = inf; 0 for unique marker key
                        ...
                    ],
                    ...
                ],
                "omg": [
                    ...
                ]
            }
            ]
        }

    Returns
    -------
    OCCausalNet
        Object-centric causal net
    """
    # infer activities
    activities = set(marker_groups.keys())

    # get input and output marker groups
    input_marker_groups = {}
    output_marker_groups = {}

    # make all keys=0 unique
    # find max key
    max_key = max(
        [
            key
            for groups in marker_groups.values()
            for group in groups.get("img", []) + groups.get("omg", [])
            for _, _, _, key in group
        ],
        default=0,
    )
    key_counter = max_key + 1

    # give markers with key=0 a unique key and set inf as max count if max count is -1
    for groups in marker_groups.values():
        for group in groups.get("img", []) + groups.get("omg", []):
            for i, (
                related_activity,
                object_type,
                count_range,
                marker_key,
            ) in enumerate(group):
                if marker_key == 0:
                    group[i] = (
                        related_activity,
                        object_type,
                        (
                            count_range
                            if count_range[1] != -1
                            else (count_range[0], float("inf"))
                        ),
                        key_counter,
                    )
                    key_counter += 1
            key_counter = max_key + 1

    for activity, groups in marker_groups.items():
        img = groups.get("img", [])
        omg = groups.get("omg", [])

        if img:
            input_marker_groups[activity] = [
                OCCausalNet.MarkerGroup(
                    markers=[
                        OCCausalNet.Marker(
                            related_activity, object_type, count_range, marker_key
                        )
                        for related_activity, object_type, count_range, marker_key in group
                    ]
                )
                for group in img
            ]
        if omg:
            output_marker_groups[activity] = [
                OCCausalNet.MarkerGroup(
                    markers=[
                        OCCausalNet.Marker(
                            related_activity, object_type, count_range, marker_key
                        )
                        for related_activity, object_type, count_range, marker_key in group
                    ]
                )
                for group in omg
            ]

    # infer arcs from the marker groups
    arcs = dict()
    for activity in activities:
        for group in output_marker_groups.get(activity, []):
            for marker in group.markers:
                related_activity = marker.related_activity
                object_type = marker.object_type
                if activity not in arcs:
                    arcs[activity] = {}
                if related_activity not in arcs[activity]:
                    arcs[activity][related_activity] = {}
                if object_type not in arcs[activity][related_activity]:
                    arcs[activity][related_activity][object_type] = {}
                arcs[activity][related_activity][object_type] = {
                    "object_type": object_type
                }
    # create the dependency graph
    dependency_graph = nx.MultiDiGraph(arcs)

    # create the object-centric causal net
    occn = OCCausalNet(
        dependency_graph,
        output_marker_groups,
        input_marker_groups,
    )
    return occn