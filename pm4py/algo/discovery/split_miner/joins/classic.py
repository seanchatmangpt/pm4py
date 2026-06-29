"""Removed module — compatibility shim.

``joins.classic`` was an early join discoverer superseded by the
RPST-based SESE join discovery in
``pm4py.algo.discovery.split_miner.joins.sese`` (``SeseJoinsDiscoverer``),
which both Split Miner variants now use.

Use the public API instead::

    pm4py.discover_bpmn_split_miner(log)
"""
raise ImportError(
    "pm4py.algo.discovery.split_miner.joins.classic was removed; use "
    "pm4py.algo.discovery.split_miner.joins.sese.SeseJoinsDiscoverer "
    "(wired automatically). "
    "Use pm4py.discover_bpmn_split_miner(log)."
)
