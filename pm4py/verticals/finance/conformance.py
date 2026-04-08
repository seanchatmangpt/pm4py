'''
PM4Py – Finance Conformance
Copyright (C) 2026 Process Intelligence Solutions GmbH

SOC2 compliance, trade compliance, and regulatory reporting validation.
'''

from typing import Dict, List, Any, Optional, Union
import pandas as pd
from pm4py.objects.log.obj import EventLog
from pm4py.conformance import conformance_diagnostics_token_based_replay

from pm4py.verticals.finance.schemas import (
    SOC2_REQUIRED_ATTRIBUTES,
    REGULATORY_REPORTING_ATTRIBUTES,
    TRADE_WORKFLOW_SCHEMA,
    RISK_METRICS,
    validate_trade_schema,
)


class SOC2ConformanceChecker:
    """
    SOC2 compliance checker for trade workflows.

    Validates compliance with SOC2 Trust Services Criteria:
    - Security (CC6.1-CC6.8)
    - Availability (CC1.1-CC1.4)
    - Processing Integrity (CC3.1-CC3.9)
    - Confidentiality (CC2.1-CC2.3)
    - Privacy (CC5.1-CC5.4)
    """

    def __init__(self):
        self.violations = []
        self.warnings = []

    def check(
        self,
        log: Union[EventLog, pd.DataFrame],
        criteria: str = "security",
        strict_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Perform SOC2 compliance check.

        :param log: Trade workflow event log
        :param criteria: SOC2 criteria to check ('security', 'availability', 'integrity', 'all')
        :param strict_mode: Treat warnings as violations
        :return: Compliance report
        """
        self.violations = []
        self.warnings = []

        log_df = self._ensure_dataframe(log)

        # Check required SOC2 attributes
        self._check_required_attributes(log_df)

        # Check specific criteria
        if criteria in ["security", "all"]:
            self._check_security_criteria(log_df)
        if criteria in ["availability", "all"]:
            self._check_availability_criteria(log_df)
        if criteria in ["integrity", "all"]:
            self._check_integrity_criteria(log_df)
        if criteria in ["confidentiality", "all"]:
            self._check_confidentiality_criteria(log_df)

        # Calculate compliance score
        total_checks = len(SOC2_REQUIRED_ATTRIBUTES)
        passed_checks = total_checks - len(self.violations)

        if strict_mode:
            passed_checks -= len(self.warnings)

        compliance_score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0

        return {
            "criteria": criteria,
            "compliance_score": round(compliance_score, 2),
            "status": "COMPLIANT" if compliance_score >= 95 else "NON_COMPLIANT",
            "violations": self.violations,
            "warnings": self.warnings,
            "recommendations": self._generate_recommendations(),
            "summary": {
                "total_violations": len(self.violations),
                "total_warnings": len(self.warnings),
                "attributes_checked": total_checks,
                "events_analyzed": len(log_df),
            },
        }

    def _ensure_dataframe(self, log: Union[EventLog, pd.DataFrame]) -> pd.DataFrame:
        if isinstance(log, pd.DataFrame):
            return log
        from pm4py.conversion import convert_to_dataframe
        return convert_to_dataframe(log)

    def _check_required_attributes(self, log_df: pd.DataFrame):
        """Check if all required SOC2 attributes are present."""
        for attr_name, attr_def in SOC2_REQUIRED_ATTRIBUTES.items():
            if attr_def.get("required", False):
                if attr_name not in log_df.columns:
                    self.violations.append({
                        "rule": "SOC2_REQUIRED_ATTRIBUTE",
                        "attribute": attr_name,
                        "severity": "HIGH",
                        "description": f"Missing required SOC2 attribute: {attr_def['description']}",
                        "criterion": self._get_criterion_for_attribute(attr_name),
                    })
                else:
                    self._validate_attribute_values(log_df, attr_name, attr_def)

    def _validate_attribute_values(self, log_df: pd.DataFrame, attr_name: str, attr_def: Dict[str, Any]):
        """Validate that attribute values meet requirements."""
        validation_fn = attr_def.get("validation")
        if validation_fn:
            invalid_count = 0
            for value in log_df[attr_name]:
                try:
                    if not validation_fn(value):
                        invalid_count += 1
                except Exception:
                    invalid_count += 1

            if invalid_count > 0:
                self.violations.append({
                    "rule": "SOC2_ATTRIBUTE_VALIDATION",
                    "attribute": attr_name,
                    "severity": "MEDIUM",
                    "description": f"{invalid_count} events have invalid values for {attr_name}",
                    "criterion": self._get_criterion_for_attribute(attr_name),
                })

    def _check_security_criteria(self, log_df: pd.DataFrame):
        """Check Security criteria (CC6)."""
        # Check encryption
        if "soc2:encryption" in log_df.columns:
            unencrypted = (~log_df["soc2:encryption"]).sum()
            if unencrypted > 0:
                self.violations.append({
                    "rule": "SOC2_ENCRYPTION",
                    "criterion": "CC6.1",
                    "severity": "HIGH",
                    "description": f"{unencrypted} events without encryption",
                })
        else:
            self.violations.append({
                "rule": "SOC2_ENCRYPTION",
                "criterion": "CC6.1",
                "severity": "HIGH",
                "description": "Encryption attribute not found",
            })

        # Check access control
        if "soc2:access_control" in log_df.columns:
            weak_auth = log_df[~log_df["soc2:access_control"].isin(["MFA", "SAML"])].shape[0]
            if weak_auth > 0:
                self.warnings.append({
                    "rule": "SOC2_ACCESS_CONTROL",
                    "criterion": "CC6.1",
                    "severity": "MEDIUM",
                    "description": f"{weak_auth} events with weak access control",
                })

    def _check_availability_criteria(self, log_df: pd.DataFrame):
        """Check Availability criteria (CC1)."""
        # Check for gaps in timestamp sequence
        log_df["timestamp"] = pd.to_datetime(log_df["time:timestamp"])
        log_df = log_df.sort_values("timestamp")
        log_df["time_diff"] = log_df["timestamp"].diff()

        # Gap detection (more than 1 hour between events might indicate unavailability)
        gaps = log_df[log_df["time_diff"] > pd.Timedelta(hours=1)]
        if len(gaps) > 0:
            self.warnings.append({
                "rule": "SOC2_AVAILABILITY",
                "criterion": "CC1.2",
                "severity": "LOW",
                "description": f"{len(gaps)} potential availability gaps detected",
            })

    def _check_integrity_criteria(self, log_df: pd.DataFrame):
        """Check Processing Integrity criteria (CC3)."""
        # Check for duplicate events
        duplicates = log_df.duplicated(subset=["case:concept:name", "concept:name", "time:timestamp"]).sum()
        if duplicates > 0:
            self.violations.append({
                "rule": "SOC2_INTEGRITY",
                "criterion": "CC3.1",
                "severity": "MEDIUM",
                "description": f"{duplicates} duplicate events detected",
            })

        # Check for missing audit trails
        if "soc2:audit_log" in log_df.columns:
            missing_audit = log_df["soc2:audit_log"].isna().sum()
            if missing_audit > 0:
                self.violations.append({
                    "rule": "SOC2_INTEGRITY",
                    "criterion": "CC3.6",
                    "severity": "HIGH",
                    "description": f"{missing_audit} events missing audit log",
                })

    def _check_confidentiality_criteria(self, log_df: pd.DataFrame):
        """Check Confidentiality criteria (CC2)."""
        if "soc2:data_classification" in log_df.columns:
            public_data = log_df[log_df["soc2:data_classification"] == "public"]
            if len(public_data) > 0:
                # Check if public data has PII
                pii_cols = [col for col in log_df.columns if "client" in col.lower() or "trader" in col.lower()]
                exposed_pii = 0
                for col in pii_cols:
                    if col in public_data.columns:
                        exposed_pii += public_data[col].notna().sum()

                if exposed_pii > 0:
                    self.violations.append({
                        "rule": "SOC2_CONFIDENTIALITY",
                        "criterion": "CC2.1",
                        "severity": "HIGH",
                        "description": f"Potential PII exposure in {exposed_pii} public-classified events",
                    })

    def _get_criterion_for_attribute(self, attr_name: str) -> str:
        """Map attribute to SOC2 criterion."""
        mapping = {
            "soc2:access_control": "CC6.1",
            "soc2:encryption": "CC6.1",
            "soc2:audit_log": "CC6.6",
            "soc2:change_management": "CC6.7",
            "soc2:incident_response": "CC6.8",
            "soc2:data_classification": "CC6.1",
            "soc2:compliance_monitoring": "CC3.6",
        }
        return mapping.get(attr_name, "CC6")

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on violations."""
        recommendations = []

        for violation in self.violations:
            rule = violation.get("rule")
            if rule == "SOC2_REQUIRED_ATTRIBUTE":
                recommendations.append(
                    f"Add required attribute: {violation['attribute']} "
                    f"({violation['description']})"
                )
            elif rule == "SOC2_ENCRYPTION":
                recommendations.append("Enable encryption for all data at rest and in transit")
            elif rule == "SOC2_INTEGRITY":
                recommendations.append("Implement duplicate detection and prevention")
            elif rule == "SOC2_CONFIDENTIALITY":
                recommendations.append("Review data classification and PII handling")

        return list(set(recommendations))


class TradeComplianceChecker:
    """
    Trade compliance checker for financial regulations.

    Validates:
    - Pre-trade controls
    - Post-trade verification
    - Position limits
    - Best execution
    - Reporting requirements
    """

    def __init__(self):
        self.violations = []

    def check(
        self,
        log: Union[EventLog, pd.DataFrame],
        regulations: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Check trade compliance.

        :param log: Trade workflow event log
        :param regulations: List of regulations to check (default: all)
        :return: Trade compliance report
        """
        if regulations is None:
            regulations = ["MIFID_II", "REG_NMS", "DODD_FRANK", "MAR"]

        self.violations = []
        log_df = self._ensure_dataframe(log)

        # Check pre-trade controls
        self._check_pre_trade_controls(log_df)

        # Check post-trade verification
        self._check_post_trade_verification(log_df)

        # Check position limits
        self._check_position_limits(log_df)

        # Check best execution
        self._check_best_execution(log_df)

        # Check market abuse indicators
        self._check_market_abuse_indicators(log_df)

        compliant = len([v for v in self.violations if v.get("severity") == "HIGH"]) == 0

        return {
            "compliant": compliant,
            "violations": self.violations,
            "regulations_checked": regulations,
            "summary": {
                "total_violations": len(self.violations),
                "high_severity": len([v for v in self.violations if v.get("severity") == "HIGH"]),
                "medium_severity": len([v for v in self.violations if v.get("severity") == "MEDIUM"]),
                "trades_analyzed": log_df["case:concept:name"].nunique() if "case:concept:name" in log_df.columns else len(log_df),
            },
        }

    def _ensure_dataframe(self, log: Union[EventLog, pd.DataFrame]) -> pd.DataFrame:
        if isinstance(log, pd.DataFrame):
            return log
        from pm4py.conversion import convert_to_dataframe
        return convert_to_dataframe(log)

    def _check_pre_trade_controls(self, log_df: pd.DataFrame):
        """Check pre-trade compliance controls."""
        if "compliance:pre_trade_check" in log_df.columns:
            failed = (~log_df["compliance:pre_trade_check"]).sum()
            if failed > 0:
                self.violations.append({
                    "rule": "PRE_TRADE_CONTROLS",
                    "severity": "HIGH",
                    "description": f"{failed} events failed pre-trade compliance check",
                })

        if "risk:limit_check" in log_df.columns:
            breaches = (log_df["risk:limit_breach"] == True).sum()
            if breaches > 0:
                self.violations.append({
                    "rule": "LIMIT_BREACH",
                    "severity": "HIGH",
                    "description": f"{breaches} limit breaches detected",
                })

    def _check_post_trade_verification(self, log_df: pd.DataFrame):
        """Check post-trade verification."""
        if "compliance:post_trade_verify" in log_df.columns:
            failed = (~log_df["compliance:post_trade_verify"]).sum()
            if failed > 0:
                self.violations.append({
                    "rule": "POST_TRADE_VERIFICATION",
                    "severity": "HIGH",
                    "description": f"{failed} trades failed post-trade verification",
                })

    def _check_position_limits(self, log_df: pd.DataFrame):
        """Check position limit compliance."""
        if "trade:quantity" in log_df.columns:
            # Flag unusually large trades
            large_trades = log_df[log_df["trade:quantity"] > log_df["trade:quantity"].quantile(0.99)]
            if len(large_trades) > 0:
                self.violations.append({
                    "rule": "POSITION_LIMITS",
                    "severity": "MEDIUM",
                    "description": f"{len(large_trades)} unusually large trades detected (99th percentile)",
                })

    def _check_best_execution(self, log_df: pd.DataFrame):
        """Check best execution compliance."""
        if "reg:best_execution" in log_df.columns:
            not_best = (~log_df["reg:best_execution"]).sum()
            if not_best > 0:
                self.violations.append({
                    "rule": "BEST_EXECUTION",
                    "severity": "HIGH",
                    "description": f"{not_best} trades without best execution documentation",
                })

    def _check_market_abuse_indicators(self, log_df: pd.DataFrame):
        """Check for potential market abuse patterns."""
        # Check for rapid trading patterns
        if "case:concept:name" in log_df.columns:
            log_df["timestamp"] = pd.to_datetime(log_df["time:timestamp"])
            case_durations = log_df.groupby("case:concept:name")["timestamp"].apply(
                lambda x: x.max() - x.min()
            )

            # Flag trades executed in under 1 second
            rapid_trades = case_durations[case_durations < pd.Timedelta(seconds=1)]
            if len(rapid_trades) > 0:
                self.violations.append({
                    "rule": "MARKET_ABUSE",
                    "severity": "MEDIUM",
                    "description": f"{len(rapid_trades)} rapid trades detected (< 1 second)",
                })


class RegulatoryReportingValidator:
    """
    Regulatory reporting validator.

    Validates completeness and accuracy of regulatory reports.
    """

    def __init__(self):
        self.missing_fields = []

    def validate(
        self,
        log: Union[EventLog, pd.DataFrame],
        regulation: str = "MIFID_II",
    ) -> Dict[str, Any]:
        """
        Validate regulatory reporting data.

        :param log: Trade workflow event log
        :param regulation: Regulation to validate against
        :return: Validation report
        """
        self.missing_fields = []
        log_df = self._ensure_dataframe(log)

        # Check required regulatory attributes
        self._check_regulatory_attributes(log_df, regulation)

        # Check timestamp precision
        self._check_timestamp_precision(log_df)

        # Check data completeness
        self._check_data_completeness(log_df)

        complete = len(self.missing_fields) == 0

        return {
            "complete": complete,
            "regulation": regulation,
            "missing_fields": self.missing_fields,
            "reporting_ready": complete and self._check_reporting_readiness(log_df, regulation),
            "summary": {
                "total_missing": len(self.missing_fields),
                "events_analyzed": len(log_df),
            },
        }

    def _ensure_dataframe(self, log: Union[EventLog, pd.DataFrame]) -> pd.DataFrame:
        if isinstance(log, pd.DataFrame):
            return log
        from pm4py.conversion import convert_to_dataframe
        return convert_to_dataframe(log)

    def _check_regulatory_attributes(self, log_df: pd.DataFrame, regulation: str):
        """Check for required regulatory attributes."""
        required_attrs = REGULATORY_REPORTING_ATTRIBUTES.keys()

        for attr in required_attrs:
            attr_def = REGULATORY_REPORTING_ATTRIBUTES[attr]
            if attr_def.get("required", False) and attr not in log_df.columns:
                self.missing_fields.append({
                    "attribute": attr,
                    "description": attr_def["description"],
                    "regulation": regulation,
                })

    def _check_timestamp_precision(self, log_df: pd.DataFrame):
        """Check that timestamps have microsecond precision (required by many regulations)."""
        log_df["timestamp"] = pd.to_datetime(log_df["time:timestamp"])

        # Check for microseconds
        has_microseconds = log_df["timestamp"].apply(
            lambda x: x.microsecond > 0 or x.nanosecond > 0
        ).any()

        if not has_microseconds:
            self.missing_fields.append({
                "attribute": "time:timestamp",
                "description": "Timestamps lack microsecond precision required by Reg NMS",
                "regulation": "REG_NMS",
            })

    def _check_data_completeness(self, log_df: pd.DataFrame):
        """Check for missing data in required fields."""
        required = [
            "trade:instrument",
            "trade:quantity",
            "trade:price",
            "trade:side",
        ]

        for field in required:
            if field in log_df.columns:
                missing = log_df[field].isna().sum()
                if missing > 0:
                    self.missing_fields.append({
                        "attribute": field,
                        "description": f"{missing} events missing {field}",
                        "severity": "MEDIUM",
                    })

    def _check_reporting_readiness(self, log_df: pd.DataFrame, regulation: str) -> bool:
        """Check if data is ready for regulatory reporting."""
        # Check that all required fields are present and complete
        critical_fields = [
            "reg:transaction_id",
            "reg:execution_timestamp",
            "reg:revenue",
            "reg:best_execution",
        ]

        for field in critical_fields:
            if field not in log_df.columns:
                return False
            if log_df[field].isna().any():
                return False

        return True


__all__ = [
    'SOC2ConformanceChecker',
    'TradeComplianceChecker',
    'RegulatoryReportingValidator',
]
