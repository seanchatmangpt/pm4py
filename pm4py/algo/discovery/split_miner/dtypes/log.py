"""Trace types used by the Split Miner phases."""
from typing import Any, List, Tuple

# A flat label trace consumed by the classic Split Miner pipeline.
LabelTrace = List[str]
LabelLog = List[LabelTrace]

# A refined event keeps the activity label, the lifecycle phase
# (``start`` or ``end``) and the timestamp. The lifecycle-aware variant
# of the pipeline operates on lists of these.
RefinedEvent = Tuple[str, str, Any]
RefinedTrace = List[RefinedEvent]
RefinedLog = List[RefinedTrace]

# Sentinel labels added to every trace so the resulting BPMN has a single
# start event and a single end event.
START_LABEL = "__start__"
END_LABEL = "__end__"
