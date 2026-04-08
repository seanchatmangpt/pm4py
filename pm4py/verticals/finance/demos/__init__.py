'''
PM4Py – Finance Demo Data Generator
Copyright (C) 2026 Process Intelligence Solutions GmbH

Generates synthetic trade workflow data for testing and demos.
'''

from typing import List, Dict, Any, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from pm4py.verticals.finance.schemas import (
    TradeType,
    AssetClass,
    MarketType,
    TRADE_ACTIVITIES,
    TradeEvent,
)


def generate_synthetic_trade_data(
    n_trades: int = 1000,
    n_traders: int = 20,
    n_instruments: int = 50,
    seed: int = 42,
    return_dataframe: bool = True,
    start_date: Optional[datetime] = None,
    variability: float = 0.3,
) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Generate synthetic trade workflow event log.

    Creates realistic trade workflows with:
    - Proper activity sequences (order receipt → execution → settlement)
    - Realistic timing distributions
    - SOC2-compliant attributes
    - Regulatory reporting fields
    - Risk indicators

    :param n_trades: Number of trades to generate
    :param n_traders: Number of traders to simulate
    :param n_instruments: Number of financial instruments
    :param seed: Random seed for reproducibility
    :param return_dataframe: Return DataFrame instead of list of dicts
    :param start_date: Start date for events (default: 30 days ago)
    :param variability: Timing variability (0-1)
    :return: Synthetic trade workflow log
    """
    np.random.seed(seed)

    if start_date is None:
        start_date = datetime.now() - timedelta(days=30)

    # Generate instruments
    instruments = _generate_instruments(n_instruments)

    # Generate traders
    traders = [f"TRADER_{i:04d}" for i in range(1, n_traders + 1)]

    # Generate desks
    desks = ["Equities", "Fixed Income", "FX", "Derivatives", "Crypto"]

    # Generate venues
    venues = [v.value for v in MarketType]

    # Generate trades
    events = []
    case_id = 0

    # Trade type weights
    trade_types = list(TradeType)
    type_weights = [0.5, 0.3, 0.1, 0.05, 0.03, 0.02]  # Market and Limit are most common

    for _ in range(n_trades):
        case_id += 1
        case_id_str = f"ORDER_{case_id:08d}"

        # Select trade attributes
        instrument = np.random.choice(instruments)
        trader = np.random.choice(traders)
        desk = np.random.choice(desks)
        venue = np.random.choice(venues)
        trade_type = np.random.choice(trade_types, p=type_weights)
        side = np.random.choice(["BUY", "SELL"], p=[0.52, 0.48])

        # Generate price based on instrument
        base_price = _get_price_for_instrument(instrument)
        price = base_price * (1 + np.random.uniform(-0.02, 0.02))

        # Generate quantity
        quantity = np.random.choice([100, 200, 500, 1000, 5000]) * np.random.randint(1, 10)

        # Calculate notional
        notional = quantity * price

        # Generate trade events following the workflow
        current_time = start_date + timedelta(
            hours=np.random.randint(0, 24 * 30),
            minutes=np.random.randint(0, 60),
            seconds=np.random.randint(0, 60),
            microseconds=np.random.randint(0, 1000000),
        )

        # Generate unique trade ID
        trade_id = f"TRADE_{case_id:08d}_{np.random.randint(100000, 999999)}"

        # Generate transaction ID for regulatory reporting
        transaction_id = f"TX_{datetime.now().strftime('%Y%m%d')}_{case_id:08d}"

        # Compliance check results (mostly passing)
        pre_trade_check = np.random.choice([True, True, True, False])  # 75% pass
        post_trade_verify = np.random.choice([True, True, True, True, False])  # 80% pass
        limit_check = np.random.choice([True, True, True, True, False])  # 80% pass

        # Best execution indicator
        best_execution = np.random.choice([True, True, True, False])  # 75% pass

        # Revenue sharing indicator
        revenue_share = np.random.choice([True, False, False, False])  # 25% have revenue sharing

        # Generate events for the trade lifecycle
        activities = [
            ("order_received", 0),
            ("order_validation", 1),
            ("pre_trade_compliance", 2),
            ("risk_check", 3),
            ("order_routing", 5),
            ("order_submission", 10),
            ("execution", 15),
            ("trade_confirmation", 20),
            ("post_trade_verification", 25),
            ("trade_reporting", 30),
            ("settlement_instruction", 35),
            ("clearing", 60),  # T+1 or T+2
            ("settlement", 120),  # T+2
        ]

        # Add randomness to timing
        for activity, base_offset in activities:
            offset = base_offset * (1 + np.random.uniform(-variability, variability))
            event_time = current_time + timedelta(seconds=offset)

            events.append({
                "case:concept:name": case_id_str,
                "concept:name": activity,
                "time:timestamp": event_time,
                "lifecycle:transition": "complete",
                "trade:Id": trade_id,
                "trade:instrument": instrument,
                "trade:asset_class": _get_asset_class_for_instrument(instrument),
                "trade:type": trade_type.value,
                "trade:side": side,
                "trade:quantity": quantity if activity == "execution" else None,
                "trade:price": price if activity == "execution" else None,
                "trade:notional": notional if activity == "execution" else None,
                "org:trader": trader,
                "org:desk": desk,
                "org:approver": f"APPROVER_{np.random.randint(1, 10):03d}" if activity in ["order_validation", "post_trade_verification"] else None,
                "market:venue": venue if activity in ["order_submission", "execution"] else None,
                "market:session": _get_session_for_time(event_time),
                "compliance:pre_trade_check": pre_trade_check if activity == "pre_trade_compliance" else None,
                "compliance:post_trade_verify": post_trade_verify if activity == "post_trade_verification" else None,
                "risk:limit_check": limit_check if activity == "risk_check" else None,
                "risk:limit_breach": not limit_check if activity == "risk_check" else None,
                "risk:var_contribution": round(notional * np.random.uniform(0.001, 0.01), 2) if activity == "execution" else None,
                "reg:transaction_id": transaction_id if activity in ["execution", "trade_reporting"] else None,
                "reg:execution_timestamp": event_time.isoformat() if activity == "execution" else None,
                "reg:revenue": round(notional * np.random.uniform(0.0001, 0.001), 2) if activity == "execution" else None,
                "reg:revenue_currency": "USD",
                "reg:revenue_calculation_method": "mark_to_market",
                "reg:best_execution": best_execution if activity == "execution" else None,
                "reg:revenue_share_indicators": revenue_share if activity == "execution" else None,
                "reg:execution_venue": venue if activity == "execution" else None,
                "reg:short_selling_indicator": side == "SHORT" if activity == "execution" else None,
                # SOC2 attributes
                "soc2:access_control": np.random.choice(["MFA", "RBAC", "SAML"]),
                "soc2:encryption": True,
                "soc2:audit_log": f"[{event_time.isoformat()}] {activity} by {trader}",
                "soc2:change_management": f"CHANGE_SET_{np.random.randint(1000, 9999)}",
                "soc2:data_classification": np.random.choice(["internal", "confidential", "restricted"], p=[0.7, 0.2, 0.1]),
                "soc2:compliance_monitoring": True,
            })

        # Randomly add cancellations/rejections (5% of trades)
        if np.random.random() < 0.05:
            cancellation_time = current_time + timedelta(seconds=np.random.randint(30, 300))
            cancel_reason = np.random.choice(["Client request", "Market conditions", "Risk limit"])

            events.append({
                "case:concept:name": case_id_str,
                "concept:name": "order_cancellation",
                "time:timestamp": cancellation_time,
                "lifecycle:transition": "complete",
                "trade:Id": trade_id,
                "trade:instrument": instrument,
                "org:trader": trader,
                "org:desk": desk,
                "market:venue": venue,
                "soc2:access_control": "MFA",
                "soc2:encryption": True,
                "soc2:audit_log": f"[{cancellation_time.isoformat()}] Order cancelled: {cancel_reason}",
            })

    # Create DataFrame
    df = pd.DataFrame(events)

    # Clean up None values
    df = df.replace({None: np.nan})

    # Ensure proper datetime
    df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])

    # Convert to EventLog if requested
    if not return_dataframe:
        from pm4py.conversion import convert_to_event_log
        return convert_to_event_log(df)

    return df


def _generate_instruments(n: int) -> List[str]:
    """Generate synthetic instrument symbols."""
    instruments = []

    # Equities
    equity_prefixes = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "BAC", "WMT"]
    for i in range(min(n // 2, len(equity_prefixes))):
        instruments.append(equity_prefixes[i])

    # Additional equities
    for i in range(max(0, n // 2 - len(equity_prefixes))):
        instruments.append(f"STOCK{i+100:04d}")

    # FX pairs
    fx_pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD"]
    instruments.extend(fx_pairs[:min(n - len(instruments), len(fx_pairs))])

    # Crypto
    cryptos = ["BTC/USD", "ETH/USD", "SOL/USD"]
    instruments.extend(cryptos[:min(n - len(instruments), len(cryptos))])

    # Fill remaining with generic instruments
    while len(instruments) < n:
        instruments.append(f"INST_{len(instruments)+1:04d}")

    return instruments[:n]


def _get_price_for_instrument(instrument: str) -> float:
    """Get base price for an instrument."""
    # Equity prices
    equity_prices = {
        "AAPL": 175.0,
        "MSFT": 380.0,
        "GOOGL": 140.0,
        "AMZN": 175.0,
        "TSLA": 240.0,
        "META": 500.0,
        "NVDA": 875.0,
        "JPM": 195.0,
        "BAC": 35.0,
        "WMT": 165.0,
    }

    if instrument in equity_prices:
        return equity_prices[instrument]

    # FX prices
    if "/" in instrument:
        return 1.0 + np.random.uniform(-0.1, 0.1)

    # Crypto prices
    if "BTC" in instrument:
        return 65000.0
    elif "ETH" in instrument:
        return 3500.0
    elif "SOL" in instrument:
        return 145.0

    # Default
    return 100.0


def _get_asset_class_for_instrument(instrument: str) -> str:
    """Get asset class for an instrument."""
    if "/" in instrument:
        return AssetClass.FX.value
    elif "BTC" in instrument or "ETH" in instrument or "SOL" in instrument:
        return AssetClass.CRYPTO.value
    elif any(x in instrument for x in ["STOCK", "AAPL", "MSFT", "GOOGL", "AMZN"]):
        return AssetClass.EQUITY.value
    else:
        return AssetClass.EQUITY.value


def _get_session_for_time(timestamp: datetime) -> str:
    """Get trading session for a timestamp."""
    hour = timestamp.hour

    if 4 <= hour < 9:
        return "Pre-market"
    elif 9 <= hour < 16:
        return "Regular"
    elif 16 <= hour < 20:
        return "After-hours"
    else:
        return "Overnight"


def generate_benchmark_dataset(
    variant: str = "typical",
    n_trades: int = 1000,
) -> pd.DataFrame:
    """
    Generate benchmark datasets for different scenarios.

    :param variant: Dataset variant ('typical', 'high_volume', 'high_risk', 'compliant')
    :param n_trades: Number of trades
    :return: Benchmark dataset
    """
    if variant == "typical":
        return generate_synthetic_trade_data(n_trades=n_trades)

    elif variant == "high_volume":
        # High volume trading day
        return generate_synthetic_trade_data(
            n_trades=n_trades * 3,
            n_traders=50,
            n_instruments=100,
            variability=0.5,
        )

    elif variant == "high_risk":
        # Dataset with intentional risk factors
        data = generate_synthetic_trade_data(n_trades=n_trades)

        # Add risk flags
        risk_indices = np.random.choice(len(data), size=len(data) // 10, replace=False)
        data.loc[risk_indices, "risk:limit_breach"] = True
        data.loc[risk_indices, "compliance:pre_trade_check"] = False

        return data

    elif variant == "compliant":
        # Fully SOC2-compliant dataset
        data = generate_synthetic_trade_data(n_trades=n_trades)
        # Ensure all compliance flags are True
        data["compliance:pre_trade_check"] = True
        data["compliance:post_trade_verify"] = True
        data["soc2:encryption"] = True
        return data

    else:
        return generate_synthetic_trade_data(n_trades=n_trades)


__all__ = [
    'generate_synthetic_trade_data',
    'generate_benchmark_dataset',
]
