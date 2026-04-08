'''
PM4Py – Finance Demo Data Generators
Copyright (C) 2026 Process Intelligence Solutions GmbH

Generates synthetic trade workflow data for testing, demos, and compliance validation.
Includes realistic trade patterns, risk scenarios, and compliance edge cases.
'''

from typing import List, Dict, Any, Optional, Union, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from pm4py.verticals.finance.schemas import (
    TradeType,
    AssetClass,
    MarketType,
    TRADE_ACTIVITIES,
)


class ScenarioType(Enum):
    """Types of demo scenarios."""
    NORMAL = "normal"  # Standard compliant trades
    HIGH_VOLUME = "high_volume"  # Peak trading period
    RISKY = "risky"  # Potential compliance issues
    CROSS_BORDER = "cross_border"  # Multi-jurisdiction trades
    ALGO_TRADING = "algo_trading"  # Algorithmic trading patterns
    MARKET_CLOSE = "market_close"  # End-of-day rush
    COMPLIANCE_VIOLATIONS = "compliance_violations"  # Intentional violations for testing


@dataclass
class GeneratorConfig:
    """Configuration for trade data generator."""
    n_trades: int = 1000
    n_traders: int = 20
    n_instruments: int = 50
    seed: int = 42
    start_date: Optional[datetime] = None
    variability: float = 0.3
    include_compliance_violations: bool = False
    violation_rate: float = 0.05  # 5% of trades have violations


def generate_trade_workflow(
    config: Optional[GeneratorConfig] = None,
    scenario: ScenarioType = ScenarioType.NORMAL,
    return_dataframe: bool = True,
) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Generate synthetic trade workflow event log.

    Args:
        config: Generator configuration
        scenario: Type of scenario to generate
        return_dataframe: Return DataFrame instead of list of dicts

    Returns:
        Synthetic trade workflow log
    """
    if config is None:
        config = GeneratorConfig()

    np.random.seed(config.seed)

    if config.start_date is None:
        config.start_date = datetime.now() - timedelta(days=30)

    # Adjust parameters based on scenario
    config = _adjust_config_for_scenario(config, scenario)

    # Generate base components
    instruments = _generate_instruments(config.n_instruments)
    traders = [f"TRADER_{i:04d}" for i in range(1, config.n_traders + 1)]
    desks = ["Equities", "Fixed Income", "FX", "Derivatives", "Crypto"]
    venues = [v.value for v in MarketType]

    events = []
    case_id = 0

    trade_types = list(TradeType)
    type_weights = [0.5, 0.3, 0.1, 0.05, 0.03, 0.02]

    for i in range(config.n_trades):
        case_id += 1
        case_id_str = f"ORDER_{case_id:08d}"

        # Determine if this trade should have compliance violations
        has_violations = (
            config.include_compliance_violations and
            np.random.random() < config.violation_rate
        )

        # Select trade attributes
        instrument = np.random.choice(instruments)
        trader = np.random.choice(traders)
        desk = np.random.choice(desks)
        venue = np.random.choice(venues)
        trade_type = np.random.choice(trade_types, p=type_weights)
        side = np.random.choice(["BUY", "SELL"], p=[0.52, 0.48])

        # Generate price
        base_price = _get_price_for_instrument(instrument)
        price = base_price * (1 + np.random.uniform(-0.02, 0.02))

        # Generate quantity
        quantity = np.random.choice([100, 200, 500, 1000, 5000]) * np.random.randint(1, 10)

        # Calculate notional
        notional = quantity * price

        # Generate trade events
        trade_events = _generate_trade_events(
            case_id_str=case_id_str,
            instrument=instrument,
            trader=trader,
            desk=desk,
            venue=venue,
            trade_type=trade_type,
            side=side,
            price=price,
            quantity=quantity,
            notional=notional,
            start_date=config.start_date,
            variability=config.variability,
            has_violations=has_violations,
            scenario=scenario,
        )

        events.extend(trade_events)

    if return_dataframe:
        return pd.DataFrame(events)
    return events


def _adjust_config_for_scenario(
    config: GeneratorConfig,
    scenario: ScenarioType,
) -> GeneratorConfig:
    """Adjust generator config based on scenario type."""
    if scenario == ScenarioType.HIGH_VOLUME:
        config.n_trades = int(config.n_trades * 3)
        config.variability = 0.1  # Lower variability = faster trades

    elif scenario == ScenarioType.RISKY:
        config.include_compliance_violations = True
        config.violation_rate = 0.15  # 15% violation rate

    elif scenario == ScenarioType.ALGO_TRADING:
        config.variability = 0.05  # Very low variability = very fast trades
        config.n_trades = int(config.n_trades * 5)  # More trades

    elif scenario == ScenarioType.MARKET_CLOSE:
        # Concentrate trades near market close
        config.variability = 0.5

    elif scenario == ScenarioType.COMPLIANCE_VIOLATIONS:
        config.include_compliance_violations = True
        config.violation_rate = 0.30  # 30% violation rate for testing

    return config


def _generate_instruments(n: int) -> List[Dict[str, Any]]:
    """Generate list of financial instruments."""
    instruments = []
    asset_templates = [
        ("AAPL", "Apple Inc.", AssetClass.EQUITY, 150.0),
        ("MSFT", "Microsoft Corp.", AssetClass.EQUITY, 300.0),
        ("GOOGL", "Alphabet Inc.", AssetClass.EQUITY, 140.0),
        ("AMZN", "Amazon.com Inc.", AssetClass.EQUITY, 170.0),
        ("TSLA", "Tesla Inc.", AssetClass.EQUITY, 200.0),
        ("NVDA", "NVIDIA Corp.", AssetClass.EQUITY, 600.0),
        ("JPM", "JPMorgan Chase", AssetClass.EQUITY, 160.0),
        ("BAC", "Bank of America", AssetClass.EQUITY, 32.0),
        ("XOM", "Exxon Mobil", AssetClass.EQUITY, 105.0),
        ("CVX", "Chevron Corp.", AssetClass.EQUITY, 145.0),
        ("TLT", "iShares 20+ Year Treasury", AssetClass.FIXED_INCOME, 95.0),
        ("IEF", "iShares 7-10 Year Treasury", AssetClass.FIXED_INCOME, 100.0),
        ("LQD", "iShares Investment Grade Corporate", AssetClass.FIXED_INCOME, 110.0),
        ("HYG", "iShares High Yield Corporate", AssetClass.FIXED_INCOME, 85.0),
        ("EURUSD", "EUR/USD Spot", AssetClass.FX, 1.08),
        ("GBPUSD", "GBP/USD Spot", AssetClass.FX, 1.26),
        ("USDJPY", "USD/JPY Spot", AssetClass.FX, 150.0),
        ("BTCUSD", "Bitcoin/USD", AssetClass.CRYPTO, 45000.0),
        ("ETHUSD", "Ethereum/USD", AssetClass.CRYPTO, 2500.0),
        ("ES", "E-mini S&P 500", AssetClass.DERIVATIVE, 5200.0),
        ("NQ", "E-mini Nasdaq-100", AssetClass.DERIVATIVE, 18000.0),
        ("CL", "Crude Oil WTI", AssetClass.COMMODITY, 80.0),
        ("GC", "Gold Futures", AssetClass.COMMODITY, 2200.0),
        ("SI", "Silver Futures", AssetClass.COMMODITY, 25.0),
        ("ZC", "Corn Futures", AssetClass.COMMODITY, 450.0),
    ]

    # Create base instruments from templates
    for symbol, name, asset_class, base_price in asset_templates:
        instruments.append({
            "symbol": symbol,
            "name": name,
            "asset_class": asset_class,
            "base_price": base_price,
        })

    # Extend to n instruments by creating variants
    while len(instruments) < n:
        template_idx = len(instruments) % len(asset_templates)
        symbol, name, asset_class, base_price = asset_templates[template_idx]
        variant_num = len(instruments) // len(asset_templates) + 1
        instruments.append({
            "symbol": f"{symbol}-{variant_num}",
            "name": f"{name} (Variant {variant_num})",
            "asset_class": asset_class,
            "base_price": base_price * (1 + (variant_num * 0.01)),  # Slightly different price
        })

    return instruments[:n]


def _get_price_for_instrument(instrument: Dict[str, Any]) -> float:
    """Get base price for an instrument."""
    return instrument.get("base_price", 100.0)


def _generate_trade_events(
    case_id_str: str,
    instrument: Dict[str, Any],
    trader: str,
    desk: str,
    venue: str,
    trade_type: TradeType,
    side: str,
    price: float,
    quantity: int,
    notional: float,
    start_date: datetime,
    variability: float,
    has_violations: bool,
    scenario: ScenarioType,
) -> List[Dict[str, Any]]:
    """Generate events for a single trade workflow."""
    events = []

    # Base timestamp for this trade
    base_timestamp = start_date + timedelta(
        days=np.random.randint(0, 30),
        hours=np.random.randint(9, 17),  # Trading hours
        minutes=np.random.randint(0, 60),
        seconds=np.random.randint(0, 60),
        microseconds=np.random.randint(0, 1000000),
    )

    # Define trade workflow activities
    workflow_steps = [
        ("Order Received", 0),
        ("Order Validation", 1),
        ("Risk Check", 2),
        ("Compliance Check", 3),
        ("Order Routing", 4),
        ("Execution", 5),
        ("Execution Report", 6),
        ("Settlement", 7),
        ("Confirmation", 8),
    ]

    # Generate events for each step
    for step_name, step_index in workflow_steps:
        # Add timing variability
        delay_minutes = int(np.random.exponential(variability * 10))
        event_timestamp = base_timestamp + timedelta(minutes=delay_minutes * step_index)

        # Determine if step was skipped (for some scenarios)
        skipped = (
            scenario == ScenarioType.ALGO_TRADING and
            step_index in [1, 2, 3] and  # Skip validation/checks for some algo trades
            np.random.random() < 0.3
        )

        if skipped:
            continue

        event = {
            "case:concept:name": case_id_str,
            "concept:name": step_name,
            "time:timestamp": event_timestamp.isoformat(),
            "trade:Id": case_id_str,
            "trade:instrument": instrument["symbol"],
            "trade:trader": trader,
            "trade:desk": desk,
            "trade:venue": venue,
            "trade:type": trade_type.value,
            "trade:side": side,
            "trade:price": round(price, 4),
            "trade:quantity": quantity,
            "trade:notional": round(notional, 2),
            "trade:asset_class": instrument["asset_class"].value,

            # SOC2 attributes
            "soc2:access_control": "MFA" if not has_violations else "NONE",
            "soc2:encryption": True if not has_violations else False,
            "soc2:audit_log": [f"audit_{case_id_str}"] if not has_violations else [],
            "soc2:change_management": f"CM_{datetime.now().strftime('%Y%m')}",
            "soc2:data_classification": "confidential",
            "soc2:compliance_monitoring": True if not has_violations else False,

            # Regulatory reporting attributes
            "reg:transaction_id": f"TXID_{case_id_str}" if not has_violations else None,
            "reg:execution_timestamp": event_timestamp.isoformat(),
            "reg:venue": round(notional * 0.001, 2) if side == "BUY" else 0,
            "reg:venue_currency": "USD",
            "reg:venue_calculation_method": "mark_to_market",
            "reg:best_execution": True if not has_violations else False,
            "reg:execution_venue": venue,
            "reg:short_selling_indicator": side == "SELL",
        }

        events.append(event)

    return events


def generate_compliance_test_data() -> pd.DataFrame:
    """
    Generate trade data specifically for compliance testing.

    Includes:
    - Fully compliant trades
    - Trades with missing attributes
    - Trades with incomplete audit trails
    - Trades without encryption
    - Trades without best execution
    """
    config = GeneratorConfig(
        n_trades=100,
        n_traders=5,
        n_instruments=10,
        include_compliance_violations=True,
        violation_rate=0.5,  # 50% violations for comprehensive testing
    )

    return generate_trade_workflow(
        config=config,
        scenario=ScenarioType.COMPLIANCE_VIOLATIONS,
        return_dataframe=True,
    )


def generate_high_frequency_trades(n_trades: int = 10000) -> pd.DataFrame:
    """Generate high-frequency trading scenario data."""
    config = GeneratorConfig(
        n_trades=n_trades,
        n_traders=10,
        n_instruments=20,
        variability=0.01,  # Very fast trades
    )

    return generate_trade_workflow(
        config=config,
        scenario=ScenarioType.ALGO_TRADING,
        return_dataframe=True,
    )


def generate_cross_border_trades() -> pd.DataFrame:
    """Generate cross-border trade scenario with multi-jurisdiction requirements."""
    config = GeneratorConfig(
        n_trades=500,
        n_traders=15,
        n_instruments=30,
        include_compliance_violations=True,
        violation_rate=0.10,  # 10% violations (common in cross-border)
    )

    return generate_trade_workflow(
        config=config,
        scenario=ScenarioType.CROSS_BORDER,
        return_dataframe=True,
    )


# Export convenience functions
__all__ = [
    "GeneratorConfig",
    "ScenarioType",
    "generate_trade_workflow",
    "generate_compliance_test_data",
    "generate_high_frequency_trades",
    "generate_cross_border_trades",
]
