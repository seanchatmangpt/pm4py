'''
PM4Py – Healthcare Dashboards
Copyright (C) 2026 Process Intelligence Solutions GmbH

Patient flow visualization, wait time analysis, and bottleneck detection.
'''

from typing import Dict, List, Any, Optional, Union
import pandas as pd
import numpy as np
from pm4py.objects.log.obj import EventLog

from pm4py.verticals.healthcare.schemas import (
    HIPAA_REQUIRED_ATTRIBUTES,
    PATIENT_JOURNEY_SCHEMA,
    STANDARD_PATHWAYS,
)


class PatientFlowDashboard:
    """
    Patient flow dashboard generator.

    Creates comprehensive dashboards showing:
    - Patient volume trends
    - Department utilization
    - Peak hours analysis
    - Length of stay distribution
    - Readmission rates
    """

    def __init__(self, log: Union[EventLog, pd.DataFrame]):
        """
        Initialize dashboard with patient journey data.

        :param log: Event log or DataFrame
        """
        self.log = log if isinstance(log, pd.DataFrame) else self._to_dataframe(log)

    def _to_dataframe(self, log: EventLog) -> pd.DataFrame:
        from pm4py import convert_to_dataframe
        return convert_to_dataframe(log)

    def generate(self) -> Dict[str, Any]:
        """
        Generate comprehensive dashboard data.

        :return: Dashboard data dictionary
        """
        return {
            "overview": self._get_overview(),
            "patient_volumes": self._get_patient_volumes(),
            "department_utilization": self._get_department_utilization(),
            "peak_hours": self._get_peak_hours(),
            "length_of_stay": self._get_length_of_stay(),
            "flow_metrics": self._get_flow_metrics(),
        }

    def _get_overview(self) -> Dict[str, Any]:
        """Get overview statistics."""
        from pm4py.util import constants, xes_constants

        case_id_key = constants.CASE_CONCEPT_NAME
        timestamp_key = xes_constants.DEFAULT_TIMESTAMP_KEY

        total_patients = self.log[case_id_key].nunique()
        total_events = len(self.log)

        # Get date range
        min_date = self.log[timestamp_key].min()
        max_date = self.log[timestamp_key].max()
        date_range_days = (max_date - min_date).days + 1

        # Average cases per day
        avg_cases_per_day = total_patients / date_range_days if date_range_days > 0 else 0

        # Most common pathway
        from pm4py.stats import get_variants
        variants = get_variants(self.log)
        most_common = max(variants.items(), key=lambda x: x[1]) if variants else (None, 0)

        return {
            "total_patients": total_patients,
            "total_events": total_events,
            "date_range_days": date_range_days,
            "avg_cases_per_day": round(avg_cases_per_day, 1),
            "most_common_pathway": most_common[0],
            "most_common_pathway_count": most_common[1],
        }

    def _get_patient_volumes(self) -> Dict[str, Any]:
        """Get patient volume trends."""
        from pm4py.util import constants, xes_constants

        timestamp_key = xes_constants.DEFAULT_TIMESTAMP_KEY
        case_id_key = constants.CASE_CONCEPT_NAME

        # Daily volumes
        log = self.log.copy()
        log["date"] = pd.to_datetime(log[timestamp_key]).dt.date
        daily_volumes = log.groupby("date")[case_id_key].nunique().to_dict()

        # Hourly distribution
        log["hour"] = pd.to_datetime(log[timestamp_key]).dt.hour
        hourly_dist = log["hour"].value_counts().sort_index().to_dict()

        # Day of week distribution
        log["dow"] = pd.to_datetime(log[timestamp_key]).dt.dayofweek
        dow_names = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}
        dow_dist = log["dow"].map(dow_names).value_counts().to_dict()

        return {
            "daily_volumes": {str(k): v for k, v in daily_volumes.items()},
            "hourly_distribution": hourly_dist,
            "day_of_week_distribution": dow_dist,
        }

    def _get_department_utilization(self) -> Dict[str, Dict[str, Any]]:
        """Get department utilization metrics."""
        from pm4py.util import constants, xes_constants

        dept_key = "org:department"
        activity_key = xes_constants.DEFAULT_NAME_KEY
        case_id_key = constants.CASE_CONCEPT_NAME
        timestamp_key = xes_constants.DEFAULT_TIMESTAMP_KEY

        if dept_key not in self.log.columns:
            return {"error": "Department attribute not found"}

        dept_stats = {}
        for dept in self.log[dept_key].unique():
            dept_data = self.log[self.log[dept_key] == dept]

            # Calculate duration per case
            case_durations = (
                dept_data.groupby(case_id_key)[timestamp_key]
                .agg(lambda x: x.max() - x.min())
                .dt.total_seconds() / 3600  # Convert to hours
            )

            dept_stats[dept] = {
                "case_count": dept_data[case_id_key].nunique(),
                "event_count": len(dept_data),
                "unique_activities": dept_data[activity_key].nunique(),
                "avg_case_duration_hours": round(case_durations.mean(), 2),
                "median_case_duration_hours": round(case_durations.median(), 2),
                "max_case_duration_hours": round(case_durations.max(), 2),
            }

        return dept_stats

    def _get_peak_hours(self) -> Dict[str, Any]:
        """Identify peak hours for different activities."""
        from pm4py.util import xes_constants

        timestamp_key = xes_constants.DEFAULT_TIMESTAMP_KEY
        activity_key = xes_constants.DEFAULT_NAME_KEY

        log = self.log.copy()
        log["hour"] = pd.to_datetime(log[timestamp_key]).dt.hour

        # Peak hours by activity
        activity_peaks = {}
        for activity in log[activity_key].unique():
            activity_data = log[log[activity_key] == activity]
            hour_counts = activity_data["hour"].value_counts()
            if len(hour_counts) > 0:
                peak_hour = hour_counts.idxmax()
                peak_count = hour_counts.max()
                activity_peaks[activity] = {
                    "peak_hour": int(peak_hour),
                    "peak_count": int(peak_count),
                }

        # Overall peak
        overall_peak = log["hour"].value_counts()
        peak_hour = overall_peak.idxmax()
        peak_count = overall_peak.max()

        return {
            "overall_peak_hour": int(peak_hour),
            "overall_peak_count": int(peak_count),
            "activity_peaks": activity_peaks,
        }

    def _get_length_of_stay(self) -> Dict[str, Any]:
        """Get length of stay statistics."""
        from pm4py.util import constants, xes_constants

        case_id_key = constants.CASE_CONCEPT_NAME
        timestamp_key = xes_constants.DEFAULT_TIMESTAMP_KEY

        # Calculate LOS per case
        case_starts = self.log.groupby(case_id_key)[timestamp_key].min()
        case_ends = self.log.groupby(case_id_key)[timestamp_key].max()
        los_hours = (case_ends - case_starts).dt.total_seconds() / 3600

        return {
            "mean_los_hours": round(los_hours.mean(), 2),
            "median_los_hours": round(los_hours.median(), 2),
            "std_los_hours": round(los_hours.std(), 2),
            "min_los_hours": round(los_hours.min(), 2),
            "max_los_hours": round(los_hours.max(), 2),
            "percentiles": {
                "p25": round(los_hours.quantile(0.25), 2),
                "p50": round(los_hours.quantile(0.50), 2),
                "p75": round(los_hours.quantile(0.75), 2),
                "p90": round(los_hours.quantile(0.90), 2),
                "p95": round(los_hours.quantile(0.95), 2),
            },
            "los_distribution": los_hours.describe().to_dict(),
        }

    def _get_flow_metrics(self) -> Dict[str, Any]:
        """Get patient flow metrics."""
        from pm4py.stats import get_start_activities, get_end_activities
        from pm4py.stats import get_variants

        start_acts = get_start_activities(self.log)
        end_acts = get_end_activities(self.log)

        return {
            "entry_points": start_acts,
            "exit_points": end_acts,
            "total_unique_pathways": len(get_variants(self.log)),
        }


class WaitTimeAnalyzer:
    """
    Wait time analysis for healthcare processes.

    Analyzes:
    - Overall wait time distribution
    - Per-department wait times
    - Per-activity wait times
    - Threshold breaches
    """

    def __init__(self, log: Union[EventLog, pd.DataFrame]):
        """
        Initialize analyzer with patient journey data.

        :param log: Event log or DataFrame
        """
        self.log = log if isinstance(log, pd.DataFrame) else self._to_dataframe(log)

    def _to_dataframe(self, log: EventLog) -> pd.DataFrame:
        from pm4py import convert_to_dataframe
        return convert_to_dataframe(log)

    def analyze(
        self,
        department: Optional[str] = None,
        activity: Optional[str] = None,
        threshold_minutes: float = 30.0,
        timestamp_key: str = "time:timestamp",
        department_key: str = "org:department",
    ) -> Dict[str, Any]:
        """
        Analyze wait times.

        :param department: Filter by department
        :param activity: Filter by activity
        :param threshold_minutes: Wait time threshold for breach detection
        :param timestamp_key: Timestamp attribute name
        :param department_key: Department attribute name
        :return: Wait time analysis results
        """
        from pm4py.util import constants, xes_constants

        activity_key = xes_constants.DEFAULT_NAME_KEY
        case_id_key = constants.CASE_CONCEPT_NAME

        # Filter data
        data = self.log.copy()
        if department and department_key in data.columns:
            data = data[data[department_key] == department]
        if activity:
            data = data[data[activity_key] == activity]

        # Calculate inter-event wait times per case
        data = data.sort_values([case_id_key, timestamp_key])
        data["prev_timestamp"] = data.groupby(case_id_key)[timestamp_key].shift(1)
        data["wait_time_minutes"] = (
            data[timestamp_key] - data["prev_timestamp"]
        ).dt.total_seconds() / 60

        # Drop first events (no wait)
        wait_times = data.dropna(subset=["wait_time_minutes"])["wait_time_minutes"]

        if len(wait_times) == 0:
            return {"error": "No wait times calculated"}

        # Statistics
        breaches = (wait_times > threshold_minutes).sum()
        breach_rate = (breaches / len(wait_times)) * 100

        return {
            "total_waits": len(wait_times),
            "mean_wait_minutes": round(wait_times.mean(), 2),
            "median_wait_minutes": round(wait_times.median(), 2),
            "std_wait_minutes": round(wait_times.std(), 2),
            "min_wait_minutes": round(wait_times.min(), 2),
            "max_wait_minutes": round(wait_times.max(), 2),
            "p90_wait_minutes": round(wait_times.quantile(0.9), 2),
            "p95_wait_minutes": round(wait_times.quantile(0.95), 2),
            "breach_threshold": threshold_minutes,
            "total_breaches": int(breaches),
            "breach_rate_percent": round(breach_rate, 2),
            "filter": {
                "department": department,
                "activity": activity,
            },
        }

    def get_per_activity_wait_times(self) -> Dict[str, Dict[str, float]]:
        """Get wait time statistics per activity."""
        from pm4py.util import xes_constants

        activity_key = xes_constants.DEFAULT_NAME_KEY
        timestamp_key = xes_constants.DEFAULT_TIMESTAMP_KEY

        results = {}
        for activity in self.log[activity_key].unique():
            activity_data = self.log[self.log[activity_key] == activity]
            analysis = self.analyze(activity=activity, timestamp_key=timestamp_key)
            if "error" not in analysis:
                results[activity] = {
                    "mean_wait": analysis["mean_wait_minutes"],
                    "median_wait": analysis["median_wait_minutes"],
                    "p95_wait": analysis["p95_wait_minutes"],
                    "breach_rate": analysis["breach_rate_percent"],
                }

        return results


class BottleneckDetector:
    """
    Bottleneck detection in patient flow.

    Identifies:
    - Activities with high wait times
    - Departments with long queues
    - Resource constraints
    - Process deviations causing delays
    """

    def __init__(self, log: Union[EventLog, pd.DataFrame]):
        """
        Initialize detector with patient journey data.

        :param log: Event log or DataFrame
        """
        self.log = log if isinstance(log, pd.DataFrame) else self._to_dataframe(log)

    def _to_dataframe(self, log: EventLog) -> pd.DataFrame:
        from pm4py import convert_to_dataframe
        return convert_to_dataframe(log)

    def detect(
        self,
        threshold_percentile: float = 75.0,
        activity_key: str = "concept:name",
        timestamp_key: str = "time:timestamp",
        department_key: str = "org:department",
    ) -> List[Dict[str, Any]]:
        """
        Detect bottlenecks in patient flow.

        :param threshold_percentile: Percentile threshold for bottleneck detection
        :param activity_key: Activity attribute name
        :param timestamp_key: Timestamp attribute name
        :param department_key: Department attribute name
        :return: List of detected bottlenecks
        """
        bottlenecks = []

        # Per-activity bottlenecks
        activity_metrics = self._analyze_activity_metrics(
            activity_key, timestamp_key, threshold_percentile
        )

        for activity, metrics in activity_metrics.items():
            if metrics["is_bottleneck"]:
                bottlenecks.append({
                    "type": "activity",
                    "name": activity,
                    "severity": self._calculate_severity(metrics["p95_wait"]),
                    "avg_wait_minutes": metrics["mean_wait"],
                    "p95_wait_minutes": metrics["p95_wait"],
                    "event_count": metrics["event_count"],
                    "recommendation": self._get_activity_recommendation(activity, metrics),
                })

        # Per-department bottlenecks
        if department_key in self.log.columns:
            dept_metrics = self._analyze_department_metrics(
                activity_key, timestamp_key, department_key, threshold_percentile
            )

            for dept, metrics in dept_metrics.items():
                if metrics["is_bottleneck"]:
                    bottlenecks.append({
                        "type": "department",
                        "name": dept,
                        "severity": self._calculate_severity(metrics["p95_duration"]),
                        "avg_duration_hours": metrics["mean_duration"],
                        "p95_duration_hours": metrics["p95_duration"],
                        "case_count": metrics["case_count"],
                        "recommendation": self._get_department_recommendation(dept, metrics),
                    })

        # Sort by severity
        severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        bottlenecks.sort(key=lambda x: severity_order.get(x["severity"], 3))

        return bottlenecks

    def _analyze_activity_metrics(
        self, activity_key: str, timestamp_key: str, threshold_percentile: float
    ) -> Dict[str, Dict[str, Any]]:
        """Analyze metrics per activity."""
        from pm4py.util import constants

        case_id_key = constants.CASE_CONCEPT_NAME

        activity_metrics = {}

        for activity in self.log[activity_key].unique():
            activity_data = self.log[self.log[activity_key] == activity]

            # Calculate wait times
            activity_data = activity_data.sort_values([case_id_key, timestamp_key])
            activity_data["prev_ts"] = activity_data.groupby(case_id_key)[timestamp_key].shift(1)
            activity_data["wait_min"] = (
                activity_data[timestamp_key] - activity_data["prev_ts"]
            ).dt.total_seconds() / 60

            wait_times = activity_data.dropna(subset=["wait_min"])["wait_min"]

            if len(wait_times) > 0:
                threshold = wait_times.quantile(threshold_percentile / 100)
                activity_metrics[activity] = {
                    "mean_wait": round(wait_times.mean(), 2),
                    "p95_wait": round(wait_times.quantile(0.95), 2),
                    "max_wait": round(wait_times.max(), 2),
                    "event_count": len(activity_data),
                    "threshold": round(threshold, 2),
                    "is_bottleneck": wait_times.quantile(0.95) > 30.0,  # 30 min threshold
                }

        return activity_metrics

    def _analyze_department_metrics(
        self,
        activity_key: str,
        timestamp_key: str,
        department_key: str,
        threshold_percentile: float,
    ) -> Dict[str, Dict[str, Any]]:
        """Analyze metrics per department."""
        from pm4py.util import constants

        case_id_key = constants.CASE_CONCEPT_NAME

        dept_metrics = {}

        for dept in self.log[department_key].unique():
            dept_data = self.log[self.log[department_key] == dept]

            # Calculate case duration
            case_durations = (
                dept_data.groupby(case_id_key)[timestamp_key]
                .agg(lambda x: x.max() - x.min())
                .dt.total_seconds() / 3600
            )

            if len(case_durations) > 0:
                threshold = case_durations.quantile(threshold_percentile / 100)
                dept_metrics[dept] = {
                    "mean_duration": round(case_durations.mean(), 2),
                    "p95_duration": round(case_durations.quantile(0.95), 2),
                    "max_duration": round(case_durations.max(), 2),
                    "case_count": dept_data[case_id_key].nunique(),
                    "threshold": round(threshold, 2),
                    "is_bottleneck": case_durations.quantile(0.95) > 4.0,  # 4 hour threshold
                }

        return dept_metrics

    def _calculate_severity(self, value: float) -> str:
        """Calculate severity based on value."""
        if value > 120:  # 2 hours
            return "HIGH"
        elif value > 60:  # 1 hour
            return "MEDIUM"
        else:
            return "LOW"

    def _get_activity_recommendation(self, activity: str, metrics: Dict) -> str:
        """Get recommendation for activity bottleneck."""
        if metrics["p95_wait"] > 120:
            return f"Significant delays at {activity}. Consider adding capacity or streamlining process."
        elif metrics["p95_wait"] > 60:
            return f"Moderate delays at {activity}. Review resource allocation."
        else:
            return f"Minor delays at {activity}. Monitor for trends."

    def _get_department_recommendation(self, dept: str, metrics: Dict) -> str:
        """Get recommendation for department bottleneck."""
        if metrics["p95_duration"] > 8:
            return f"Extended stays in {dept}. Consider capacity expansion or process redesign."
        elif metrics["p95_duration"] > 4:
            return f"Elevated duration in {dept}. Review triage and throughput processes."
        else:
            return f"Monitor {dept} performance for optimization opportunities."


__all__ = [
    'PatientFlowDashboard',
    'WaitTimeAnalyzer',
    'BottleneckDetector',
]
