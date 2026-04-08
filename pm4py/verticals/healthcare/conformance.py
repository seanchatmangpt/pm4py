'''
PM4Py – Healthcare Conformance Checking
Copyright (C) 2026 Process Intelligence Solutions GmbH

HIPAA compliance, consent tracking, and clinical pathway validation.
'''

from typing import Dict, List, Any, Optional, Union
import pandas as pd
from pm4py.objects.log.obj import EventLog
from pm4py.conformance import conformance_diagnostics_token_based_replay
from pm4py.discovery import discover_petri_net_inductive
from pm4py.objects.petri_net.obj import PetriNet, Marking

from pm4py.verticals.healthcare.schemas import (
    HIPAA_REQUIRED_ATTRIBUTES,
    CONSENT_TRACKING_ATTRIBUTES,
    PATIENT_JOURNEY_SCHEMA,
    STANDARD_PATHWAYS,
    validate_schema,
    identify_pathway,
)


class HIPAAConformanceChecker:
    """
    HIPAA compliance checker for patient journey data.

    Validates compliance with:
    - 45 CFR 164.312(a)(1): Access Control
    - 45 CFR 164.312(a)(2): Audit Controls
    - 45 CFR 164.312(e)(1): Transmission Security
    - 45 CFR 164.312(e)(2)(ii): Encryption
    """

    def __init__(self):
        self.violations = []
        self.warnings = []

    def check(
        self,
        log: Union[EventLog, pd.DataFrame],
        strict_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Perform comprehensive HIPAA compliance check.

        :param log: Patient journey event log
        :param strict_mode: If True, treat warnings as violations
        :return: Compliance report
        """
        self.violations = []
        self.warnings = []

        log_df = self._ensure_dataframe(log)

        # Check required HIPAA attributes
        self._check_required_attributes(log_df)

        # Check PHI handling
        self._check_phi_handling(log_df)

        # Check audit trail completeness
        self._check_audit_trail(log_df)

        # Check access control indicators
        self._check_access_control(log_df)

        # Check encryption indicators
        self._check_encryption(log_df)

        # Calculate compliance score
        total_checks = (
            len(HIPAA_REQUIRED_ATTRIBUTES) * 2
        )  # Each attribute: presence + validity
        passed_checks = total_checks - len(self.violations)

        if strict_mode:
            passed_checks -= len(self.warnings)

        compliance_score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0

        return {
            "compliance_score": round(compliance_score, 2),
            "status": "COMPLIANT" if compliance_score >= 95 else "NON_COMPLIANT",
            "violations": self.violations,
            "warnings": self.warnings,
            "recommendations": self._generate_recommendations(),
            "summary": {
                "total_violations": len(self.violations),
                "total_warnings": len(self.warnings),
                "attributes_checked": len(HIPAA_REQUIRED_ATTRIBUTES),
                "events_analyzed": len(log_df),
            },
        }

    def _ensure_dataframe(self, log: Union[EventLog, pd.DataFrame]) -> pd.DataFrame:
        if isinstance(log, pd.DataFrame):
            return log
        from pm4py.conversion import convert_to_dataframe
        return convert_to_dataframe(log)

    def _check_required_attributes(self, log_df: pd.DataFrame):
        """Check if all required HIPAA attributes are present."""
        for attr_name, attr_def in HIPAA_REQUIRED_ATTRIBUTES.items():
            if attr_def.get("required", False):
                if attr_name not in log_df.columns:
                    self.violations.append({
                        "rule": "HIPAA_REQUIRED_ATTRIBUTE",
                        "attribute": attr_name,
                        "severity": "HIGH",
                        "description": f"Missing required HIPAA attribute: {attr_def['description']}",
                        "section": "45 CFR 164.312",
                    })
                else:
                    # Validate attribute values
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
                    "rule": "HIPAA_ATTRIBUTE_VALIDATION",
                    "attribute": attr_name,
                    "severity": "MEDIUM",
                    "description": f"{invalid_count} events have invalid values for {attr_name}",
                    "section": "45 CFR 164.312",
                })

        # Check allowed values if specified
        allowed = attr_def.get("allowed_values")
        if allowed:
            invalid_values = set(log_df[attr_name].unique()) - set(allowed)
            if invalid_values:
                self.warnings.append({
                    "rule": "HIPAA_ATTRIBUTE_VALUES",
                    "attribute": attr_name,
                    "severity": "LOW",
                    "description": f"Unexpected values found: {invalid_values}",
                    "allowed_values": allowed,
                })

    def _check_phi_handling(self, log_df: pd.DataFrame):
        """Check if PHI is properly handled."""
        phi_attributes = [
            col for col in log_df.columns
            if "patient" in col.lower() or "phi" in col.lower()
        ]

        if not phi_attributes:
            self.violations.append({
                "rule": "PHI_HANDLING",
                "severity": "HIGH",
                "description": "No PHI attributes found - cannot verify proper handling",
                "section": "45 CFR 164.312(a)(1)",
            })
            return

        # Check for unencrypted PHI indicators
        if "phi:encrypted" in log_df.columns:
            unencrypted_count = (~log_df["phi:encrypted"]).sum()
            if unencrypted_count > 0:
                self.violations.append({
                    "rule": "PHI_ENCRYPTION",
                    "severity": "HIGH",
                    "description": f"{unencrypted_count} events contain unencrypted PHI",
                    "section": "45 CFR 164.312(e)(2)(ii)",
                })

    def _check_audit_trail(self, log_df: pd.DataFrame):
        """Check audit trail completeness."""
        if "phi:audit_trail" in log_df.columns:
            empty_audit = log_df["phi:audit_trail"].isna().sum()
            if empty_audit > 0:
                self.violations.append({
                    "rule": "AUDIT_TRAIL",
                    "severity": "HIGH",
                    "description": f"{empty_audit} events missing audit trail entries",
                    "section": "45 CFR 164.312(b)",
                })
        else:
            self.violations.append({
                "rule": "AUDIT_TRAIL",
                "severity": "HIGH",
                "description": "No audit trail attribute found",
                "section": "45 CFR 164.312(b)",
            })

    def _check_access_control(self, log_df: pd.DataFrame):
        """Check access control implementation."""
        if "phi:access_control" in log_df.columns:
            # Check for unknown access levels
            known_levels = ["provider", "admin", "billing", "emergency"]
            unknown = set(log_df["phi:access_control"].unique()) - set(known_levels)
            if unknown:
                self.warnings.append({
                    "rule": "ACCESS_CONTROL",
                    "severity": "MEDIUM",
                    "description": f"Unknown access levels found: {unknown}",
                    "section": "45 CFR 164.312(a)(1)",
                })
        else:
            self.violations.append({
                "rule": "ACCESS_CONTROL",
                "severity": "HIGH",
                "description": "No access control attribute found",
                "section": "45 CFR 164.312(a)(1)",
            })

    def _check_encryption(self, log_df: pd.DataFrame):
        """Check encryption indicators."""
        if "phi:encrypted" not in log_df.columns:
            self.violations.append({
                "rule": "ENCRYPTION",
                "severity": "HIGH",
                "description": "No encryption indicator found",
                "section": "45 CFR 164.312(e)(2)(ii)",
            })

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on violations."""
        recommendations = []

        for violation in self.violations:
            rule = violation.get("rule")
            if rule == "HIPAA_REQUIRED_ATTRIBUTE":
                recommendations.append(
                    f"Add required attribute: {violation['attribute']} "
                    f"({violation['description']})"
                )
            elif rule == "PHI_ENCRYPTION":
                recommendations.append(
                    "Enable encryption for all PHI at rest and in transit"
                )
            elif rule == "AUDIT_TRAIL":
                recommendations.append(
                    "Implement complete audit trail for all PHI accesses"
                )
            elif rule == "ACCESS_CONTROL":
                recommendations.append(
                    "Implement role-based access control with proper logging"
                )
            elif rule == "ENCRYPTION":
                recommendations.append(
                    "Add phi:encrypted attribute indicating encryption status"
                )

        return list(set(recommendations))  # Deduplicate


class ConsentTrackingChecker:
    """
    Consent tracking compliance checker.

    Validates consent for:
    - Treatment (HIPAA)
    - Data sharing (HIPAA + GDPR)
    - Research use (optional)
    - Consent withdrawal handling
    """

    def __init__(self):
        self.violations = []
        self.warnings = []

    def check(
        self,
        log: Union[EventLog, pd.DataFrame],
        require_all_consents: bool = True,
    ) -> Dict[str, Any]:
        """
        Check consent tracking completeness.

        :param log: Patient journey event log
        :param require_all_consents: Require all consent types to be present
        :return: Consent tracking report
        """
        self.violations = []
        self.warnings = []

        log_df = self._ensure_dataframe(log)

        # Check consent attributes
        self._check_consent_attributes(log_df, require_all_consents)

        # Check consent timestamps
        self._check_consent_timestamps(log_df)

        # Check consent withdrawal
        self._check_consent_withdrawal(log_df)

        # Calculate completeness score
        required_consents = [
            attr for attr, defn in CONSENT_TRACKING_ATTRIBUTES.items()
            if defn.get("required", False)
        ]

        present_consents = sum(
            1 for attr in required_consents
            if attr in log_df.columns
        )

        completeness_score = (present_consents / len(required_consents)) * 100 if required_consents else 100

        return {
            "completeness_score": round(completeness_score, 2),
            "status": "COMPLETE" if completeness_score >= 100 else "INCOMPLETE",
            "violations": self.violations,
            "warnings": self.warnings,
            "summary": {
                "total_violations": len(self.violations),
                "total_warnings": len(self.warnings),
                "consents_present": present_consents,
                "consents_required": len(required_consents),
                "events_analyzed": len(log_df),
            },
        }

    def _ensure_dataframe(self, log: Union[EventLog, pd.DataFrame]) -> pd.DataFrame:
        if isinstance(log, pd.DataFrame):
            return log
        from pm4py.conversion import convert_to_dataframe
        return convert_to_dataframe(log)

    def _check_consent_attributes(self, log_df: pd.DataFrame, require_all: bool):
        """Check if required consent attributes are present."""
        for attr_name, attr_def in CONSENT_TRACKING_ATTRIBUTES.items():
            required = attr_def.get("required", False) and require_all
            if required and attr_name not in log_df.columns:
                self.violations.append({
                    "rule": "CONSENT_MISSING",
                    "attribute": attr_name,
                    "severity": "HIGH",
                    "description": f"Missing required consent: {attr_def['description']}",
                })

    def _check_consent_timestamps(self, log_df: pd.DataFrame):
        """Check if consent timestamps are present and valid."""
        if "consent:timestamp" in log_df.columns:
            missing_timestamps = log_df["consent:timestamp"].isna().sum()
            if missing_timestamps > 0:
                self.warnings.append({
                    "rule": "CONSENT_TIMESTAMP",
                    "severity": "MEDIUM",
                    "description": f"{missing_timestamps} events missing consent timestamp",
                })
        else:
            self.warnings.append({
                "rule": "CONSENT_TIMESTAMP",
                "severity": "MEDIUM",
                "description": "Consent timestamp attribute not found",
            })

    def _check_consent_withdrawal(self, log_df: pd.DataFrame):
        """Check consent withdrawal handling."""
        if "consent:withdrawn" in log_df.columns:
            withdrawn_count = log_df["consent:withdrawn"].sum()
            if withdrawn_count > 0:
                if "consent:withdrawal_timestamp" not in log_df.columns:
                    self.violations.append({
                        "rule": "CONSENT_WITHDRAWAL",
                        "severity": "HIGH",
                        "description": f"{withdrawn_count} withdrawn consents missing withdrawal timestamp",
                    })


class PatientJourneyValidator:
    """
    Patient journey validator against clinical pathways.

    Checks if patient journeys follow expected clinical pathways
    and identifies deviations.
    """

    def __init__(self):
        self.deviations = []
        self.matches = []

    def validate(
        self,
        log: Union[EventLog, pd.DataFrame],
        model: Optional[tuple[PetriNet, Marking, Marking]] = None,
        activity_key: str = "concept:name",
        timestamp_key: str = "time:timestamp",
        case_id_key: str = "case:concept:name",
        min_similarity: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Validate patient journeys against model or clinical pathways.

        :param log: Patient journey event log
        :param model: Process model to validate against (optional)
        :param activity_key: Activity attribute name
        :param timestamp_key: Timestamp attribute name
        :param case_id_key: Case ID attribute name
        :param min_similarity: Minimum similarity threshold for pathway matching
        :return: Validation results
        """
        self.deviations = []
        self.matches = []

        log_df = self._ensure_dataframe(log)

        # Validate against process model if provided
        if model is not None:
            self._validate_against_model(log_df, model)

        # Match against clinical pathways
        pathway_results = self._match_pathways(log_df, min_similarity)

        # Calculate compliance statistics
        total_cases = log_df[case_id_key].nunique()
        compliant_cases = sum(1 for m in self.matches if m["similarity"] >= min_similarity)

        return {
            "compliance_rate": round((compliant_cases / total_cases) * 100, 2) if total_cases > 0 else 100,
            "total_cases": total_cases,
            "compliant_cases": compliant_cases,
            "deviations": self.deviations,
            "pathway_matches": pathway_results,
            "summary": {
                "most_common_pathway": self._get_most_common_pathway(pathway_results),
                "avg_similarity": round(
                    sum(m["similarity"] for m in self.matches) / len(self.matches) if self.matches else 0,
                    2,
                ),
            },
        }

    def _ensure_dataframe(self, log: Union[EventLog, pd.DataFrame]) -> pd.DataFrame:
        if isinstance(log, pd.DataFrame):
            return log
        from pm4py.conversion import convert_to_dataframe
        return convert_to_dataframe(log)

    def _validate_against_model(self, log_df: pd.DataFrame, model: tuple):
        """Validate against process model using conformance checking."""
        try:
            results = conformance_diagnostics_token_based_replay(
                log_df,
                model[0],
                model[1],
                model[2],
            )

            for i, result in enumerate(results):
                if not result.get("trace_is_fit", True):
                    self.deviations.append({
                        "case_id": result.get("case_id", i),
                        "type": "model_deviation",
                        "missing_tokens": result.get("missing_tokens", 0),
                        "remaining_tokens": result.get("remaining_tokens", 0),
                    })
        except Exception as e:
            self.deviations.append({
                "type": "validation_error",
                "message": str(e),
            })

    def _match_pathways(self, log_df: pd.DataFrame, min_threshold: float) -> List[Dict[str, Any]]:
        """Match cases against clinical pathways."""
        from pm4py.stats import get_variants

        # Get case activities
        case_activities = (
            log_df.groupby("case:concept:name")["concept:name"]
            .apply(list)
            .to_dict()
        )

        results = []
        for case_id, activities in case_activities.items():
            pathway_name, similarity = identify_pathway(activities)

            match_result = {
                "case_id": case_id,
                "pathway": pathway_name,
                "similarity": round(similarity, 2),
                "activities": activities,
                "is_compliant": similarity >= min_threshold,
            }

            results.append(match_result)
            self.matches.append(match_result)

            if similarity < min_threshold:
                self.deviations.append({
                    "case_id": case_id,
                    "type": "pathway_deviation",
                    "expected_pathway": pathway_name,
                    "similarity": similarity,
                })

        return results

    def _get_most_common_pathway(self, results: List[Dict[str, Any]]) -> str:
        """Get the most commonly matched pathway."""
        if not results:
            return "unknown"

        from collections import Counter
        pathway_counts = Counter(r["pathway"] for r in results)
        return pathway_counts.most_common(1)[0][0]


__all__ = [
    'HIPAAConformanceChecker',
    'ConsentTrackingChecker',
    'PatientJourneyValidator',
]
