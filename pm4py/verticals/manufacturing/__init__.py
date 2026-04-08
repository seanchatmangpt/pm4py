'''
PM4Py – Manufacturing Vertical
Copyright (C) 2026 Process Intelligence Solutions GmbH

IIoT-ready manufacturing process mining with OEE calculation,
quality conformance, and real-time monitoring.
'''

from typing import Dict, List, Any, Optional, Union
import pandas as pd
from pm4py.objects.log.obj import EventLog
from pm4py.discovery import discover_powl
from pm4py.conformance import conformance_diagnostics_token_based_replay
from pm4py.vis import view_powl, save_vis_powl

from pm4py.verticals.manufacturing.schemas import (
    MANUFACTURING_WORKFLOW_SCHEMA,
    OEE_ATTRIBUTES,
    IIOT_SENSOR_ATTRIBUTES,
    EquipmentType,
    ProductType,
    calculate_oee,
)
from pm4py.verticals.manufacturing.conformance import (
    OEEConformanceChecker,
    QualityConformanceChecker,
    ProductionStandardsChecker,
)
from pm4py.verticals.manufacturing.dashboards import (
    OEEDashboard,
    RealTimeMonitor,
    BottleneckAnalyzer,
)
from pm4py.verticals.manufacturing.demos import generate_synthetic_manufacturing_data


class ManufacturingVertical:
    """
    IIoT-ready manufacturing process mining vertical.

    Features:
    - Production workflow discovery and analysis
    - OEE calculation and monitoring
    - Quality conformance checking
    - Bottleneck detection
    - Real-time equipment monitoring
    - IIoT sensor data integration

    Example:
        >>> import pm4py
        >>> from pm4py.verticals import ManufacturingVertical
        >>>
        >>> # Generate demo data
        >>> log = ManufacturingVertical.generate_demo_data(n_orders=500)
        >>>
        >>> # Discover production workflow
        >>> vertical = ManufacturingVertical(log)
        >>> model = vertical.discover_production_workflow()
        >>>
        >>> # Check OEE conformance
        >>> oee_report = vertical.check_oee_conformance()
        >>>
        >>> # Analyze quality
        >>> quality_report = vertical.check_quality_conformance()
        >>>
        >>> # Detect bottlenecks
        >>> bottlenecks = vertical.detect_bottlenecks()
        >>>
        >>> # Get real-time status
        >>> status = vertical.get_real_time_status()
    """

    def __init__(
        self,
        log: Union[EventLog, pd.DataFrame],
        activity_key: str = "concept:name",
        timestamp_key: str = "time:timestamp",
        case_id_key: str = "case:concept:name",
        equipment_key: str = "equipment:id",
        product_key: str = "production:product_id",
        order_key: str = "production:order_id",
    ):
        """
        Initialize manufacturing vertical with production workflow data.

        :param log: Event log or DataFrame containing manufacturing events
        :param activity_key: Attribute for activity names
        :param timestamp_key: Attribute for timestamps
        :param case_id_key: Attribute for case IDs (production orders)
        :param equipment_key: Attribute for equipment identifiers
        :param product_key: Attribute for product identifiers
        :param order_key: Attribute for production order identifiers
        """
        self.log = log
        self.activity_key = activity_key
        self.timestamp_key = timestamp_key
        self.case_id_key = case_id_key
        self.equipment_key = equipment_key
        self.product_key = product_key
        self.order_key = order_key

        # Initialize components
        self.oee_checker = OEEConformanceChecker()
        self.quality_checker = QualityConformanceChecker()
        self.standards_checker = ProductionStandardsChecker()
        self.oee_dashboard = OEEDashboard(log)
        self.real_time_monitor = RealTimeMonitor(log)
        self.bottleneck_analyzer = BottleneckAnalyzer(log)

    def discover_production_workflow(
        self,
        variant: str = "powl",
    ):
        """
        Discover production workflow process model.

        :param variant: Discovery algorithm ('inductive', 'heuristic', 'powl')
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

    def check_oee_conformance(
        self,
        oee_threshold: float = 60.0,
    ) -> Dict[str, Any]:
        """
        Check OEE conformance of the manufacturing data.

        Verifies:
        - Availability thresholds
        - Performance thresholds
        - Quality thresholds
        - World-class vs acceptable standards

        :param oee_threshold: Minimum acceptable OEE percentage
        :return: OEE conformance report with violations and recommendations
        """
        return self.oee_checker.check(self.log, oee_threshold=oee_threshold)

    def check_quality_conformance(
        self,
        defect_threshold: float = 5.0,
    ) -> Dict[str, Any]:
        """
        Check quality conformance.

        Verifies:
        - Quality check coverage
        - Defect rates
        - Rework and scrap rates
        - Inspection compliance

        :param defect_threshold: Maximum acceptable defect rate percentage
        :return: Quality conformance report
        """
        return self.quality_checker.check(self.log, defect_threshold=defect_threshold)

    def check_production_standards(
        self,
        target_cycle_time: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Check production standards conformance.

        Verifies:
        - Cycle time compliance
        - Maintenance schedule adherence
        - Documentation completeness

        :param target_cycle_time: Target cycle time in seconds
        :return: Production standards report
        """
        return self.standards_checker.check(self.log, target_cycle_time=target_cycle_time)

    def calculate_oee_metrics(self) -> Dict[str, Any]:
        """
        Calculate OEE metrics for the manufacturing data.

        :return: OEE metrics including availability, performance, quality, and overall OEE
        """
        dashboard_data = self.oee_dashboard.generate()

        return {
            "overall_oee": dashboard_data["overview"]["overall_oee"],
            "oee_breakdown": dashboard_data["oee_breakdown"],
            "equipment_analysis": dashboard_data["equipment_analysis"],
            "downtime_analysis": dashboard_data["downtime_analysis"],
            "throughput_analysis": dashboard_data["throughput_analysis"],
        }

    def detect_bottlenecks(
        self,
        threshold_percentile: float = 75,
    ) -> Dict[str, Any]:
        """
        Detect bottlenecks in the manufacturing process.

        :param threshold_percentile: Percentile threshold for identifying bottlenecks
        :return: Bottleneck analysis results
        """
        return self.bottleneck_analyzer.detect(threshold_percentile=threshold_percentile)

    def get_real_time_status(self) -> Dict[str, Any]:
        """
        Get real-time monitoring status.

        :return: Real-time status including equipment status, active orders, and alerts
        """
        return self.real_time_monitor.get_status()

    def analyze_equipment_utilization(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyze equipment utilization.

        :return: Equipment-wise utilization statistics
        """
        log_df = self.log if isinstance(self.log, pd.DataFrame) else self._to_dataframe(self.log)

        if self.equipment_key not in log_df.columns:
            return {"error": "Equipment key not found in log"}

        stats = {}
        for equipment in log_df[self.equipment_key].unique():
            equipment_data = log_df[log_df[self.equipment_key] == equipment]

            # Calculate utilization
            if "equipment:status" in equipment_data.columns:
                status_counts = equipment_data["equipment:status"].value_counts()
                total_events = len(equipment_data)
                running_percent = (status_counts.get("running", 0) / total_events * 100) if total_events > 0 else 0

                stats[equipment] = {
                    "total_events": total_events,
                    "running_percent": round(running_percent, 2),
                    "idle_percent": round((status_counts.get("idle", 0) / total_events * 100) if total_events > 0 else 0, 2),
                    "maintenance_percent": round((status_counts.get("maintenance", 0) / total_events * 100) if total_events > 0 else 0, 2),
                    "breakdown_percent": round((status_counts.get("breakdown", 0) / total_events * 100) if total_events > 0 else 0, 2),
                    "order_count": equipment_data[self.case_id_key].nunique(),
                }

        return stats

    def analyze_production_flow(self) -> Dict[str, Any]:
        """
        Analyze production flow patterns.

        :return: Production flow analysis
        """
        log_df = self.log if isinstance(self.log, pd.DataFrame) else self._to_dataframe(self.log)

        # Get process variants
        from pm4py.statistics.variants.log import get
        variants = get.get_variants(log_df)

        # Analyze flow time - use aggregation to avoid Series.total_seconds() issue
        case_durations = log_df.groupby(self.case_id_key).apply(
            lambda g: (g[self.timestamp_key].max() - g[self.timestamp_key].min())
        ).dt.total_seconds()

        return {
            "total_variants": len(variants),
            "top_variants": sorted(variants.items(), key=lambda x: len(x[1]), reverse=True)[:10],
            "avg_flow_time_seconds": round(case_durations.mean(), 2) if len(case_durations) > 0 else 0,
            "median_flow_time_seconds": round(case_durations.median(), 2) if len(case_durations) > 0 else 0,
            "p95_flow_time_seconds": round(case_durations.quantile(0.95), 2) if len(case_durations) > 0 else 0,
        }

    def generate_production_report(
        self,
        report_type: str = "oee_summary",
    ) -> Dict[str, Any]:
        """
        Generate production report.

        :param report_type: Type of report ('oee_summary', 'quality_report', 'equipment_report')
        :return: Production report data
        """
        if report_type == "oee_summary":
            return self._generate_oee_summary_report()
        elif report_type == "quality_report":
            return self._generate_quality_report()
        elif report_type == "equipment_report":
            return self._generate_equipment_report()
        else:
            raise ValueError(f"Unknown report type: {report_type}")

    def _generate_oee_summary_report(self) -> Dict[str, Any]:
        """Generate OEE summary report."""
        oee_metrics = self.calculate_oee_metrics()
        oee_conformance = self.check_oee_conformance()

        return {
            "report_type": "oee_summary",
            "report_timestamp": pd.Timestamp.now().isoformat(),
            "overall_oee": oee_metrics["overall_oee"],
            "oee_conformance": oee_conformance["status"],
            "conformance_score": oee_conformance["conformance_score"],
            "violations": oee_conformance["violations"],
            "recommendations": oee_conformance["recommendations"],
        }

    def _generate_quality_report(self) -> Dict[str, Any]:
        """Generate quality report."""
        quality_conformance = self.check_quality_conformance()

        return {
            "report_type": "quality_report",
            "report_timestamp": pd.Timestamp.now().isoformat(),
            "compliance_status": quality_conformance["compliant"],
            "violations": quality_conformance["violations"],
            "summary": quality_conformance["summary"],
        }

    def _generate_equipment_report(self) -> Dict[str, Any]:
        """Generate equipment report."""
        utilization = self.analyze_equipment_utilization()
        bottlenecks = self.detect_bottlenecks()

        return {
            "report_type": "equipment_report",
            "report_timestamp": pd.Timestamp.now().isoformat(),
            "equipment_utilization": utilization,
            "equipment_bottlenecks": bottlenecks["equipment_bottlenecks"],
        }

    def visualize_production_flow(
        self,
        format: str = "png",
        output_path: Optional[str] = None
    ):
        """
        Visualize production workflow process model.

        :param format: Output format ('png', 'svg', 'pdf')
        :param output_path: Output file path (optional)
        """
        model = self.discover_production_workflow(variant="powl")
        if output_path:
            save_vis_powl(model, file_path=output_path)
        else:
            view_powl(model, format=format)

    def _to_dataframe(self, log: EventLog) -> pd.DataFrame:
        """Convert EventLog to DataFrame."""
        from pm4py.conversion import convert_to_dataframe
        return convert_to_dataframe(log)

    @staticmethod
    def generate_demo_data(
        n_orders: int = 500,
        n_equipment: int = 15,
        n_products: int = 20,
        seed: int = 42,
        return_dataframe: bool = True,
    ) -> Union[pd.DataFrame, EventLog]:
        """
        Generate synthetic manufacturing data for testing.

        :param n_orders: Number of production orders to generate
        :param n_equipment: Number of equipment units to simulate
        :param n_products: Number of product types
        :param seed: Random seed for reproducibility
        :param return_dataframe: Return DataFrame instead of EventLog
        :return: Synthetic manufacturing workflow log
        """
        return generate_synthetic_manufacturing_data(
            n_orders=n_orders,
            n_equipment=n_equipment,
            n_products=n_products,
            seed=seed,
            return_dataframe=return_dataframe,
        )


# Convenience functions
def quick_analyze(log: Union[EventLog, pd.DataFrame]) -> Dict[str, Any]:
    """
    Quick analysis of manufacturing workflow data.

    Returns comprehensive analysis including:
    - Process model
    - OEE conformance
    - Quality conformance
    - Bottleneck detection
    - Real-time status

    :param log: Manufacturing workflow event log
    :return: Comprehensive analysis results
    """
    vertical = ManufacturingVertical(log)

    return {
        "model": vertical.discover_production_workflow(),
        "oee_conformance": vertical.check_oee_conformance(),
        "quality_conformance": vertical.check_quality_conformance(),
        "oee_metrics": vertical.calculate_oee_metrics(),
        "bottlenecks": vertical.detect_bottlenecks(),
        "real_time_status": vertical.get_real_time_status(),
        "equipment_utilization": vertical.analyze_equipment_utilization(),
    }


__all__ = [
    'ManufacturingVertical',
    'quick_analyze',
    'MANUFACTURING_WORKFLOW_SCHEMA',
    'OEE_ATTRIBUTES',
    'IIOT_SENSOR_ATTRIBUTES',
]
