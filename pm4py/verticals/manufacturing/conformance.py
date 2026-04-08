'''
PM4Py – Manufacturing Conformance
Copyright (C) 2026 Process Intelligence Solutions GmbH

Quality conformance, OEE validation, and production standard checking.
'''

from typing import Dict, List, Any, Optional, Union
import pandas as pd
from pm4py.objects.log.obj import EventLog

from pm4py.verticals.manufacturing.schemas import (
    OEE_ATTRIBUTES,
    OEE_CALCULATION_STANDARDS,
    MANUFACTURING_WORKFLOW_SCHEMA,
    calculate_oee,
)


class OEEConformanceChecker:
    """
    OEE (Overall Equipment Effectiveness) conformance checker.

    Validates:
    - Availability thresholds
    - Performance thresholds
    - Quality thresholds
    - World-class vs acceptable standards
    """

    def __init__(self):
        self.violations = []
        self.warnings = []

    def check(
        self,
        log: Union[EventLog, pd.DataFrame],
        oee_threshold: float = 60.0,
        strict_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Perform OEE conformance check.

        :param log: Manufacturing event log
        :param oee_threshold: Minimum acceptable OEE percentage (default: 60%)
        :param strict_mode: Treat warnings as violations
        :return: OEE conformance report
        """
        self.violations = []
        self.warnings = []

        log_df = self._ensure_dataframe(log)

        # Check OEE attributes
        self._check_oee_attributes(log_df)

        # Check OEE values against thresholds
        self._check_oee_values(log_df, oee_threshold)

        # Check world-class standards
        self._check_world_class_standards(log_df)

        # Calculate conformance score
        total_checks = len(OEE_ATTRIBUTES)
        passed_checks = total_checks - len(self.violations)

        if strict_mode:
            passed_checks -= len(self.warnings)

        conformance_score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0

        return {
            "oee_threshold": oee_threshold,
            "conformance_score": round(conformance_score, 2),
            "status": "COMPLIANT" if conformance_score >= 80 else "NON_COMPLIANT",
            "violations": self.violations,
            "warnings": self.warnings,
            "recommendations": self._generate_recommendations(),
            "summary": {
                "total_violations": len(self.violations),
                "total_warnings": len(self.warnings),
                "attributes_checked": total_checks,
                "equipment_analyzed": log_df["equipment:id"].nunique() if "equipment:id" in log_df.columns else 0,
            },
        }

    def _ensure_dataframe(self, log: Union[EventLog, pd.DataFrame]) -> pd.DataFrame:
        if isinstance(log, pd.DataFrame):
            return log
        from pm4py.conversion import convert_to_dataframe
        return convert_to_dataframe(log)

    def _check_oee_attributes(self, log_df: pd.DataFrame):
        """Check if required OEE attributes are present."""
        for attr_name, attr_def in OEE_ATTRIBUTES.items():
            if attr_def.get("required", False):
                if attr_name not in log_df.columns:
                    self.violations.append({
                        "rule": "OEE_REQUIRED_ATTRIBUTE",
                        "attribute": attr_name,
                        "severity": "HIGH",
                        "description": f"Missing required OEE attribute: {attr_def['description']}",
                    })

    def _check_oee_values(self, log_df: pd.DataFrame, threshold: float):
        """Check OEE values against threshold."""
        if "oee:oee" not in log_df.columns:
            return

        # Get unique equipment
        if "equipment:id" in log_df.columns:
            for equipment_id in log_df["equipment:id"].unique():
                equipment_data = log_df[log_df["equipment:id"] == equipment_id]
                avg_oee = equipment_data["oee:oee"].mean()

                if avg_oee < threshold:
                    self.violations.append({
                        "rule": "OEE_THRESHOLD",
                        "equipment": equipment_id,
                        "severity": "HIGH",
                        "description": f"Equipment {equipment_id}: OEE {avg_oee:.2f}% below threshold {threshold}%",
                        "actual_oee": round(avg_oee, 2),
                        "threshold": threshold,
                    })

                # Check individual OEE components
                if "oee:availability" in equipment_data.columns:
                    avg_availability = equipment_data["oee:availability"].mean()
                    availability_threshold = OEE_CALCULATION_STANDARDS["availability"]["acceptable"]
                    if avg_availability < availability_threshold:
                        self.violations.append({
                            "rule": "AVAILABILITY_LOW",
                            "equipment": equipment_id,
                            "severity": "MEDIUM",
                            "description": f"Equipment {equipment_id}: Availability {avg_availability:.2f}% below acceptable {availability_threshold}%",
                        })

                if "oee:performance" in equipment_data.columns:
                    avg_performance = equipment_data["oee:performance"].mean()
                    performance_threshold = OEE_CALCULATION_STANDARDS["performance"]["acceptable"]
                    if avg_performance < performance_threshold:
                        self.violations.append({
                            "rule": "PERFORMANCE_LOW",
                            "equipment": equipment_id,
                            "severity": "MEDIUM",
                            "description": f"Equipment {equipment_id}: Performance {avg_performance:.2f}% below acceptable {performance_threshold}%",
                        })

                if "oee:quality" in equipment_data.columns:
                    avg_quality = equipment_data["oee:quality"].mean()
                    quality_threshold = OEE_CALCULATION_STANDARDS["quality"]["acceptable"]
                    if avg_quality < quality_threshold:
                        self.violations.append({
                            "rule": "QUALITY_LOW",
                            "equipment": equipment_id,
                            "severity": "HIGH",
                            "description": f"Equipment {equipment_id}: Quality {avg_quality:.2f}% below acceptable {quality_threshold}%",
                        })

    def _check_world_class_standards(self, log_df: pd.DataFrame):
        """Check against world-class OEE standards."""
        if "oee:oee" not in log_df.columns:
            return

        world_class_oee = OEE_CALCULATION_STANDARDS["oee"]["world_class"]

        if "equipment:id" in log_df.columns:
            for equipment_id in log_df["equipment:id"].unique():
                equipment_data = log_df[log_df["equipment:id"] == equipment_id]
                avg_oee = equipment_data["oee:oee"].mean()

                if avg_oee >= world_class_oee:
                    self.warnings.append({
                        "rule": "WORLD_CLASS_OEE",
                        "equipment": equipment_id,
                        "severity": "INFO",
                        "description": f"Equipment {equipment_id}: OEE {avg_oee:.2f}% meets world-class standard ({world_class_oee}%)",
                    })

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on violations."""
        recommendations = []

        for violation in self.violations:
            rule = violation.get("rule")
            if rule == "OEE_REQUIRED_ATTRIBUTE":
                recommendations.append(
                    f"Add required OEE attribute: {violation['attribute']}"
                )
            elif rule == "OEE_THRESHOLD":
                recommendations.append(
                    f"Investigate equipment {violation['equipment']}: analyze downtime, speed losses, and quality losses"
                )
            elif rule == "AVAILABILITY_LOW":
                recommendations.append(
                    f"Reduce unplanned downtime on equipment {violation['equipment']}: implement preventive maintenance"
                )
            elif rule == "PERFORMANCE_LOW":
                recommendations.append(
                    f"Address speed losses on equipment {violation['equipment']}: check for minor stops and reduced speed"
                )
            elif rule == "QUALITY_LOW":
                recommendations.append(
                    f"Improve quality on equipment {violation['equipment']}: analyze defect patterns and implement process controls"
                )

        return list(set(recommendations))


class QualityConformanceChecker:
    """
    Quality conformance checker for manufacturing processes.

    Validates:
    - Quality check coverage
    - Defect rates
    - Rework and scrap rates
    - Inspection compliance
    """

    def __init__(self):
        self.violations = []

    def check(
        self,
        log: Union[EventLog, pd.DataFrame],
        defect_threshold: float = 5.0,
    ) -> Dict[str, Any]:
        """
        Check quality conformance.

        :param log: Manufacturing event log
        :param defect_threshold: Maximum acceptable defect rate percentage
        :return: Quality conformance report
        """
        self.violations = []
        log_df = self._ensure_dataframe(log)

        # Check quality attributes
        self._check_quality_attributes(log_df)

        # Check defect rates
        self._check_defect_rates(log_df, defect_threshold)

        # Check inspection coverage
        self._check_inspection_coverage(log_df)

        # Check rework and scrap
        self._check_rework_scrap(log_df)

        compliant = len([v for v in self.violations if v.get("severity") == "HIGH"]) == 0

        return {
            "compliant": compliant,
            "defect_threshold": defect_threshold,
            "violations": self.violations,
            "summary": {
                "total_violations": len(self.violations),
                "high_severity": len([v for v in self.violations if v.get("severity") == "HIGH"]),
                "medium_severity": len([v for v in self.violations if v.get("severity") == "MEDIUM"]),
                "orders_analyzed": log_df["case:concept:name"].nunique() if "case:concept:name" in log_df.columns else len(log_df),
            },
        }

    def _ensure_dataframe(self, log: Union[EventLog, pd.DataFrame]) -> pd.DataFrame:
        if isinstance(log, pd.DataFrame):
            return log
        from pm4py.conversion import convert_to_dataframe
        return convert_to_dataframe(log)

    def _check_quality_attributes(self, log_df: pd.DataFrame):
        """Check if quality attributes are present."""
        quality_attrs = ["quality:status", "quality:defect_code", "quality:inspector"]

        for attr in quality_attrs:
            if attr not in log_df.columns:
                self.violations.append({
                    "rule": "QUALITY_ATTRIBUTE_MISSING",
                    "attribute": attr,
                    "severity": "MEDIUM",
                    "description": f"Missing quality attribute: {attr}",
                })

    def _check_defect_rates(self, log_df: pd.DataFrame, threshold: float):
        """Check defect rates against threshold."""
        if "quality:status" not in log_df.columns:
            return

        # Calculate overall defect rate
        total = len(log_df)
        failed = (log_df["quality:status"] == "fail").sum()

        if total > 0:
            defect_rate = (failed / total) * 100

            if defect_rate > threshold:
                self.violations.append({
                    "rule": "DEFECT_RATE_HIGH",
                    "severity": "HIGH",
                    "description": f"Defect rate {defect_rate:.2f}% exceeds threshold {threshold}%",
                    "actual_rate": round(defect_rate, 2),
                    "threshold": threshold,
                })

        # Check per-equipment defect rates
        if "equipment:id" in log_df.columns:
            for equipment_id in log_df["equipment:id"].unique():
                equipment_data = log_df[log_df["equipment:id"] == equipment_id]
                equipment_total = len(equipment_data)
                equipment_failed = (equipment_data["quality:status"] == "fail").sum()

                if equipment_total > 0:
                    equipment_defect_rate = (equipment_failed / equipment_total) * 100

                    if equipment_defect_rate > threshold * 1.5:  # Allow 1.5x threshold for individual equipment
                        self.violations.append({
                            "rule": "EQUIPMENT_DEFECT_RATE",
                            "equipment": equipment_id,
                            "severity": "HIGH",
                            "description": f"Equipment {equipment_id}: Defect rate {equipment_defect_rate:.2f}% exceeds threshold",
                        })

    def _check_inspection_coverage(self, log_df: pd.DataFrame):
        """Check that all production has quality inspection."""
        production_activities = ["machining", "assembly", "welding", "production_start"]
        inspection_activities = ["inspection", "quality_check", "first_piece_inspection"]

        if "case:concept:name" not in log_df.columns or "concept:name" not in log_df.columns:
            return

        # Check cases with production but no inspection
        cases_with_production = log_df[
            log_df["concept:name"].isin(production_activities)
        ]["case:concept:name"].unique()

        cases_with_inspection = log_df[
            log_df["concept:name"].isin(inspection_activities)
        ]["case:concept:name"].unique()

        cases_without_inspection = set(cases_with_production) - set(cases_with_inspection)

        if len(cases_without_inspection) > 0:
            self.violations.append({
                "rule": "NO_INSPECTION",
                "severity": "HIGH",
                "description": f"{len(cases_without_inspection)} production cases without quality inspection",
                "cases": list(cases_without_inspection)[:10],  # First 10 cases
            })

    def _check_rework_scrap(self, log_df: pd.DataFrame):
        """Check rework and scrap rates."""
        if "concept:name" not in log_df.columns:
            return

        rework_activities = ["rework"]
        scrap_activities = ["scrap"]

        rework_count = log_df[log_df["concept:name"].isin(rework_activities)].shape[0]
        scrap_count = log_df[log_df["concept:name"].isin(scrap_activities)].shape[0]
        total_count = len(log_df)

        if total_count > 0:
            rework_rate = (rework_count / total_count) * 100
            scrap_rate = (scrap_count / total_count) * 100

            if rework_rate > 5.0:
                self.violations.append({
                    "rule": "REWORK_RATE_HIGH",
                    "severity": "MEDIUM",
                    "description": f"Rework rate {rework_rate:.2f}% exceeds 5% threshold",
                })

            if scrap_rate > 2.0:
                self.violations.append({
                    "rule": "SCRAP_RATE_HIGH",
                    "severity": "HIGH",
                    "description": f"Scrap rate {scrap_rate:.2f}% exceeds 2% threshold",
                })


class ProductionStandardsChecker:
    """
    Production standards conformance checker.

    Validates:
    - Cycle time compliance
    - Maintenance schedule adherence
    - Safety procedure compliance
    - Documentation completeness
    """

    def __init__(self):
        self.violations = []

    def check(
        self,
        log: Union[EventLog, pd.DataFrame],
        target_cycle_time: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Check production standards conformance.

        :param log: Manufacturing event log
        :param target_cycle_time: Target cycle time in seconds
        :return: Production standards report
        """
        self.violations = []
        log_df = self._ensure_dataframe(log)

        # Check cycle times
        if target_cycle_time:
            self._check_cycle_times(log_df, target_cycle_time)

        # Check maintenance compliance
        self._check_maintenance_compliance(log_df)

        # Check documentation
        self._check_documentation(log_df)

        compliant = len([v for v in self.violations if v.get("severity") == "HIGH"]) == 0

        return {
            "compliant": compliant,
            "violations": self.violations,
            "summary": {
                "total_violations": len(self.violations),
                "high_severity": len([v for v in self.violations if v.get("severity") == "HIGH"]),
                "orders_analyzed": log_df["case:concept:name"].nunique() if "case:concept:name" in log_df.columns else len(log_df),
            },
        }

    def _ensure_dataframe(self, log: Union[EventLog, pd.DataFrame]) -> pd.DataFrame:
        if isinstance(log, pd.DataFrame):
            return log
        from pm4py.conversion import convert_to_dataframe
        return convert_to_dataframe(log)

    def _check_cycle_times(self, log_df: pd.DataFrame, target: float):
        """Check cycle time compliance."""
        if "production:cycle_time" not in log_df.columns:
            return

        # Flag excessive cycle times (more than 20% over target)
        excessive = log_df[log_df["production:cycle_time"] > target * 1.2]

        if len(excessive) > 0:
            self.violations.append({
                "rule": "CYCLE_TIME_EXCESSIVE",
                "severity": "MEDIUM",
                "description": f"{len(excessive)} events with cycle time > 120% of target ({target}s)",
                "target_cycle_time": target,
            })

    def _check_maintenance_compliance(self, log_df: pd.DataFrame):
        """Check maintenance schedule adherence."""
        maintenance_activities = ["preventive_maintenance", "corrective_maintenance", "calibration"]

        if "concept:name" not in log_df.columns:
            return

        maintenance_events = log_df[log_df["concept:name"].isin(maintenance_activities)]

        if "equipment:id" in log_df.columns:
            # Check equipment without any maintenance records
            all_equipment = log_df["equipment:id"].unique()
            equipment_with_maintenance = maintenance_events["equipment:id"].unique() if len(maintenance_events) > 0 else []
            equipment_without_maintenance = set(all_equipment) - set(equipment_with_maintenance)

            if len(equipment_without_maintenance) > 0:
                self.violations.append({
                    "rule": "NO_MAINTENANCE",
                    "severity": "MEDIUM",
                    "description": f"{len(equipment_without_maintenance)} equipment without maintenance records",
                    "equipment": list(equipment_without_maintenance),
                })

    def _check_documentation(self, log_df: pd.DataFrame):
        """Check documentation completeness."""
        required_docs = ["production:order_id", "production:product_id", "equipment:id"]

        missing = []
        for doc_attr in required_docs:
            if doc_attr not in log_df.columns:
                missing.append(doc_attr)

        if missing:
            self.violations.append({
                "rule": "DOCUMENTATION_INCOMPLETE",
                "severity": "LOW",
                "description": f"Missing documentation attributes: {missing}",
            })


__all__ = [
    'OEEConformanceChecker',
    'QualityConformanceChecker',
    'ProductionStandardsChecker',
]
