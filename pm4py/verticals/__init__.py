'''
PM4Py – Vertical Solutions
Copyright (C) 2026 Process Intelligence Solutions GmbH

Industry-specific process mining templates with pre-built schemas,
compliance rules, and dashboards.

Verticals:
- healthcare: HIPAA-ready patient journey mining
- finance: SOC2-ready trade workflow mining
- manufacturing: IIoT-ready OEE and equipment monitoring
'''
from pm4py.verticals.healthcare import HealthcareVertical
from pm4py.verticals.finance import FinanceVertical
from pm4py.verticals.manufacturing import ManufacturingVertical

__all__ = [
    'HealthcareVertical',
    'FinanceVertical',
    'ManufacturingVertical',
]

VERTICALS = {
    'healthcare': HealthcareVertical,
    'finance': FinanceVertical,
    'manufacturing': ManufacturingVertical,
}


def get_vertical(vertical_name: str):
    """Get a vertical template by name."""
    if vertical_name.lower() not in VERTICALS:
        raise ValueError(f"Unknown vertical: {vertical_name}. Available: {list(VERTICALS.keys())}")
    return VERTICALS[vertical_name.lower()]


def list_verticals():
    """List all available vertical templates."""
    return list(VERTICALS.keys())
