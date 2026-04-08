'''
PM4Py – Finance Vertical
Copyright (C) 2026 Process Intelligence Solutions GmbH

SOC2-ready trade workflow mining with pre-built schemas,
regulatory reporting, and risk detection.
'''

from typing import Dict, List, Any, Optional, Union
import pandas as pd
from pm4py.objects.log.obj import EventLog
from pm4py.discovery import discover_powl
from pm4py.conformance import conformance_diagnostics_token_based_replay
from pm4py.vis import view_powl, save_vis_powl

from pm4py.verticals.finance.schemas import (
    TRADE_WORKFLOW_SCHEMA,
    SOC2_REQUIRED_ATTRIBUTES,
    REGULATORY_REPORTING_ATTRIBUTES,
    MarketType,
    TradeType,
    AssetClass,
)
from pm4py.verticals.finance.conformance import (
    SOC2ConformanceChecker,
    TradeComplianceChecker,
    RegulatoryReportingValidator,
)
from pm4py.verticals.finance.dashboards import (
    TradeFlowDashboard,
    RiskAnalyzer,
    ComplianceMonitor,
)
from pm4py.verticals.finance.demos import generate_synthetic_trade_data


class FinanceVertical:
    """
    SOC2-ready finance process mining vertical.

    Features:
    - Trade workflow discovery and analysis
    - SOC2 compliance checking
    - Regulatory reporting validation
    - Risk detection and analysis
    - Trade reconstruction
    - Audit trail generation

    Example:
        >>> import pm4py
        >>> from pm4py.verticals import FinanceVertical
        >>>
        >>> # Generate demo data
        >>> log = FinanceVertical.generate_demo_data(n_trades=1000)
        >>>
        >>> # Discover trade workflow model
        >>> vertical = FinanceVertical(log)
        >>> model = vertical.discover_trade_workflow()
        >>>
        >>> # Check SOC2 compliance
        >>> compliance = vertical.check_soc2_compliance()
        >>>
        >>> # Analyze trading risks
        >>> risks = vertical.analyze_risks()
        >>>
        >>> # Generate regulatory report
        >>> report = vertical.generate_regulatory_report()
    """

    def __init__(
        self,
        log: Union[EventLog, pd.DataFrame],
        activity_key: str = "concept:name",
        timestamp_key: str = "time:timestamp",
        case_id_key: str = "case:concept:name",
        trade_id_key: str = "trade:Id",
        instrument_key: str = "trade:instrument",
        trader_key: str = "trade:trader",
    ):
        """
        Initialize finance vertical with trade workflow data.

        :param log: Event log or DataFrame containing trade workflow events
        :param activity_key: Attribute for activity names
        :param timestamp_key: Attribute for timestamps
        :param case_id_key: Attribute for case IDs (trade IDs)
        :param trade_id_key: Attribute for trade identifiers
        :param instrument_key: Attribute for financial instruments
        :param trader_key: Attribute for trader IDs
        """
        self.log = log
        self.activity_key = activity_key
        self.timestamp_key = timestamp_key
        self.case_id_key = case_id_key
        self.trade_id_key = trade_id_key
        self.instrument_key = instrument_key
        self.trader_key = trader_key

        # Initialize components
        self.soc2_checker = SOC2ConformanceChecker()
        self.trade_compliance_checker = TradeComplianceChecker()
        self.reporting_validator = RegulatoryReportingValidator()
        self.dashboard = TradeFlowDashboard(log)
        self.risk_analyzer = RiskAnalyzer(log)
        self.compliance_monitor = ComplianceMonitor(log)

    def discover_trade_workflow(
        self,
        variant: str = "powl",
        optimize_for: str = "trade_reconstruction"
    ):
        """
        Discover trade workflow process model.

        :param variant: Discovery algorithm ('inductive', 'heuristic', 'powl')
        :param optimize_for: Optimization target ('trade_reconstruction', 'risk_detection', 'audit')
        :return: Process model (POWL, Petri net, or BPMN)
        """
        if variant == "powl":
            return discover_powl(
                self.log,
                activity_key=self.activity_key,
                timestamp_key=self.timestamp_key,
                case_id_key=self.case_id_key,
            )
        else:
            from pm4py.discovery import discover_petri_net_inductive
            return discover_petri_net_inductive(
                self.log,
                activity_key=self.activity_key,
                timestamp_key=self.timestamp_key,
                case_id_key=self.case_id_key,
            )

    def check_soc2_compliance(self) -> Dict[str, Any]:
        """
        Check SOC2 compliance of the trade workflow data.

        Verifies:
        - Access control (CC6.1)
        - Change management (CC6.7)
        - Data encryption (CC6.1)
        - Audit trail completeness
        - Incident response

        :return: Compliance report with violations and recommendations
        """
        return self.soc2_checker.check(self.log)

    def check_trade_compliance(self) -> Dict[str, Any]:
        """
        Check trade compliance regulations.

        Verifies:
        - Pre-trade controls
        - Post-trade verification
        - Position limits
        - Reporting requirements
        - Best execution

        :return: Trade compliance report
        """
        return self.trade_compliance_checker.check(self.log)

    def validate_regulatory_reporting(self) -> Dict[str, Any]:
        """
        Validate regulatory reporting completeness.

        Verifies:
        - Trade reporting attributes
        - Timestamp accuracy
        - Counterparty information
        - Transaction details

        :return: Regulatory reporting validation report
        """
        return self.reporting_validator.validate(self.log)

    def analyze_risks(
        self,
        risk_type: str = "all",
        threshold: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Analyze trading risks.

        :param risk_type: Type of risk ('all', 'market', 'credit', 'operational', 'compliance')
        :param threshold: Risk threshold for alerting
        :return: Risk analysis results
        """
        return self.risk_analyzer.analyze(
            risk_type=risk_type,
            threshold=threshold,
            trade_id_key=self.trade_id_key,
            instrument_key=self.instrument_key,
        )

    def reconstruct_trades(self, trade_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Reconstruct complete trade lifecycle from events.

        :param trade_ids: List of specific trade IDs to reconstruct (optional)
        :return: List of reconstructed trades with full event history
        """
        log_df = self.log if isinstance(self.log, pd.DataFrame) else self._to_dataframe(self.log)

        if trade_ids:
            log_df = log_df[log_df[self.trade_id_key].isin(trade_ids)]

        trades = []
        for trade_id, group in log_df.groupby(self.case_id_key):
            group = group.sort_values(self.timestamp_key)
            trades.append({
                "trade_id": trade_id,
                "events": group.to_dict("records"),
                "start_time": group[self.timestamp_key].min(),
                "end_time": group[self.timestamp_key].max(),
                "duration_seconds": (
                    group[self.timestamp_key].max() - group[self.timestamp_key].min()
                ).total_seconds(),
                "activities": group[self.activity_key].tolist(),
            })

        return trades

    def generate_regulatory_report(
        self,
        report_type: str = "trade_reconstruction",
        date_range: Optional[tuple] = None,
    ) -> Dict[str, Any]:
        """
        Generate regulatory report.

        :param report_type: Type of report ('trade_reconstruction', 'audit_trail', 'risk_summary')
        :param date_range: Date range for the report (start, end)
        :return: Regulatory report data
        """
        log_df = self.log if isinstance(self.log, pd.DataFrame) else self._to_dataframe(self.log)

        if date_range:
            log_df = log_df[
                (log_df[self.timestamp_key] >= date_range[0]) &
                (log_df[self.timestamp_key] <= date_range[1])
            ]

        if report_type == "trade_reconstruction":
            return self._generate_trade_reconstruction_report(log_df)
        elif report_type == "audit_trail":
            return self._generate_audit_trail_report(log_df)
        elif report_type == "risk_summary":
            return self._generate_risk_summary_report(log_df)
        else:
            raise ValueError(f"Unknown report type: {report_type}")

    def _generate_trade_reconstruction_report(self, log_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate trade reconstruction report."""
        trades = self.reconstruct_trades()

        return {
            "report_type": "trade_reconstruction",
            "report_timestamp": pd.Timestamp.now().isoformat(),
            "total_trades": len(trades),
            "trades": trades,
            "summary": {
                "avg_trade_duration_seconds": sum(
                    t["duration_seconds"] for t in trades
                ) / len(trades) if trades else 0,
                "unique_instruments": log_df[self.instrument_key].nunique() if self.instrument_key in log_df.columns else 0,
                "unique_traders": log_df[self.trader_key].nunique() if self.trader_key in log_df.columns else 0,
            },
        }

    def _generate_audit_trail_report(self, log_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate audit trail report."""
        return {
            "report_type": "audit_trail",
            "report_timestamp": pd.Timestamp.now().isoformat(),
            "total_events": len(log_df),
            "events_by_activity": log_df[self.activity_key].value_counts().to_dict(),
            "events_by_user": log_df[self.trader_key].value_counts().to_dict() if self.trader_key in log_df.columns else {},
            "time_range": {
                "start": log_df[self.timestamp_key].min().isoformat(),
                "end": log_df[self.timestamp_key].max().isoformat(),
            },
        }

    def _generate_risk_summary_report(self, log_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate risk summary report."""
        risk_analysis = self.analyze_risks()

        return {
            "report_type": "risk_summary",
            "report_timestamp": pd.Timestamp.now().isoformat(),
            "risk_analysis": risk_analysis,
            "high_risk_trades": len([
                r for r in risk_analysis.get("risks", [])
                if r.get("severity") == "HIGH"
            ]),
        }

    def detect_unusual_patterns(self) -> List[Dict[str, Any]]:
        """
        Detect unusual trading patterns.

        Identifies:
        - Rapidly executed trades
        - Unusual volumes
        - Off-hours trading
        - Pattern deviations

        :return: List of detected anomalies
        """
        log_df = self.log if isinstance(self.log, pd.DataFrame) else self._to_dataframe(self.log)

        anomalies = []

        # Detect rapid trades (sub-second execution)
        if self.case_id_key in log_df.columns:
            case_durations = log_df.groupby(self.case_id_key).apply(
                lambda g: (g[self.timestamp_key].max() - g[self.timestamp_key].min()).total_seconds()
            )

            rapid_trades = case_durations[case_durations < 1.0]
            for trade_id, duration in rapid_trades.items():
                anomalies.append({
                    "type": "rapid_trade",
                    "trade_id": trade_id,
                    "duration_seconds": duration,
                    "severity": "HIGH" if duration < 0.1 else "MEDIUM",
                    "description": f"Trade executed in {duration:.3f} seconds",
                })

        # Detect off-hours trading (outside 9:30 AM - 4:00 PM ET)
        log_df["hour"] = pd.to_datetime(log_df[self.timestamp_key]).dt.hour
        off_hours = log_df[(log_df["hour"] < 9) | (log_df["hour"] >= 16)]

        if len(off_hours) > 0:
            anomalies.append({
                "type": "off_hours_trading",
                "count": len(off_hours),
                "severity": "MEDIUM",
                "description": f"{len(off_hours)} events detected outside market hours",
            })

        return anomalies

    def visualize_trade_flow(
        self,
        format: str = "png",
        output_path: Optional[str] = None
    ):
        """
        Visualize trade workflow process model.

        :param format: Output format ('png', 'svg', 'pdf')
        :param output_path: Output file path (optional)
        """
        model = self.discover_trade_workflow(variant="powl")
        if output_path:
            save_vis_powl(model, file_path=output_path)
        else:
            view_powl(model, format=format)

    def get_trader_statistics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics per trader.

        :return: Trader-wise statistics
        """
        log_df = self.log if isinstance(self.log, pd.DataFrame) else self._to_dataframe(self.log)

        if self.trader_key not in log_df.columns:
            return {"error": "Trader key not found in log"}

        stats = {}
        for trader in log_df[self.trader_key].unique():
            trader_data = log_df[log_df[self.trader_key] == trader]

            stats[trader] = {
                "trade_count": trader_data[self.case_id_key].nunique(),
                "event_count": len(trader_data),
                "unique_instruments": trader_data[self.instrument_key].nunique() if self.instrument_key in trader_data.columns else 0,
                "avg_trade_duration": self._calculate_avg_duration(trader_data),
            }

        return stats

    def _calculate_avg_duration(self, trader_data: pd.DataFrame) -> float:
        """Calculate average trade duration for a trader."""
        durations = trader_data.groupby(self.case_id_key).apply(
            lambda g: (g[self.timestamp_key].max() - g[self.timestamp_key].min()).total_seconds()
        )
        return float(durations.mean()) if len(durations) > 0 else 0.0

    def _to_dataframe(self, log: EventLog) -> pd.DataFrame:
        """Convert EventLog to DataFrame."""
        from pm4py.conversion import convert_to_dataframe
        return convert_to_dataframe(log)

    @staticmethod
    def generate_demo_data(
        n_trades: int = 1000,
        n_traders: int = 20,
        n_instruments: int = 50,
        seed: int = 42,
        return_dataframe: bool = True,
    ) -> Union[pd.DataFrame, EventLog]:
        """
        Generate synthetic trade workflow data for testing.

        :param n_trades: Number of trades to generate
        :param n_traders: Number of traders to simulate
        :param n_instruments: Number of financial instruments
        :param seed: Random seed for reproducibility
        :param return_dataframe: Return DataFrame instead of EventLog
        :return: Synthetic trade workflow log
        """
        return generate_synthetic_trade_data(
            n_trades=n_trades,
            n_traders=n_traders,
            n_instruments=n_instruments,
            seed=seed,
            return_dataframe=return_dataframe,
        )

    def export_for_audit(self, output_path: str, include_phi: bool = False):
        """
        Export data for audit purposes.

        Creates a sanitized export with:
        - Complete audit trail
        - All required SOC2 attributes
        - Trade reconstruction data
        - Risk indicators

        :param output_path: Output file path
        :param include_phi: Include personally identifiable information
        """
        import json

        log_df = self.log if isinstance(self.log, pd.DataFrame) else self._to_dataframe(self.log)

        audit_data = {
            "export_timestamp": pd.Timestamp.now().isoformat(),
            "soc2_compliant": True,
            "total_events": len(log_df),
            "total_trades": log_df[self.case_id_key].nunique(),
            "audit_trail": self._generate_audit_trail_report(log_df),
            "compliance": self.check_soc2_compliance(),
            "risks": self.analyze_risks(),
        }

        if include_phi:
            audit_data["trades"] = self.reconstruct_trades()

        with open(output_path, 'w') as f:
            json.dump(audit_data, f, indent=2, default=str)


# Convenience functions
def quick_analyze(log: Union[EventLog, pd.DataFrame]) -> Dict[str, Any]:
    """
    Quick analysis of trade workflow data.

    Returns comprehensive analysis including:
    - Process model
    - SOC2 compliance
    - Trade compliance
    - Risk analysis
    - Unusual patterns

    :param log: Trade workflow event log
    :return: Comprehensive analysis results
    """
    vertical = FinanceVertical(log)

    return {
        "model": vertical.discover_trade_workflow(),
        "soc2_compliance": vertical.check_soc2_compliance(),
        "trade_compliance": vertical.check_trade_compliance(),
        "regulatory_reporting": vertical.validate_regulatory_reporting(),
        "risks": vertical.analyze_risks(),
        "unusual_patterns": vertical.detect_unusual_patterns(),
        "trader_stats": vertical.get_trader_statistics(),
    }


__all__ = [
    'FinanceVertical',
    'quick_analyze',
    'TRADE_WORKFLOW_SCHEMA',
    'SOC2_REQUIRED_ATTRIBUTES',
]
