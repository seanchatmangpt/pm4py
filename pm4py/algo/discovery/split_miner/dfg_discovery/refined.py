"""Removed module — compatibility shim.

``dfg_discovery.refined.RefinedDFGDiscoverer`` was the approximate
lifecycle DFG of the earlier Split Miner 2.0. The faithful variant now
builds the directly-follows graph from ``complete`` events via
``pm4py.algo.discovery.split_miner.dtypes.complex_log.parse_complex_log``
(the ``getComplexLog`` port) and reuses the classic DFG discoverer; the
SM2 variant wires this automatically.

Use the public API instead::

    pm4py.discover_bpmn_split_miner(log, variant='sm2')
"""
raise ImportError(
    "pm4py.algo.discovery.split_miner.dfg_discovery.refined was removed. The "
    "faithful SM2 directly-follows graph is now built by "
    "pm4py.algo.discovery.split_miner.dtypes.complex_log.parse_complex_log "
    "and used automatically for variant='sm2'. "
    "Use pm4py.discover_bpmn_split_miner(log, variant='sm2')."
)
