"""Trace types used by the Split Miner phases."""
from typing import List

# A flat label trace consumed by the Split Miner pipeline. Split Miner
# 2.0 projects each trace onto its ``complete``-event labels and feeds
# the same flat representation through the shared machinery.
LabelTrace = List[str]

# Sentinel labels added to every trace so the resulting BPMN has a single
# start event and a single end event.
START_LABEL = "__start__"
END_LABEL = "__end__"
