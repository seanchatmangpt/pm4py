from collections import Counter
from typing import Tuple, Any, Counter as TCounter


class PerformanceDFG(dict):
    """Dictionary-compatible performance DFG with calculation metadata.

    Performance values are intentionally kept as a regular mapping for
    backwards compatibility.  The optional business-hour schedule lets
    downstream consumers render those values using the same definition of a
    working day that was used during discovery.
    """

    def __init__(self, *args, business_hour_slots=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.business_hour_slots = (
            tuple(tuple(slot) for slot in business_hour_slots)
            if business_hour_slots is not None
            else None
        )

    def copy(self):
        return type(self)(
            self, business_hour_slots=self.business_hour_slots
        )


class DirectlyFollowsGraph:

    def __init__(self, graph=None, start_activities=None, end_activities=None):
        if graph is None:
            graph = {}
        if start_activities is None:
            start_activities = {}
        if end_activities is None:
            end_activities = {}
        self._graph = Counter(graph)
        self._start_activities = Counter(start_activities)
        self._end_activities = Counter(end_activities)

    @property
    def graph(self) -> TCounter[Tuple[Any, Any]]:
        return self._graph

    @property
    def start_activities(self) -> TCounter[Any]:
        return self._start_activities

    @property
    def end_activities(self) -> TCounter[Any]:
        return self._end_activities

    def __repr__(self):
        return repr(self._graph)

    def __str__(self):
        return str(self._graph)

    def __iter__(self):
        yield dict(self.graph)
        yield dict(self.start_activities)
        yield dict(self.end_activities)


DFG = DirectlyFollowsGraph
