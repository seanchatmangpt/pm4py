"""Removed module — compatibility shim.

``concurrency.refined.RefinedConcurrencyOracle`` was the
approximate lifecycle-overlap oracle of the earlier Split Miner 2.0. It
was replaced by the faithful overlap oracle in
``pm4py.algo.discovery.split_miner.concurrency.lifecycle``
(``apply_overlap_concurrency``), which the SM2 variant selects
automatically for genuine lifecycle logs.

Use the public API instead::

    pm4py.discover_bpmn_split_miner(log, variant='sm2')
"""
raise ImportError(
    "pm4py.algo.discovery.split_miner.concurrency.refined was removed. The "
    "faithful lifecycle-overlap oracle now lives in "
    "pm4py.algo.discovery.split_miner.concurrency.lifecycle and is used "
    "automatically for variant='sm2'. "
    "Use pm4py.discover_bpmn_split_miner(log, variant='sm2')."
)
