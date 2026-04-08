'''
PM4Py – Manufacturing Dashboards
Copyright (C) 2026 Process Intelligence Solutions GmbH

OEE visualization, real-time monitoring, and production analytics.
'''

from typing import Dict, List, Any, Optional, Union
import pandas as pd
import numpy as np
from pm4py.objects.log.obj import EventLog
from pm4py.statistics.variants.log import get as get_variants

from pm4py.verticals.manufacturing.schemas import (
    OEE_ATTRIBUTES,
    OEE_CALCULATION_STANDARDS,
    EquipmentType,
)


class OEEDashboard:
    """
    OEE (Overall Equipment Effectiveness) dashboard generator.

    Creates comprehensive dashboards showing:
    - Overall OEE trends
    - Availability, performance, quality breakdown
    - Equipment-wise OEE
    - Downtime analysis
    - Production throughput
    """

    def __init__(self, log: Union[EventLog, pd.DataFrame]):
        """
        Initialize dashboard with manufacturing data.

        :param log: Event log or DataFrame
        """
        self.log = log if isinstance(log, pd.DataFrame) else self._to_dataframe(log)

    def _to_dataframe(self, log: EventLog) -> pd.DataFrame:
        from pm4py.objects.conversion.log import converter as log_converter
        return log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME)

    def generate(self) -> Dict[str, Any]:
        """
        Generate comprehensive OEE dashboard data.

        :return: Dashboard data dictionary
        """
        return {
            "overview": self._get_overview(),
            "oee_breakdown": self._get_oee_breakdown(),
            "equipment_analysis": self._get_equipment_analysis(),
            "downtime_analysis": self._get_downtime_analysis(),
            "throughput_analysis": self._get_throughput_analysis(),
            "trend_analysis": self._get_trend_analysis(),
        }

    def _get_overview(self) -> Dict[str, Any]:
        """Get overview statistics."""
        from pm4py.util import constants

        case_id_key = constants.CASE_CONCEPT_NAME
        timestamp_key = "time:timestamp"

        total_orders = self.log[case_id_key].nunique()
        total_events = len(self.log)

        # Get date range
        min_date = self.log[timestamp_key].min()
        max_date = self.log[timestamp_key].max()
        date_range_days = (max_date - min_date).days + 1

        # Calculate overall OEE
        overall_oee = self._calculate_overall_oee()

        return {
            "total_orders": total_orders,
            "total_events": total_events,
            "date_range_days": date_range_days,
            "avg_orders_per_day": round(total_orders / date_range_days, 1) if date_range_days > 0 else 0,
            "overall_oee": overall_oee,
            "oee_status": self._get_oee_status(overall_oee.get("oee", 0)),
        }

    def _calculate_overall_oee(self) -> Dict[str, float]:
        """Calculate overall OEE from the log."""
        oee = {"availability": 0, "performance": 0, "quality": 0, "oee": 0}

        if "oee:oee" in self.log.columns:
            oee["oee"] = round(self.log["oee:oee"].mean(), 2)

        if "oee:availability" in self.log.columns:
            oee["availability"] = round(self.log["oee:availability"].mean(), 2)

        if "oee:performance" in self.log.columns:
            oee["performance"] = round(self.log["oee:performance"].mean(), 2)

        if "oee:quality" in self.log.columns:
            oee["quality"] = round(self.log["oee:quality"].mean(), 2)

        # If OEE not directly calculated, compute from components
        if oee["oee"] == 0 and all(v > 0 for v in [oee["availability"], oee["performance"], oee["quality"]]):
            oee["oee"] = round(oee["availability"] * oee["performance"] * oee["quality"] / 10000, 2)

        return oee

    def _get_oee_status(self, oee_value: float) -> str:
        """Get OEE status classification."""
        world_class = OEE_CALCULATION_STANDARDS["oee"]["world_class"]
        acceptable = OEE_CALCULATION_STANDARDS["oee"]["acceptable"]

        if oee_value >= world_class:
            return "WORLD_CLASS"
        elif oee_value >= acceptable:
            return "ACCEPTABLE"
        else:
            return "NEEDS_IMPROVEMENT"

    def _get_oee_breakdown(self) -> Dict[str, Any]:
        """Get OEE component breakdown."""
        breakdown = {
            "availability": {"current": 0, "target": OEE_CALCULATION_STANDARDS["availability"]["acceptable"]},
            "performance": {"current": 0, "target": OEE_CALCULATION_STANDARDS["performance"]["acceptable"]},
            "quality": {"current": 0, "target": OEE_CALCULATION_STANDARDS["quality"]["acceptable"]},
        }

        if "oee:availability" in self.log.columns:
            breakdown["availability"]["current"] = round(self.log["oee:availability"].mean(), 2)

        if "oee:performance" in self.log.columns:
            breakdown["performance"]["current"] = round(self.log["oee:performance"].mean(), 2)

        if "oee:quality" in self.log.columns:
            breakdown["quality"]["current"] = round(self.log["oee:quality"].mean(), 2)

        return breakdown

    def _get_equipment_analysis(self) -> Dict[str, Dict[str, Any]]:
        """Get equipment-wise OEE analysis."""
        from pm4py.util import constants

        equipment_key = "equipment:id"
        case_id_key = constants.CASE_CONCEPT_NAME

        if equipment_key not in self.log.columns:
            return {"error": "Equipment ID not found"}

        equipment_stats = {}
        for equipment in self.log[equipment_key].unique():
            equipment_data = self.log[self.log[equipment_key] == equipment]

            stats = {
                "order_count": equipment_data[case_id_key].nunique(),
                "event_count": len(equipment_data),
            }

            # Calculate OEE for this equipment
            if "oee:oee" in equipment_data.columns:
                stats["oee"] = round(equipment_data["oee:oee"].mean(), 2)

            if "oee:availability" in equipment_data.columns:
                stats["availability"] = round(equipment_data["oee:availability"].mean(), 2)

            if "oee:performance" in equipment_data.columns:
                stats["performance"] = round(equipment_data["oee:performance"].mean(), 2)

            if "oee:quality" in equipment_data.columns:
                stats["quality"] = round(equipment_data["oee:quality"].mean(), 2)

            # Calculate total downtime
            if "oee:downtime" in equipment_data.columns:
                stats["total_downtime_minutes"] = round(equipment_data["oee:downtime"].sum(), 2)

            # Calculate total production
            if "oee:total_pieces" in equipment_data.columns:
                stats["total_pieces"] = int(equipment_data["oee:total_pieces"].sum())

            if "oee:good_pieces" in equipment_data.columns:
                stats["good_pieces"] = int(equipment_data["oee:good_pieces"].sum())

            equipment_stats[equipment] = stats

        return equipment_stats

    def _get_downtime_analysis(self) -> Dict[str, Any]:
        """Get downtime analysis."""
        analysis = {
            "total_downtime_minutes": 0,
            "avg_downtime_per_event": 0,
            "downtime_by_equipment": {},
            "downtime_by_reason": {},
        }

        if "oee:downtime" not in self.log.columns:
            return analysis

        analysis["total_downtime_minutes"] = round(self.log["oee:downtime"].sum(), 2)
        analysis["avg_downtime_per_event"] = round(self.log["oee:downtime"].mean(), 2)

        # Downtime by equipment
        if "equipment:id" in self.log.columns:
            downtime_by_equipment = self.log.groupby("equipment:id")["oee:downtime"].sum().to_dict()
            analysis["downtime_by_equipment"] = {k: round(v, 2) for k, v in downtime_by_equipment.items()}

        # Downtime by reason (if maintenance reason code available)
        if "maintenance:reason_code" in self.log.columns:
            downtime_by_reason = self.log.groupby("maintenance:reason_code")["oee:downtime"].sum().to_dict()
            analysis["downtime_by_reason"] = {k: round(v, 2) for k, v in downtime_by_reason.items()}

        return analysis

    def _get_throughput_analysis(self) -> Dict[str, Any]:
        """Get production throughput analysis."""
        from pm4py.util import constants

        case_id_key = constants.CASE_CONCEPT_NAME
        timestamp_key = "time:timestamp"

        analysis = {
            "total_pieces": 0,
            "good_pieces": 0,
            "defective_pieces": 0,
            "yield_rate": 0,
            "throughput_per_hour": 0,
        }

        if "oee:total_pieces" in self.log.columns:
            analysis["total_pieces"] = int(self.log["oee:total_pieces"].sum())

        if "oee:good_pieces" in self.log.columns:
            analysis["good_pieces"] = int(self.log["oee:good_pieces"].sum())

        if "oee:defective_pieces" in self.log.columns:
            analysis["defective_pieces"] = int(self.log["oee:defective_pieces"].sum())

        # Calculate yield rate
        if analysis["total_pieces"] > 0:
            analysis["yield_rate"] = round((analysis["good_pieces"] / analysis["total_pieces"]) * 100, 2)

        # Calculate throughput per hour
        min_time = self.log[timestamp_key].min()
        max_time = self.log[timestamp_key].max()
        hours = (max_time - min_time).total_seconds() / 3600

        if hours > 0 and analysis["total_pieces"] > 0:
            analysis["throughput_per_hour"] = round(analysis["total_pieces"] / hours, 2)

        return analysis

    def _get_trend_analysis(self) -> Dict[str, Any]:
        """Get OEE trend over time."""
        from pm4py.util import constants

        timestamp_key = "time:timestamp"

        if timestamp_key not in self.log.columns:
            return {"error": "Timestamp not found"}

        self.log["date"] = pd.to_datetime(self.log[timestamp_key]).dt.date

        # Daily OEE
        daily_oee = {}
        if "oee:oee" in self.log.columns:
            daily_oee = self.log.groupby("date")["oee:oee"].mean().to_dict()
            daily_oee = {str(k): round(v, 2) for k, v in daily_oee.items()}

        # Hourly OEE distribution
        self.log["hour"] = pd.to_datetime(self.log[timestamp_key]).dt.hour
        hourly_oee = {}
        if "oee:oee" in self.log.columns:
            hourly_oee = self.log.groupby("hour")["oee:oee"].mean().to_dict()
            hourly_oee = {int(k): round(v, 2) for k, v in hourly_oee.items()}

        return {
            "daily_oee": daily_oee,
            "hourly_oee": hourly_oee,
        }


class RealTimeMonitor:
    """
    Real-time manufacturing monitoring dashboard.

    Monitors:
    - Equipment status
    - Active production orders
    - Quality alerts
    - Maintenance alerts
    - IIoT sensor readings
    """

    def __init__(self, log: Union[EventLog, pd.DataFrame]):
        """
        Initialize monitor with manufacturing data.

        :param log: Event log or DataFrame
        """
        self.log = log if isinstance(log, pd.DataFrame) else self._to_dataframe(log)

    def _to_dataframe(self, log: EventLog) -> pd.DataFrame:
        from pm4py.objects.conversion.log import converter as log_converter
        return log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME)

    def get_status(self) -> Dict[str, Any]:
        """
        Get current real-time monitoring status.

        :return: Real-time status summary
        """
        return {
            "equipment_status": self._get_equipment_status(),
            "active_orders": self._get_active_orders(),
            "quality_alerts": self._get_quality_alerts(),
            "maintenance_alerts": self._get_maintenance_alerts(),
            "sensor_alerts": self._get_sensor_alerts(),
        }

    def _get_equipment_status(self) -> Dict[str, Any]:
        """Get current equipment status."""
        equipment_key = "equipment:id"
        status_key = "equipment:status"

        if equipment_key not in self.log.columns:
            return {"error": "Equipment ID not found"}

        # Get most recent status per equipment
        if status_key in self.log.columns:
            from pm4py.util import constants
            timestamp_key = "time:timestamp"

            self.log = self.log.sort_values(timestamp_key)
            latest_status = self.log.groupby(equipment_key).last()
            status_counts = latest_status[status_key].value_counts().to_dict()

            return {
                "total_equipment": self.log[equipment_key].nunique(),
                "running": status_counts.get("running", 0),
                "idle": status_counts.get("idle", 0),
                "maintenance": status_counts.get("maintenance", 0),
                "breakdown": status_counts.get("breakdown", 0),
                "setup": status_counts.get("setup", 0),
            }

        return {"total_equipment": self.log[equipment_key].nunique()}

    def _get_active_orders(self) -> List[Dict[str, Any]]:
        """Get active production orders."""
        from pm4py.util import constants

        case_id_key = constants.CASE_CONCEPT_NAME
        timestamp_key = "time:timestamp"
        order_key = "production:order_id"

        active_orders = []

        if case_id_key in self.log.columns and "concept:name" in self.log.columns:
            # Find orders that haven't completed
            completed_activities = ["order_completion", "shipping"]

            for case_id in self.log[case_id_key].unique():
                case_data = self.log[self.log[case_id_key] == case_id]

                # Check if order has completion activity
                has_completion = case_data["concept:name"].isin(completed_activities).any()

                if not has_completion:
                    last_event = case_data.sort_values(timestamp_key).iloc[-1]

                    order_info = {
                        "order_id": case_id,
                        "current_activity": last_event["concept:name"],
                        "last_update": last_event[timestamp_key].isoformat(),
                    }

                    if order_key in case_data.columns:
                        order_info["production_order"] = case_data[order_key].iloc[0]

                    active_orders.append(order_info)

        return active_orders[:50]  # Limit to 50 active orders

    def _get_quality_alerts(self) -> List[Dict[str, Any]]:
        """Get quality-related alerts."""
        alerts = []

        # Check for recent quality failures
        if "quality:status" in self.log.columns:
            from pm4py.util import constants
            timestamp_key = "time:timestamp"

            recent_failures = self.log[
                (self.log["quality:status"] == "fail") |
                (self.log["quality:status"] == "scrap")
            ]

            if len(recent_failures) > 0:
                # Get last 10 failures
                recent_failures = recent_failures.sort_values(timestamp_key, ascending=False).head(10)

                for _, row in recent_failures.iterrows():
                    alert = {
                        "type": "QUALITY_FAILURE",
                        "severity": "HIGH",
                        "timestamp": row[timestamp_key].isoformat(),
                        "status": row["quality:status"],
                    }

                    if "equipment:id" in row:
                        alert["equipment"] = row["equipment:id"]

                    if "quality:defect_code" in row:
                        alert["defect_code"] = row["quality:defect_code"]

                    alerts.append(alert)

        return alerts

    def _get_maintenance_alerts(self) -> List[Dict[str, Any]]:
        """Get maintenance-related alerts."""
        alerts = []

        # Check for recent breakdowns
        if "concept:name" in self.log.columns:
            from pm4py.util import constants
            timestamp_key = "time:timestamp"

            breakdown_events = self.log[self.log["concept:name"] == "equipment_breakdown"]

            if len(breakdown_events) > 0:
                # Get last 10 breakdowns
                recent_breakdowns = breakdown_events.sort_values(timestamp_key, ascending=False).head(10)

                for _, row in recent_breakdowns.iterrows():
                    alert = {
                        "type": "EQUIPMENT_BREAKDOWN",
                        "severity": "HIGH",
                        "timestamp": row[timestamp_key].isoformat(),
                    }

                    if "equipment:id" in row:
                        alert["equipment"] = row["equipment:id"]

                    alerts.append(alert)

        return alerts

    def _get_sensor_alerts(self) -> List[Dict[str, Any]]:
        """Get IIoT sensor alerts."""
        alerts = []

        # Check for active sensor alarms
        if "iot:alarm_active" in self.log.columns:
            from pm4py.util import constants
            timestamp_key = "time:timestamp"

            active_alarms = self.log[self.log["iot:alarm_active"] == True]

            if len(active_alarms) > 0:
                # Get last 20 alarms
                recent_alarms = active_alarms.sort_values(timestamp_key, ascending=False).head(20)

                for _, row in recent_alarms.iterrows():
                    alert = {
                        "type": "SENSOR_ALARM",
                        "severity": "MEDIUM",
                        "timestamp": row[timestamp_key].isoformat(),
                    }

                    if "iot:sensor_id" in row:
                        alert["sensor_id"] = row["iot:sensor_id"]

                    if "iot:sensor_type" in row:
                        alert["sensor_type"] = row["iot:sensor_type"]

                    if "iot:sensor_value" in row:
                        alert["sensor_value"] = row["iot:sensor_value"]

                    if "equipment:id" in row:
                        alert["equipment"] = row["equipment:id"]

                    alerts.append(alert)

        return alerts


class BottleneckAnalyzer:
    """
    Bottleneck detection for manufacturing processes.

    Identifies:
    - High-wait activities
    - Equipment bottlenecks
    - Production flow constraints
    - Capacity limitations
    """

    def __init__(self, log: Union[EventLog, pd.DataFrame]):
        """
        Initialize analyzer with manufacturing data.

        :param log: Event log or DataFrame
        """
        self.log = log if isinstance(log, pd.DataFrame) else self._to_dataframe(log)

    def _to_dataframe(self, log: EventLog) -> pd.DataFrame:
        from pm4py.objects.conversion.log import converter as log_converter
        return log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME)

    def detect(
        self,
        threshold_percentile: float = 75,
    ) -> Dict[str, Any]:
        """
        Detect bottlenecks in the manufacturing process.

        :param threshold_percentile: Percentile threshold for identifying bottlenecks
        :return: Bottleneck analysis results
        """
        return {
            "activity_bottlenecks": self._detect_activity_bottlenecks(threshold_percentile),
            "equipment_bottlenecks": self._detect_equipment_bottlenecks(threshold_percentile),
            "flow_bottlenecks": self._detect_flow_bottlenecks(),
        }

    def _detect_activity_bottlenecks(self, percentile: float) -> List[Dict[str, Any]]:
        """Detect activity-level bottlenecks."""
        from pm4py.util import constants

        activity_key = "concept:name"
        case_id_key = constants.CASE_CONCEPT_NAME
        timestamp_key = "time:timestamp"

        if activity_key not in self.log.columns:
            return [{"error": "Activity name not found"}]

        bottlenecks = []

        # Calculate cycle time per activity
        for activity in self.log[activity_key].unique():
            activity_data = self.log[self.log[activity_key] == activity]

            # Calculate duration for each case
            case_durations = activity_data.groupby(case_id_key)[timestamp_key].apply(
                lambda x: (x.max() - x.min()).total_seconds()
            )

            if len(case_durations) > 0:
                avg_duration = case_durations.mean()
                p75_duration = case_durations.quantile(percentile / 100)

                bottlenecks.append({
                    "activity": activity,
                    "avg_duration_seconds": round(avg_duration, 2),
                    "p75_duration_seconds": round(p75_duration, 2),
                    "case_count": len(case_durations),
                    "is_bottleneck": avg_duration > p75_duration,
                })

        # Sort by avg duration descending
        bottlenecks.sort(key=lambda x: x["avg_duration_seconds"], reverse=True)

        return bottlenecks

    def _detect_equipment_bottlenecks(self, percentile: float) -> List[Dict[str, Any]]:
        """Detect equipment-level bottlenecks."""
        from pm4py.util import constants

        equipment_key = "equipment:id"
        case_id_key = constants.CASE_CONCEPT_NAME
        timestamp_key = "time:timestamp"

        if equipment_key not in self.log.columns:
            return [{"error": "Equipment ID not found"}]

        bottlenecks = []

        for equipment in self.log[equipment_key].unique():
            equipment_data = self.log[self.log[equipment_key] == equipment]

            # Calculate utilization (running time / total time)
            if "equipment:status" in equipment_data.columns:
                running_count = (equipment_data["equipment:status"] == "running").sum()
                utilization = (running_count / len(equipment_data)) * 100
            else:
                utilization = 0

            # Calculate case processing time
            case_durations = equipment_data.groupby(case_id_key)[timestamp_key].apply(
                lambda x: (x.max() - x.min()).total_seconds()
            )

            avg_duration = case_durations.mean() if len(case_durations) > 0 else 0

            bottlenecks.append({
                "equipment": equipment,
                "utilization_percent": round(utilization, 2),
                "avg_case_duration_seconds": round(avg_duration, 2),
                "case_count": len(case_durations),
                "is_bottleneck": utilization > 85,  # High utilization = potential bottleneck
            })

        # Sort by utilization descending
        bottlenecks.sort(key=lambda x: x["utilization_percent"], reverse=True)

        return bottlenecks

    def _detect_flow_bottlenecks(self) -> List[Dict[str, Any]]:
        """Detect flow bottlenecks using process variants."""
        from pm4py.util import constants

        case_id_key = constants.CASE_CONCEPT_NAME
        timestamp_key = "time:timestamp"

        # Calculate case duration
        case_durations = self.log.groupby(case_id_key)[timestamp_key].apply(
            lambda x: (x.max() - x.min()).total_seconds()
        )

        # Identify long-running cases (top 25%)
        threshold = case_durations.quantile(0.75)

        long_cases = case_durations[case_durations > threshold]

        bottlenecks = []

        if len(long_cases) > 0:
            # Analyze activities in long cases
            long_case_data = self.log[self.log[case_id_key].isin(long_cases.index)]

            activity_counts = long_case_data["concept:name"].value_counts()

            for activity, count in activity_counts.head(10).items():
                bottlenecks.append({
                    "activity": activity,
                    "occurrence_in_long_cases": count,
                    "avg_case_duration": round(long_cases.mean(), 2),
                })

        return bottlenecks


__all__ = [
    'OEEDashboard',
    'RealTimeMonitor',
    'BottleneckAnalyzer',
]
