'''
PM4Py – Finance Dashboards
Copyright (C) 2026 Process Intelligence Solutions GmbH

Trade flow visualization, risk analysis, and compliance monitoring.
'''

from typing import Dict, List, Any, Optional, Union
import pandas as pd
import numpy as np
from pm4py.objects.log.obj import EventLog
from pm4py.stats import get_variants, get_case_arrival_average, get_all_case_durations

from pm4py.verticals.finance.schemas import RISK_METRICS, AssetClass


class TradeFlowDashboard:
    """
    Trade flow dashboard generator.

    Creates comprehensive dashboards showing:
    - Trade volume trends
    - Execution quality metrics
    - Trader performance
    - Instrument activity
    - Venue analysis
    """

    def __init__(self, log: Union[EventLog, pd.DataFrame]):
        """
        Initialize dashboard with trade workflow data.

        :param log: Event log or DataFrame
        """
        self.log = log if isinstance(log, pd.DataFrame) else self._to_dataframe(log)

    def _to_dataframe(self, log: EventLog) -> pd.DataFrame:
        from pm4py.conversion import convert_to_dataframe
        return convert_to_dataframe(log)

    def generate(self) -> Dict[str, Any]:
        """
        Generate comprehensive dashboard data.

        :return: Dashboard data dictionary
        """
        return {
            "overview": self._get_overview(),
            "trade_volumes": self._get_trade_volumes(),
            "execution_quality": self._get_execution_quality(),
            "trader_performance": self._get_trader_performance(),
            "instrument_activity": self._get_instrument_activity(),
            "venue_analysis": self._get_venue_analysis(),
        }

    def _get_overview(self) -> Dict[str, Any]:
        """Get overview statistics."""
        from pm4py.util import constants

        case_id_key = constants.DEFAULT_CASE_ID_KEY
        timestamp_key = constants.DEFAULT_TIMESTAMP_KEY

        total_trades = self.log[case_id_key].nunique()
        total_events = len(self.log)

        # Get date range
        min_date = self.log[timestamp_key].min()
        max_date = self.log[timestamp_key].max()
        date_range_days = (max_date - min_date).days + 1

        # Calculate notional value
        notional = 0
        if "trade:notional" in self.log.columns:
            notional = self.log["trade:notional"].sum()
        elif "trade:quantity" in self.log.columns and "trade:price" in self.log.columns:
            notional = (self.log["trade:quantity"] * self.log["trade:price"]).sum()

        return {
            "total_trades": total_trades,
            "total_events": total_events,
            "date_range_days": date_range_days,
            "avg_trades_per_day": round(total_trades / date_range_days, 1) if date_range_days > 0 else 0,
            "total_notional": round(notional, 2),
        }

    def _get_trade_volumes(self) -> Dict[str, Any]:
        """Get trade volume trends."""
        from pm4py.util import constants

        timestamp_key = constants.DEFAULT_TIMESTAMP_KEY
        case_id_key = constants.DEFAULT_CASE_ID_KEY

        # Daily volumes
        self.log["date"] = pd.to_datetime(self.log[timestamp_key]).dt.date
        daily_volumes = self.log.groupby("date")[case_id_key].nunique().to_dict()

        # Hourly distribution
        self.log["hour"] = pd.to_datetime(self.log[timestamp_key]).dt.hour
        hourly_dist = self.log["hour"].value_counts().sort_index().to_dict()

        # Day of week distribution
        self.log["dow"] = pd.to_datetime(self.log[timestamp_key]).dt.dayofweek
        dow_names = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}
        dow_dist = self.log["dow"].map(dow_names).value_counts().to_dict()

        return {
            "daily_volumes": {str(k): v for k, v in daily_volumes.items()},
            "hourly_distribution": hourly_dist,
            "day_of_week_distribution": dow_dist,
        }

    def _get_execution_quality(self) -> Dict[str, Any]:
        """Get execution quality metrics."""
        metrics = {
            "avg_execution_time_seconds": 0,
            "fill_rate": 0,
            "partial_fill_rate": 0,
        }

        # Calculate execution time
        from pm4py.util import constants
        case_id_key = constants.DEFAULT_CASE_ID_KEY
        timestamp_key = constants.DEFAULT_TIMESTAMP_KEY

        case_durations = self.log.groupby(case_id_key)[timestamp_key].apply(
            lambda x: (x.max() - x.min()).total_seconds()
        )

        metrics["avg_execution_time_seconds"] = round(case_durations.mean(), 3) if len(case_durations) > 0 else 0
        metrics["median_execution_time_seconds"] = round(case_durations.median(), 3) if len(case_durations) > 0 else 0
        metrics["p95_execution_time_seconds"] = round(case_durations.quantile(0.95), 3) if len(case_durations) > 0 else 0

        # Fill rates
        if "order:status" in self.log.columns:
            total = len(self.log)
            filled = (self.log["order:status"] == "Filled").sum()
            partial = (self.log["order:status"] == "Partial Fill").sum()

            metrics["fill_rate"] = round((filled / total) * 100, 2) if total > 0 else 0
            metrics["partial_fill_rate"] = round((partial / total) * 100, 2) if total > 0 else 0

        return metrics

    def _get_trader_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get trader performance metrics."""
        from pm4py.util import constants

        trader_key = "org:trader"
        case_id_key = constants.DEFAULT_CASE_ID_KEY
        timestamp_key = constants.DEFAULT_TIMESTAMP_KEY

        if trader_key not in self.log.columns:
            return {"error": "Trader attribute not found"}

        trader_stats = {}
        for trader in self.log[trader_key].unique():
            trader_data = self.log[self.log[trader_key] == trader]

            # Calculate trade durations
            case_durations = trader_data.groupby(case_id_key)[timestamp_key].apply(
                lambda x: (x.max() - x.min()).total_seconds()
            )

            # Calculate notional
            notional = 0
            if "trade:notional" in trader_data.columns:
                notional = trader_data["trade:notional"].sum()

            trader_stats[trader] = {
                "trade_count": trader_data[case_id_key].nunique(),
                "event_count": len(trader_data),
                "avg_execution_time_seconds": round(case_durations.mean(), 3) if len(case_durations) > 0 else 0,
                "total_notional": round(notional, 2),
            }

        return trader_stats

    def _get_instrument_activity(self) -> Dict[str, Dict[str, Any]]:
        """Get instrument activity statistics."""
        from pm4py.util import constants

        instrument_key = "trade:instrument"
        case_id_key = constants.DEFAULT_CASE_ID_KEY

        if instrument_key not in self.log.columns:
            return {"error": "Instrument attribute not found"}

        instrument_stats = {}
        for instrument in self.log[instrument_key].unique():
            instrument_data = self.log[self.log[instrument_key] == instrument]

            # Calculate volume
            volume = 0
            if "trade:quantity" in instrument_data.columns:
                volume = instrument_data["trade:quantity"].sum()

            instrument_stats[instrument] = {
                "trade_count": instrument_data[case_id_key].nunique(),
                "event_count": len(instrument_data),
                "total_volume": round(volume, 2),
            }

        return instrument_stats

    def _get_venue_analysis(self) -> Dict[str, Dict[str, Any]]:
        """Get execution venue analysis."""
        from pm4py.util import constants

        venue_key = "market:venue"
        case_id_key = constants.DEFAULT_CASE_ID_KEY

        if venue_key not in self.log.columns:
            return {"error": "Venue attribute not found"}

        venue_stats = {}
        for venue in self.log[venue_key].unique():
            venue_data = self.log[self.log[venue_key] == venue]

            venue_stats[venue] = {
                "trade_count": venue_data[case_id_key].nunique(),
                "event_count": len(venue_data),
            }

        return venue_stats


class RiskAnalyzer:
    """
    Risk analysis for trading activities.

    Analyzes:
    - Value at Risk (VaR)
    - Concentration risk
    - Liquidity risk
    - Leverage ratios
    - Counterparty risk
    """

    def __init__(self, log: Union[EventLog, pd.DataFrame]):
        """
        Initialize analyzer with trade workflow data.

        :param log: Event log or DataFrame
        """
        self.log = log if isinstance(log, pd.DataFrame) else self._to_dataframe(log)

    def _to_dataframe(self, log: EventLog) -> pd.DataFrame:
        from pm4py.conversion import convert_to_dataframe
        return convert_to_dataframe(log)

    def analyze(
        self,
        risk_type: str = "all",
        threshold: float = 0.7,
        trade_id_key: str = "trade:Id",
        instrument_key: str = "trade:instrument",
    ) -> Dict[str, Any]:
        """
        Analyze trading risks.

        :param risk_type: Type of risk to analyze
        :param threshold: Risk threshold for alerting
        :param trade_id_key: Trade ID attribute
        :param instrument_key: Instrument attribute
        :return: Risk analysis results
        """
        risks = []
        alerts = []

        if risk_type in ["all", "market"]:
            market_risks = self._analyze_market_risk(instrument_key)
            risks.extend(market_risks)

        if risk_type in ["all", "concentration"]:
            concentration_risks = self._analyze_concentration_risk(instrument_key)
            risks.extend(concentration_risks)

        if risk_type in ["all", "liquidity"]:
            liquidity_risks = self._analyze_liquidity_risk(instrument_key)
            risks.extend(liquidity_risks)

        if risk_type in ["all", "operational"]:
            operational_risks = self._analyze_operational_risk()
            risks.extend(operational_risks)

        if risk_type in ["all", "compliance"]:
            compliance_risks = self._analyze_compliance_risk()
            risks.extend(compliance_risks)

        # Generate alerts for high-risk items
        for risk in risks:
            if risk.get("score", 0) >= threshold:
                alerts.append({
                    "type": risk["type"],
                    "description": risk["description"],
                    "severity": "HIGH" if risk["score"] >= 0.9 else "MEDIUM",
                    "recommendation": self._get_risk_recommendation(risk),
                })

        return {
            "total_risks": len(risks),
            "high_risk_count": len([r for r in risks if r.get("score", 0) >= 0.8]),
            "risks": risks,
            "alerts": alerts,
        }

    def _analyze_market_risk(self, instrument_key: str) -> List[Dict[str, Any]]:
        """Analyze market risk."""
        risks = []

        if "trade:notional" not in self.log.columns:
            return risks

        # Calculate portfolio volatility (using notional as proxy)
        total_notional = self.log["trade:notional"].sum()
        if total_notional == 0:
            return risks

        # Check for large single trades
        max_notional = self.log["trade:notional"].max()
        max_ratio = max_notional / total_notional

        if max_ratio > 0.1:  # Single trade > 10% of portfolio
            risks.append({
                "type": "market_risk",
                "metric": "concentration",
                "score": min(1.0, max_ratio * 10),
                "description": f"Large single trade: {max_notional} ({max_ratio*100:.1f}% of portfolio)",
            })

        return risks

    def _analyze_concentration_risk(self, instrument_key: str) -> List[Dict[str, Any]]:
        """Analyze concentration risk by instrument."""
        risks = []

        if instrument_key not in self.log.columns:
            return risks

        if "trade:notional" not in self.log.columns:
            return risks

        # Calculate concentration by instrument
        instrument_notional = self.log.groupby(instrument_key)["trade:notional"].sum()
        total_notional = instrument_notional.sum()

        for instrument, notional in instrument_notional.items():
            concentration = notional / total_notional if total_notional > 0 else 0

            if concentration > 0.1:  # > 10% concentration
                risks.append({
                    "type": "concentration_risk",
                    "instrument": instrument,
                    "concentration_ratio": round(concentration, 3),
                    "score": min(1.0, concentration * 5),
                    "description": f"{instrument}: {concentration*100:.1f}% of portfolio",
                })

        return risks

    def _analyze_liquidity_risk(self, instrument_key: str) -> List[Dict[str, Any]]:
        """Analyze liquidity risk."""
        risks = []

        if instrument_key not in self.log.columns:
            return risks

        # Check for trades in illiquid instruments (low activity)
        instrument_counts = self.log[instrument_key].value_counts()
        total_trades = instrument_counts.sum()

        for instrument, count in instrument_counts.items():
            liquidity_ratio = count / total_trades if total_trades > 0 else 0

            if liquidity_ratio < 0.01:  # Less than 1% of trades
                risks.append({
                    "type": "liquidity_risk",
                    "instrument": instrument,
                    "trade_count": count,
                    "score": 1.0 - liquidity_ratio * 100,
                    "description": f"{instrument} appears illiquid ({count} trades)",
                })

        return risks

    def _analyze_operational_risk(self) -> List[Dict[str, Any]]:
        """Analyze operational risk."""
        risks = []

        # Check for failed trades
        if "order:status" in self.log.columns:
            failed = self.log[self.log["order:status"].isin(["Rejected", "Cancelled"])]

            if len(failed) > 0:
                failure_rate = len(failed) / len(self.log)
                risks.append({
                    "type": "operational_risk",
                    "metric": "trade_failures",
                    "score": min(1.0, failure_rate * 10),
                    "description": f"{len(failed)} failed trades ({failure_rate*100:.2f}% failure rate)",
                })

        # Check for rapid trading (potential operational issues)
        from pm4py.util import constants
        case_id_key = constants.DEFAULT_CASE_ID_KEY
        timestamp_key = constants.DEFAULT_TIMESTAMP_KEY

        self.log["timestamp"] = pd.to_datetime(self.log[timestamp_key])
        case_durations = self.log.groupby(case_id_key)["timestamp"].apply(
            lambda x: (x.max() - x.min()).total_seconds()
        )

        rapid_trades = case_durations[case_durations < 1.0]  # < 1 second
        if len(rapid_trades) > 0:
            risks.append({
                "type": "operational_risk",
                "metric": "rapid_trading",
                "score": min(1.0, len(rapid_trades) / len(case_durations)),
                "description": f"{len(rapid_trades)} trades executed in < 1 second",
            })

        return risks

    def _analyze_compliance_risk(self) -> List[Dict[str, Any]]:
        """Analyze compliance risk."""
        risks = []

        # Check for missing compliance attributes
        compliance_attrs = ["compliance:pre_trade_check", "compliance:post_trade_verify"]

        for attr in compliance_attrs:
            if attr in self.log.columns:
                failed = (~self.log[attr]).sum()
                if failed > 0:
                    risks.append({
                        "type": "compliance_risk",
                        "attribute": attr,
                        "score": min(1.0, failed / len(self.log)),
                        "description": f"{failed} events failed {attr}",
                    })

        return risks

    def _get_risk_recommendation(self, risk: Dict[str, Any]) -> str:
        """Get recommendation for a risk."""
        risk_type = risk.get("type")

        recommendations = {
            "market_risk": "Consider reducing position size or implementing hedging strategies",
            "concentration_risk": "Diversify portfolio to reduce concentration risk",
            "liquidity_risk": "Use position sizing limits for illiquid instruments",
            "operational_risk": "Review trading procedures and system reliability",
            "compliance_risk": "Strengthen pre-trade controls and verification processes",
        }

        return recommendations.get(risk_type, "Monitor this risk factor closely")


class ComplianceMonitor:
    """
    Real-time compliance monitoring dashboard.

    Monitors:
    - SOC2 compliance status
    - Trade compliance status
    - Regulatory reporting status
    - Alert generation
    """

    def __init__(self, log: Union[EventLog, pd.DataFrame]):
        """
        Initialize monitor with trade workflow data.

        :param log: Event log or DataFrame
        """
        self.log = log if isinstance(log, pd.DataFrame) else self._to_dataframe(log)

    def _to_dataframe(self, log: EventLog) -> pd.DataFrame:
        from pm4py.conversion import convert_to_dataframe
        return convert_to_dataframe(log)

    def get_status(self) -> Dict[str, Any]:
        """
        Get current compliance monitoring status.

        :return: Compliance status summary
        """
        return {
            "soc2_status": self._get_soc2_status(),
            "trade_compliance_status": self._get_trade_compliance_status(),
            "regulatory_reporting_status": self._get_regulatory_status(),
            "active_alerts": self._get_active_alerts(),
            "compliance_trend": self._get_compliance_trend(),
        }

    def _get_soc2_status(self) -> Dict[str, Any]:
        """Get SOC2 compliance status."""
        required_attrs = ["soc2:encryption", "soc2:access_control", "soc2:audit_log"]

        present = sum(1 for attr in required_attrs if attr in self.log.columns)
        compliant = all(attr in self.log.columns for attr in required_attrs)

        return {
            "compliant": compliant,
            "attributes_present": present,
            "attributes_required": len(required_attrs),
            "status": "COMPLIANT" if compliant else "NON_COMPLIANT",
        }

    def _get_trade_compliance_status(self) -> Dict[str, Any]:
        """Get trade compliance status."""
        checks = ["compliance:pre_trade_check", "compliance:post_trade_verify"]

        results = {}
        for check in checks:
            if check in self.log.columns:
                passed = self.log[check].sum()
                total = len(self.log)
                results[check] = {
                    "pass_rate": round((passed / total) * 100, 2) if total > 0 else 100,
                    "passed": int(passed),
                    "total": total,
                }

        return results

    def _get_regulatory_status(self) -> Dict[str, Any]:
        """Get regulatory reporting status."""
        required = ["reg:transaction_id", "reg:execution_timestamp", "reg:revenue"]

        present = sum(1 for attr in required if attr in self.log.columns)
        complete = all(attr in self.log.columns for attr in required)

        return {
            "complete": complete,
            "attributes_present": present,
            "attributes_required": len(required),
            "status": "READY" if complete else "INCOMPLETE",
        }

    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active compliance alerts."""
        alerts = []

        # Check for encryption violations
        if "soc2:encryption" in self.log.columns:
            unencrypted = (~self.log["soc2:encryption"]).sum()
            if unencrypted > 0:
                alerts.append({
                    "type": "SOC2_ENCRYPTION",
                    "severity": "HIGH",
                    "count": int(unencrypted),
                    "description": f"{unencrypted} events without encryption",
                })

        # Check for compliance failures
        if "compliance:pre_trade_check" in self.log.columns:
            failed = (~self.log["compliance:pre_trade_check"]).sum()
            if failed > 0:
                alerts.append({
                    "type": "PRE_TRADE_COMPLIANCE",
                    "severity": "HIGH",
                    "count": int(failed),
                    "description": f"{failed} pre-trade compliance failures",
                })

        return alerts

    def _get_compliance_trend(self) -> Dict[str, Any]:
        """Get compliance trend over time."""
        from pm4py.util import constants

        timestamp_key = constants.DEFAULT_TIMESTAMP_KEY

        if timestamp_key not in self.log.columns:
            return {"error": "Timestamp not found"}

        self.log["date"] = pd.to_datetime(self.log[timestamp_key]).dt.date

        # Calculate daily compliance rate
        daily_compliance = {}
        for date, group in self.log.groupby("date"):
            if "compliance:pre_trade_check" in group.columns:
                pass_rate = (group["compliance:pre_trade_check"].sum() / len(group)) * 100
                daily_compliance[str(date)] = round(pass_rate, 2)

        return {
            "daily_compliance_rate": daily_compliance,
            "avg_compliance_rate": round(np.mean(list(daily_compliance.values())) if daily_compliance else 100, 2),
        }


__all__ = [
    'TradeFlowDashboard',
    'RiskAnalyzer',
    'ComplianceMonitor',
]
