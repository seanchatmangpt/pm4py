'''
PM4Py – Healthcare Vertical
Copyright (C) 2026 Process Intelligence Solutions GmbH

HIPAA-ready patient journey mining with pre-built schemas,
conformance rules, and dashboards.
'''

from typing import Dict, List, Any, Optional, Union
import pandas as pd
from pm4py.objects.log.obj import EventLog
from pm4py.discovery import discover_powl
from pm4py.conformance import conformance_diagnostics_token_based_replay
from pm4py.vis import view_powl, save_vis_powl

from pm4py.verticals.healthcare.schemas import (
    PATIENT_JOURNEY_SCHEMA,
    HIPAA_REQUIRED_ATTRIBUTES,
    CONSENT_TRACKING_ATTRIBUTES,
)
from pm4py.verticals.healthcare.conformance import (
    HIPAAConformanceChecker,
    ConsentTrackingChecker,
    PatientJourneyValidator,
)
from pm4py.verticals.healthcare.dashboards import (
    PatientFlowDashboard,
    WaitTimeAnalyzer,
    BottleneckDetector,
)
from pm4py.verticals.healthcare.demos import generate_synthetic_patient_data


class HealthcareVertical:
    """
    HIPAA-ready healthcare process mining vertical.

    Features:
    - Patient journey discovery and analysis
    - HIPAA compliance checking
    - Consent tracking validation
    - Patient flow visualization
    - Wait time analysis
    - Bottleneck detection

    Example:
        >>> import pm4py
        >>> from pm4py.verticals import HealthcareVertical
        >>>
        >>> # Generate demo data
        >>> log = HealthcareVertical.generate_demo_data(n_patients=100)
        >>>
        >>> # Discover patient journey model
        >>> vertical = HealthcareVertical(log)
        >>> model = vertical.discover_journey()
        >>>
        >>> # Check HIPAA compliance
        >>> compliance = vertical.check_hipaa_compliance()
        >>>
        >>> # Analyze wait times
        >>> wait_analysis = vertical.analyze_wait_times()
        >>>
        >>> # Visualize patient flow
        >>> vertical.visualize_patient_flow()
    """

    def __init__(
        self,
        log: Union[EventLog, pd.DataFrame],
        activity_key: str = "concept:name",
        timestamp_key: str = "time:timestamp",
        case_id_key: str = "case:concept:name",
        patient_id_key: str = "patient:Id",
        department_key: str = "org:department",
    ):
        """
        Initialize healthcare vertical with patient journey data.

        :param log: Event log or DataFrame containing patient journey events
        :param activity_key: Attribute for activity names
        :param timestamp_key: Attribute for timestamps
        :param case_id_key: Attribute for case IDs (encounter IDs)
        :param patient_id_key: Attribute for patient IDs
        :param department_key: Attribute for departments/units
        """
        self.log = log
        self.activity_key = activity_key
        self.timestamp_key = timestamp_key
        self.case_id_key = case_id_key
        self.patient_id_key = patient_id_key
        self.department_key = department_key

        # Initialize components
        self.hipaa_checker = HIPAAConformanceChecker()
        self.consent_checker = ConsentTrackingChecker()
        self.journey_validator = PatientJourneyValidator()
        self.dashboard = PatientFlowDashboard(log)
        self.wait_analyzer = WaitTimeAnalyzer(log)
        self.bottleneck_detector = BottleneckDetector(log)

    def discover_journey(
        self,
        variant: str = "inductive",
        optimize_for: str = "clinical_pathways"
    ):
        """
        Discover patient journey process model.

        :param variant: Discovery algorithm ('inductive', 'heuristic', 'powl')
        :param optimize_for: Optimization target ('clinical_pathways', 'wait_times', 'bottlenecks')
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

    def check_hipaa_compliance(self) -> Dict[str, Any]:
        """
        Check HIPAA compliance of the patient journey data.

        Verifies:
        - Required attributes present
        - PHI (Protected Health Information) properly handled
        - Audit trail completeness
        - Access control indicators

        :return: Compliance report with violations and recommendations
        """
        return self.hipaa_checker.check(self.log)

    def check_consent_tracking(self) -> Dict[str, Any]:
        """
        Check consent tracking completeness.

        Verifies:
        - Treatment consent recorded
        - Data sharing consent recorded
        - Consent timestamp present
        - Consent status valid

        :return: Consent tracking report
        """
        return self.consent_checker.check(self.log)

    def validate_journey(self, model=None) -> Dict[str, Any]:
        """
        Validate patient journeys against clinical pathways.

        :param model: Process model to validate against (optional)
        :return: Validation results with deviations
        """
        if model is None:
            model = self.discover_journey()

        return self.journey_validator.validate(
            self.log,
            model,
            activity_key=self.activity_key,
            timestamp_key=self.timestamp_key,
            case_id_key=self.case_id_key,
        )

    def analyze_wait_times(
        self,
        department: Optional[str] = None,
        activity: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze wait times across patient journey.

        :param department: Filter by department (optional)
        :param activity: Filter by activity (optional)
        :return: Wait time statistics and insights
        """
        return self.wait_analyzer.analyze(
            department=department,
            activity=activity,
            timestamp_key=self.timestamp_key,
            department_key=self.department_key,
        )

    def detect_bottlenecks(self, threshold_percentile: float = 75.0) -> List[Dict[str, Any]]:
        """
        Detect bottlenecks in patient flow.

        :param threshold_percentile: Percentile threshold for bottleneck detection
        :return: List of detected bottlenecks with recommendations
        """
        return self.bottleneck_detector.detect(
            threshold_percentile=threshold_percentile,
            activity_key=self.activity_key,
            timestamp_key=self.timestamp_key,
            department_key=self.department_key,
        )

    def visualize_patient_flow(
        self,
        format: str = "png",
        output_path: Optional[str] = None
    ):
        """
        Visualize patient flow process model.

        :param format: Output format ('png', 'svg', 'pdf')
        :param output_path: Output file path (optional)
        """
        model = self.discover_journey(variant="powl")
        if output_path:
            save_vis_powl(model, file_path=output_path)
        else:
            view_powl(model, format=format)

    def generate_dashboard(self) -> Dict[str, Any]:
        """
        Generate comprehensive patient flow dashboard.

        Includes:
        - Patient volume trends
        - Department utilization
        - Wait time distributions
        - Bottleneck alerts
        - Compliance status

        :return: Dashboard data for visualization
        """
        return self.dashboard.generate()

    def get_clinical_pathways(self) -> List[Dict[str, Any]]:
        """
        Extract common clinical pathways from patient journeys.

        :return: List of discovered clinical pathways with frequencies
        """
        from pm4py.stats import get_variants

        variants = get_variants(
            self.log,
            activity_key=self.activity_key,
            case_id_key=self.case_id_key,
        )

        # Sort by frequency
        sorted_variants = sorted(
            variants.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {
                "pathway": variant,
                "frequency": count,
                "percentage": (count / sum(variants.values())) * 100,
            }
            for variant, count in sorted_variants
        ]

    def get_department_statistics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics per department/unit.

        :return: Department-wise statistics
        """
        stats = {}
        grouped = self.log.groupby(self.department_key) if isinstance(self.log, pd.DataFrame) else None

        if grouped:
            for dept, group in grouped:
                stats[dept] = {
                    "case_count": len(group[self.case_id_key].unique()),
                    "event_count": len(group),
                    "activities": group[self.activity_key].nunique(),
                    "avg_duration": (
                        group.groupby(self.case_id_key)[self.timestamp_key].max()
                        - group.groupby(self.case_id_key)[self.timestamp_key].min()
                    ).mean(),
                }

        return stats

    @staticmethod
    def generate_demo_data(
        n_patients: int = 100,
        n_departments: int = 5,
        seed: int = 42,
        return_dataframe: bool = True,
    ) -> Union[pd.DataFrame, EventLog]:
        """
        Generate synthetic patient journey data for testing.

        :param n_patients: Number of patients to generate
        :param n_departments: Number of departments to simulate
        :param seed: Random seed for reproducibility
        :param return_dataframe: Return DataFrame instead of EventLog
        :return: Synthetic patient journey log
        """
        return generate_synthetic_patient_data(
            n_patients=n_patients,
            n_departments=n_departments,
            seed=seed,
            return_dataframe=return_dataframe,
        )

    def export_for_compliance_audit(self, output_path: str):
        """
        Export data for HIPAA compliance audit.

        Creates a sanitized export with:
        - Hashed patient IDs
        - All required PHI attributes
        - Complete audit trail
        - Consent documentation

        :param output_path: Output file path
        """
        import hashlib
        import json

        log_df = self.log if isinstance(self.log, pd.DataFrame) else None

        if log_df is None:
            from pm4py.conversion import convert_to_dataframe
            log_df = convert_to_dataframe(self.log)

        # Sanitize PHI
        audit_data = []
        for _, row in log_df.iterrows():
            audit_row = {
                "case_id": row[self.case_id_key],
                "patient_id_hash": hashlib.sha256(
                    str(row.get(self.patient_id_key, "")).encode()
                ).hexdigest()[:16],
                "activity": row[self.activity_key],
                "timestamp": row[self.timestamp_key].isoformat(),
                "department": row.get(self.department_key, "Unknown"),
                "consent_status": row.get("consent:status", "Unknown"),
                "consent_timestamp": row.get("consent:timestamp", ""),
            }
            audit_data.append(audit_row)

        with open(output_path, 'w') as f:
            json.dump({
                "export_timestamp": pd.Timestamp.now().isoformat(),
                "total_events": len(audit_data),
                "hipaa_required_attributes": list(HIPAA_REQUIRED_ATTRIBUTES.keys()),
                "events": audit_data,
            }, f, indent=2)


# Convenience functions
def quick_analyze(log: Union[EventLog, pd.DataFrame]) -> Dict[str, Any]:
    """
    Quick analysis of patient journey data.

    Returns comprehensive analysis including:
    - Process model
    - HIPAA compliance
    - Wait times
    - Bottlenecks
    - Clinical pathways

    :param log: Patient journey event log
    :return: Comprehensive analysis results
    """
    vertical = HealthcareVertical(log)

    return {
        "model": vertical.discover_journey(),
        "hipaa_compliance": vertical.check_hipaa_compliance(),
        "consent_tracking": vertical.check_consent_tracking(),
        "wait_times": vertical.analyze_wait_times(),
        "bottlenecks": vertical.detect_bottlenecks(),
        "clinical_pathways": vertical.get_clinical_pathways(),
        "department_stats": vertical.get_department_statistics(),
    }


__all__ = [
    'HealthcareVertical',
    'quick_analyze',
    'PATIENT_JOURNEY_SCHEMA',
    'HIPAA_REQUIRED_ATTRIBUTES',
]
