"""Removed module — compatibility shim.

``pm4py.algo.discovery.split_miner.heuristics`` (``OrSplitHeuristic``,
``ImproperCompletionHeuristic``) belonged to an earlier, approximate
Split Miner 2.0 and was removed when the variant was reworked to
reproduce the reference Java implementation (``MineWithSMTC``) exactly.

* The OR-split heuristic is now an intrinsic stage of the faithful SM2
  pipeline (``pm4py.algo.discovery.split_miner.or_min.or_split``); it
  runs automatically for ``variant='sm2'``.
* The improper-completion heuristic was an approximation with no
  equivalent in the reference tool and has been dropped.

Use the public API instead::

    pm4py.discover_bpmn_split_miner(log, variant='sm2')
"""
raise ImportError(
    "pm4py.algo.discovery.split_miner.heuristics was removed when Split "
    "Miner 2.0 was reworked to faithfully match the reference Java tool. "
    "The OR-split heuristic now runs automatically for variant='sm2'; the "
    "improper-completion heuristic was an approximation and was dropped. "
    "Use pm4py.discover_bpmn_split_miner(log, variant='sm2')."
)
