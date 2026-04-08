'''
PM4Py – Finance Risk Detection Rules
Copyright (C) 2026 Process Intelligence Solutions GmbH

Advanced risk detection rules for trading activities.
'''

from typing import Dict, List, Any, Optional, Callable
import pandas as pd
from datetime import timedelta
from dataclasses import dataclass


@dataclass
class RiskAlert:
    """A risk alert."""
    rule_id: str
    rule_name: str
    severity: str
    risk_type: str
    case_id: Optional[str]
    description: str
    evidence: Dict[str, Any]
    recommendation: str
    timestamp: Optional[str] = None


class RiskDetectionRule:
    """Base class for risk detection rules."""

    def __init__(
        self,
        rule_id: str,
        name: str,
        risk_type: str,
        severity: str = "MEDIUM",
        description: str = "",
        threshold: Optional[float] = None,
    ):
        self.rule_id = rule_id
        self.name = name
        self.risk_type = risk_type
        self.severity = severity
        self.description = description
        self.threshold = threshold

    def check(self, log: pd.DataFrame) -> List[RiskAlert]:
        """Check the rule against the log."""
        raise NotImplementedError

    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary."""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "risk_type": self.risk_type,
            "severity": self.severity,
            "description": self.description,
            "threshold": self.threshold,
        }


class RapidTradingRule(RiskDetectionRule):
    """
    Detect rapid trading patterns (potential market manipulation or operational issues).

    Flags trades executed in unusually short timeframes.
    """

    def __init__(self, threshold_seconds: float = 1.0):
        super().__init__(
            rule_id="RISK.001",
            name="Rapid Trading Detection",
            risk_type="market_manipulation",
            severity="HIGH",
            description="Detects trades executed in unusually short timeframes",
            threshold=threshold_seconds,
        )
        self.threshold_seconds = threshold_seconds

    def check(self, log: pd.DataFrame) -> List[RiskAlert]:
        """Check for rapid trades."""
        from pm4py.util import constants

        case_id_key = constants.DEFAULT_CASE_ID_KEY
        timestamp_key = constants.DEFAULT_TIMESTAMP_KEY

        if case_id_key not in log.columns or timestamp_key not in log.columns:
            return []

        log_df = log.copy()
        log_df["timestamp"] = pd.to_datetime(log_df[timestamp_key])
        case_durations = log_df.groupby(case_id_key)["timestamp"].apply(
            lambda x: (x.max() - x.min()).total_seconds()
        )

        rapid_trades = case_durations[case_durations < self.threshold_seconds]

        alerts = []
        for trade_id, duration in rapid_trades.items():
            alerts.append(RiskAlert(
                rule_id=self.rule_id,
                rule_name=self.name,
                severity="HIGH" if duration < 0.1 else "MEDIUM",
                risk_type=self.risk_type,
                case_id=trade_id,
                description=f"Trade executed in {duration:.3f} seconds",
                evidence={"duration_seconds": duration, "threshold": self.threshold_seconds},
                recommendation="Review for potential market manipulation or system issues",
            ))

        return alerts


class OffHoursTradingRule(RiskDetectionRule):
    """
    Detect off-hours trading activity.

    Flags trades executed outside regular market hours.
    """

    def __init__(self, market_hours: tuple = (9, 16)):
        super().__init__(
            rule_id="RISK.002",
            name="Off-Hours Trading Detection",
            risk_type="operational_risk",
            severity="MEDIUM",
            description="Detects trades outside regular market hours",
        )
        self.market_hours = market_hours

    def check(self, log: pd.DataFrame) -> List[RiskAlert]:
        """Check for off-hours trading."""
        from pm4py.util import constants

        timestamp_key = constants.DEFAULT_TIMESTAMP_KEY

        if timestamp_key not in log.columns:
            return []

        log_df = log.copy()
        log_df["timestamp"] = pd.to_datetime(log_df[timestamp_key])
        log_df["hour"] = log_df["timestamp"].dt.hour

        off_hours = log_df[(log_df["hour"] < self.market_hours[0]) | (log_df["hour"] >= self.market_hours[1])]

        if len(off_hours) == 0:
            return []

        return [RiskAlert(
            rule_id=self.rule_id,
            rule_name=self.name,
            severity="MEDIUM",
            risk_type=self.risk_type,
            case_id=None,
            description=f"{len(off_hours)} events outside market hours ({self.market_hours[0]}:00-{self.market_hours[1]}:00)",
            evidence={"count": len(off_hours), "market_hours": self.market_hours},
            recommendation="Verify legitimate trading activity vs. unauthorized access",
        )]


class LargeOrderRule(RiskDetectionRule):
    """
    Detect unusually large orders.

    Flags orders exceeding a threshold percentile of average volume.
    """

    def __init__(self, percentile: float = 95.0):
        super().__init__(
            rule_id="RISK.003",
            name="Large Order Detection",
            risk_type="concentration_risk",
            severity="HIGH",
            description="Detects unusually large orders",
            threshold=percentile,
        )
        self.percentile = percentile

    def check(self, log: pd.DataFrame) -> List[RiskAlert]:
        """Check for large orders."""
        quantity_key = "trade:quantity"
        case_id_key = "case:concept:name"

        if quantity_key not in log.columns:
            return []

        threshold = log[quantity_key].quantile(self.percentile / 100)
        large_orders = log[log[quantity_key] > threshold]

        if len(large_orders) == 0:
            return []

        alerts = []
        for _, row in large_orders.head(10).iterrows():
            alerts.append(RiskAlert(
                rule_id=self.rule_id,
                rule_name=self.name,
                severity="HIGH",
                risk_type=self.risk_type,
                case_id=row.get(case_id_key, "unknown"),
                description=f"Order quantity {row[quantity_key]:.0f} exceeds {self.percentile}th percentile ({threshold:.0f})",
                evidence={"quantity": row[quantity_key], "threshold": threshold},
                recommendation="Review for proper authorization and risk approval",
            ))

        return alerts


class ConcentrationRiskRule(RiskDetectionRule):
    """
    Detect concentration risk by instrument or sector.

    Flags excessive exposure to single instruments.
    """

    def __init__(self, threshold: float = 0.15):
        super().__init__(
            rule_id="RISK.004",
            name="Concentration Risk Detection",
            risk_type="concentration_risk",
            severity="HIGH",
            description="Detects excessive concentration in single instruments",
            threshold=threshold,
        )
        self.threshold = threshold

    def check(self, log: pd.DataFrame) -> List[RiskAlert]:
        """Check for concentration risk."""
        instrument_key = "trade:instrument"
        notional_key = "trade:notional"

        if instrument_key not in log.columns:
            return []

        alerts = []

        # Calculate exposure by instrument
        if notional_key in log.columns:
            instrument_notional = log.groupby(instrument_key)[notional_key].sum()
            total_notional = instrument_notional.sum()

            for instrument, notional in instrument_notional.items():
                concentration = notional / total_notional if total_notional > 0 else 0

                if concentration > self.threshold:
                    alerts.append(RiskAlert(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity="HIGH",
                        risk_type=self.risk_type,
                        case_id=None,
                        description=f"{instrument}: {concentration*100:.1f}% of portfolio exposure",
                        evidence={
                            "instrument": instrument,
                            "concentration_ratio": concentration,
                            "notional_value": notional,
                        },
                        recommendation="Consider reducing position to meet concentration limits",
                    ))

        return alerts


class WashSaleRule(RiskDetectionRule):
    """
    Detect potential wash sales (buying and selling same instrument quickly).

    Flags trades that sell and repurchase the same instrument within 30 days.
    """

    def __init__(self, days: int = 30):
        super().__init__(
            rule_id="RISK.005",
            name="Wash Sale Detection",
            risk_type="tax_risk",
            severity="MEDIUM",
            description="Detects potential wash sales for tax purposes",
            threshold=days,
        )
        self.days = days

    def check(self, log: pd.DataFrame) -> List[RiskAlert]:
        """Check for potential wash sales."""
        from pm4py.util import constants

        case_id_key = constants.DEFAULT_CASE_ID_KEY
        timestamp_key = constants.DEFAULT_TIMESTAMP_KEY
        instrument_key = "trade:instrument"
        side_key = "trade:side"

        required_cols = [case_id_key, timestamp_key, instrument_key, side_key]
        if not all(col in log.columns for col in required_cols):
            return []

        log_df = log.copy()
        log_df["timestamp"] = pd.to_datetime(log_df[timestamp_key])

        # Find sell events
        sells = log_df[log_df[side_key] == "SELL"].copy()

        alerts = []
        for _, sell in sells.iterrows():
            instrument = sell[instrument_key]
            sell_time = sell[timestamp_key]

            # Look for buy events of same instrument within window
            future_buys = log_df[
                (log_df[instrument_key] == instrument) &
                (log_df[side_key] == "BUY") &
                (log_df["timestamp"] > sell_time) &
                (log_df["timestamp"] <= sell_time + timedelta(days=self.days))
            ]

            if len(future_buys) > 0:
                alerts.append(RiskAlert(
                    rule_id=self.rule_id,
                    rule_name=self.name,
                    severity="MEDIUM",
                    risk_type=self.risk_type,
                    case_id=sell[case_id_key],
                    description=f"Potential wash sale: {instrument} sold and repurchased within {self.days} days",
                    evidence={
                        "instrument": instrument,
                        "sell_time": sell_time.isoformat(),
                        "repurchase_count": len(future_buys),
                    },
                    recommendation="Review for tax reporting implications",
                ))

        return alerts[:10]


class PatternDayTradingRule(RiskDetectionRule):
    """
    Detect pattern day trading (frequent buy/sell of same instruments).

    Flags accounts engaging in pattern day trading behavior.
    """

    def __init__(self, min_round_trips: int = 4):
        super().__init__(
            rule_id="RISK.006",
            name="Pattern Day Trading Detection",
            risk_type="operational_risk",
            severity="MEDIUM",
            description="Detects pattern day trading behavior",
            threshold=min_round_trips,
        )
        self.min_round_trips = min_round_trips

    def check(self, log: pd.DataFrame) -> List[RiskAlert]:
        """Check for pattern day trading."""
        trader_key = "org:trader"
        instrument_key = "trade:instrument"
        side_key = "trade:side"
        case_id_key = "case:concept:name"

        required_cols = [trader_key, instrument_key, side_key, case_id_key]
        if not all(col in log.columns for col in required_cols):
            return []

        alerts = []

        # Check each trader-instrument pair for round trips
        for trader in log[trader_key].unique():
            trader_data = log[log[trader_key] == trader]

            for instrument in trader_data[instrument_key].unique():
                inst_data = trader_data[trader_data[instrument_key] == instrument]

                # Count round trips (buy followed by sell)
                buys = inst_data[inst_data[side_key] == "BUY"][case_id_key].unique()
                sells = inst_data[inst_data[side_key] == "SELL"][case_id_key].unique()

                round_trips = len(set(buys) & set(sells))

                if round_trips >= self.min_round_trips:
                    alerts.append(RiskAlert(
                        rule_id=self.rule_id,
                        rule_name=self.name,
                        severity="MEDIUM",
                        risk_type=self.risk_type,
                        case_id=trader,
                        description=f"{round_trips} round trips in {instrument}",
                        evidence={
                            "trader": trader,
                            "instrument": instrument,
                            "round_trips": round_trips,
                        },
                        recommendation="Review for Pattern Day Trader classification and margin requirements",
                    ))

        return alerts


# Registry of all risk detection rules
RISK_DETECTION_RULES = [
    RapidTradingRule(),
    OffHoursTradingRule(),
    LargeOrderRule(),
    ConcentrationRiskRule(),
    WashSaleRule(),
    PatternDayTradingRule(),
]


def check_all_risk_rules(log: pd.DataFrame) -> List[RiskAlert]:
    """
    Run all risk detection rules against the log.

    :param log: Trade workflow event log
    :return: List of all alerts from all rules
    """
    all_alerts = []

    for rule in RISK_DETECTION_RULES:
        try:
            alerts = rule.check(log)
            all_alerts.extend(alerts)
        except Exception as e:
            all_alerts.append(RiskAlert(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                severity="ERROR",
                risk_type="system_error",
                case_id=None,
                description=f"Error checking rule: {str(e)}",
                evidence={"error": str(e)},
                recommendation="Review rule configuration",
            ))

    return all_alerts


def get_risk_rule_by_id(rule_id: str) -> Optional[RiskDetectionRule]:
    """Get a risk rule by ID."""
    for rule in RISK_DETECTION_RULES:
        if rule.rule_id == rule_id:
            return rule
    return None


def get_risk_rule_by_name(name: str) -> Optional[RiskDetectionRule]:
    """Get a risk rule by name."""
    for rule in RISK_DETECTION_RULES:
        if rule.name == name:
            return rule
    return None


__all__ = [
    'RiskAlert',
    'RiskDetectionRule',
    'RapidTradingRule',
    'OffHoursTradingRule',
    'LargeOrderRule',
    'ConcentrationRiskRule',
    'WashSaleRule',
    'PatternDayTradingRule',
    'RISK_DETECTION_RULES',
    'check_all_risk_rules',
    'get_risk_rule_by_id',
    'get_risk_rule_by_name',
]
