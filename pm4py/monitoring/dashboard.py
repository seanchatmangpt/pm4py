'''
PM4Py – Monitoring Dashboard Module
Copyright (C) 2026 Process Intelligence Solutions GmbH

Real-time monitoring dashboard for process mining operations.
'''

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import json


class DashboardTheme(Enum):
    """Dashboard themes."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class RefreshInterval(Enum):
    """Dashboard refresh intervals."""
    OFF = "off"
    REALTIME = "1s"
    FAST = "5s"
    NORMAL = "30s"
    SLOW = "60s"


@dataclass
class WidgetConfig:
    """Configuration for a dashboard widget."""
    widget_id: str
    widget_type: str  # "chart", "metric", "table", "alert"
    title: str
    position: Dict[str, int]  # {"x": 0, "y": 0, "w": 4, "h": 2}
    data_source: str
    refresh_interval: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardConfig:
    """Dashboard configuration."""
    dashboard_id: str
    title: str
    description: str = ""
    theme: DashboardTheme = DashboardTheme.LIGHT
    refresh_interval: RefreshInterval = RefreshInterval.NORMAL
    widgets: List[WidgetConfig] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['theme'] = self.theme.value
        data['refresh_interval'] = self.refresh_interval.value
        return data


class MonitoringDashboard:
    """
    Real-time monitoring dashboard for process mining.

    Provides:
    - System health metrics
    - Process discovery status
    - Conformance checking results
    - Drift detection alerts
    - Performance metrics
    """

    # Pre-configured dashboard templates
    TEMPLATES = {
        "overview": DashboardConfig(
            dashboard_id="overview",
            title="PM4Py Overview",
            description="System-wide overview of process mining operations",
            theme=DashboardTheme.LIGHT,
            refresh_interval=RefreshInterval.NORMAL,
            widgets=[
                WidgetConfig(
                    widget_id="system_health",
                    widget_type="metric",
                    title="System Health",
                    position={"x": 0, "y": 0, "w": 3, "h": 2},
                    data_source="system.health",
                ),
                WidgetConfig(
                    widget_id="active_discoveries",
                    widget_type="metric",
                    title="Active Discoveries",
                    position={"x": 3, "y": 0, "w": 3, "h": 2},
                    data_source="system.discoveries",
                ),
                WidgetConfig(
                    widget_id="discovery_throughput",
                    widget_type="chart",
                    title="Discovery Throughput",
                    position={"x": 6, "y": 0, "w": 6, "h": 2},
                    data_source="metrics.throughput",
                    config={"chart_type": "line", "time_range": "1h"},
                ),
                WidgetConfig(
                    widget_id="recent_alerts",
                    widget_type="alert",
                    title="Recent Alerts",
                    position={"x": 0, "y": 2, "w": 12, "h": 3},
                    data_source="alerts.recent",
                    config={"limit": 10},
                ),
            ],
        ),
        "conformance": DashboardConfig(
            dashboard_id="conformance",
            title="Conformance Monitoring",
            description="Real-time conformance checking metrics",
            theme=DashboardTheme.LIGHT,
            refresh_interval=RefreshInterval.FAST,
            widgets=[
                WidgetConfig(
                    widget_id="fitness_scores",
                    widget_type="chart",
                    title="Fitness Scores",
                    position={"x": 0, "y": 0, "w": 6, "h": 3},
                    data_source="conformance.fitness",
                    config={"chart_type": "gauge"},
                ),
                WidgetConfig(
                    widget_id="precision_scores",
                    widget_type="chart",
                    title="Precision Scores",
                    position={"x": 6, "y": 0, "w": 6, "h": 3},
                    data_source="conformance.precision",
                    config={"chart_type": "gauge"},
                ),
                WidgetConfig(
                    widget_id="deviations_table",
                    widget_type="table",
                    title="Recent Deviations",
                    position={"x": 0, "y": 3, "w": 12, "h": 4},
                    data_source="conformance.deviations",
                    config={"columns": ["case_id", "deviation", "timestamp"]},
                ),
            ],
        ),
        "drift": DashboardConfig(
            dashboard_id="drift",
            title="Process Drift Monitoring",
            description="Real-time process drift detection",
            theme=DashboardTheme.LIGHT,
            refresh_interval=RefreshInterval.FAST,
            widgets=[
                WidgetConfig(
                    widget_id="drift_score",
                    widget_type="metric",
                    title="Current Drift Score",
                    position={"x": 0, "y": 0, "w": 4, "h": 2},
                    data_source="drift.score",
                ),
                WidgetConfig(
                    widget_id="drift_trend",
                    widget_type="chart",
                    title="Drift Trend",
                    position={"x": 4, "y": 0, "w": 8, "h": 2},
                    data_source="drift.trend",
                    config={"chart_type": "line", "time_range": "24h"},
                ),
                WidgetConfig(
                    widget_id="drift_events",
                    widget_type="table",
                    title="Drift Events",
                    position={"x": 0, "y": 2, "w": 12, "h": 4},
                    data_source="drift.events",
                    config={"columns": ["timestamp", "type", "severity", "description"]},
                ),
            ],
        ),
    }

    def __init__(self, config: Optional[DashboardConfig] = None):
        self.config = config or self.TEMPLATES["overview"]
        self._data_sources: Dict[str, Callable] = {}
        self._subscribers: List[Callable] = []

        # Register default data sources
        self._register_default_sources()

    def _register_default_sources(self):
        """Register default data source providers."""

        def system_health() -> Dict[str, Any]:
            try:
                metric = SystemMetric.collect()
                return {
                    "status": "healthy" if metric.cpu_percent < 80 else "warning",
                    "cpu_percent": metric.cpu_percent,
                    "memory_usage_mb": round(metric.memory_usage_mb, 2),
                    "uptime_seconds": metric.uptime_seconds,
                }
            except ImportError:
                return {"status": "unknown", "cpu_percent": 0}

        def active_discoveries() -> Dict[str, Any]:
            return {
                "count": 0,  # To be tracked by application
                "capacity": 10,
            }

        def recent_alerts() -> List[Dict[str, Any]]:
            return []  # To be populated by alert manager

        self._data_sources.update({
            "system.health": system_health,
            "system.discoveries": active_discoveries,
            "alerts.recent": recent_alerts,
        })

    def register_data_source(self, name: str, provider: Callable):
        """Register a custom data source."""
        self._data_sources[name] = provider

    def get_widget_data(self, widget: WidgetConfig) -> Dict[str, Any]:
        """Get data for a specific widget."""
        provider = self._data_sources.get(widget.data_source)

        if provider is None:
            return {"error": f"Data source '{widget.data_source}' not found"}

        try:
            return provider()
        except Exception as e:
            return {"error": str(e)}

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for all widgets in the dashboard."""
        return {
            "dashboard": self.config.to_dict(),
            "widgets": {
                widget.widget_id: self.get_widget_data(widget)
                for widget in self.config.widgets
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    def subscribe(self, callback: Callable):
        """Subscribe to dashboard updates."""
        self._subscribers.append(callback)

    def notify_subscribers(self):
        """Notify all subscribers of dashboard updates."""
        data = self.get_dashboard_data()
        for callback in self._subscribers:
            try:
                callback(data)
            except Exception:
                pass  # Don't let one subscriber failure break others

    def to_html(self) -> str:
        """Generate HTML representation of the dashboard."""
        data = self.get_dashboard_data()

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{self.config.title}</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .dashboard {{
                    max-width: 1400px;
                    margin: 0 auto;
                }}
                .dashboard-header {{
                    margin-bottom: 20px;
                }}
                .dashboard-title {{
                    font-size: 24px;
                    font-weight: 600;
                    margin: 0;
                }}
                .dashboard-description {{
                    color: #666;
                    margin-top: 5px;
                }}
                .widget {{
                    background: white;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }}
                .widget-title {{
                    font-size: 16px;
                    font-weight: 600;
                    margin-bottom: 15px;
                }}
                .metric-value {{
                    font-size: 32px;
                    font-weight: 700;
                }}
                .metric-label {{
                    color: #666;
                    font-size: 14px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                th, td {{
                    text-align: left;
                    padding: 12px;
                    border-bottom: 1px solid #eee;
                }}
                th {{
                    font-weight: 600;
                    color: #666;
                }}
                .status-healthy {{ color: #10b981; }}
                .status-warning {{ color: #f59e0b; }}
                .status-error {{ color: #ef4444; }}
            </style>
        </head>
        <body>
            <div class="dashboard">
                <div class="dashboard-header">
                    <h1 class="dashboard-title">{self.config.title}</h1>
                    <p class="dashboard-description">{self.config.description}</p>
                </div>
        """

        # Render widgets
        for widget in self.config.widgets:
            widget_data = data["widgets"].get(widget.widget_id, {})

            if widget.widget_type == "metric":
                html += self._render_metric_widget(widget, widget_data)
            elif widget.widget_type == "chart":
                html += self._render_chart_widget(widget, widget_data)
            elif widget.widget_type == "table":
                html += self._render_table_widget(widget, widget_data)
            elif widget.widget_type == "alert":
                html += self._render_alert_widget(widget, widget_data)

        html += """
            </div>
            <script>
                // Auto-refresh every 30 seconds
                setTimeout(() => location.reload(), 30000);
            </script>
        </body>
        </html>
        """

        return html

    def _render_metric_widget(self, widget: WidgetConfig, data: Dict[str, Any]) -> str:
        """Render a metric widget."""
        if "error" in data:
            return f'<div class="widget"><div class="widget-title">{widget.title}</div>Error: {data["error"]}</div>'

        value = data.get("value", 0)
        status = data.get("status", "healthy")

        return f"""
        <div class="widget">
            <div class="widget-title">{widget.title}</div>
            <div class="metric-value status-{status}">{value}</div>
            <div class="metric-label">Current Status</div>
        </div>
        """

    def _render_chart_widget(self, widget: WidgetConfig, data: Dict[str, Any]) -> str:
        """Render a chart widget."""
        return f'''
        <div class="widget">
            <div class="widget-title">{widget.title}</div>
            <canvas id="{widget.widget_id}"></canvas>
            <script>
                new Chart(document.getElementById("{widget.widget_id}"), {{
                    type: "line",
                    data: {{
                        labels: ["1h ago", "45m ago", "30m ago", "15m ago", "Now"],
                        datasets: [{{
                            label: "Value",
                            data: [10, 12, 8, 15, 14],
                            borderColor: "rgb(75, 192, 192)",
                            tension: 0.1
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        scales: {{
                            y: {{
                                beginAtZero: true
                            }}
                        }}
                    }}
                }});
            </script>
        </div>
        '''

    def _render_table_widget(self, widget: WidgetConfig, data: Dict[str, Any]) -> str:
        """Render a table widget."""
        columns = widget.config.get("columns", [])
        rows = data.get("rows", [])

        header_html = "".join(f"<th>{col}</th>" for col in columns)

        rows_html = ""
        for row in rows[:10]:  # Limit to 10 rows
            cells_html = "".join(f"<td>{row.get(col, '')}</td>" for col in columns)
            rows_html += f"<tr>{cells_html}</tr>"

        return f'''
        <div class="widget">
            <div class="widget-title">{widget.title}</div>
            <table>
                <thead><tr>{header_html}</tr></thead>
                <tbody>{rows_html if rows_html else "<tr><td colspan='{len(columns)}'>No data</td></tr>"}</tbody>
            </table>
        </div>
        '''

    def _render_alert_widget(self, widget: WidgetConfig, data: Dict[str, Any]) -> str:
        """Render an alert widget."""
        alerts = data.get("alerts", [])

        if not alerts:
            return f'''
            <div class="widget">
                <div class="widget-title">{widget.title}</div>
                <p style="color: #10b981;">✓ No recent alerts</p>
            </div>
            '''

        alerts_html = ""
        for alert in alerts[:10]:
            severity = alert.get("severity", "info")
            alerts_html += f'''
            <div style="padding: 10px; margin-bottom: 10px; border-left: 3px solid #ef4444; background: #fef2f2;">
                <strong>[{severity.upper()}]</strong> {alert.get("title", "")}
                <br><small>{alert.get("description", "")}</small>
            </div>
            '''

        return f'''
        <div class="widget">
            <div class="widget-title">{widget.title}</div>
            {alerts_html}
        </div>
        '''

    def save_html(self, output_path: str):
        """Save dashboard as HTML file."""
        html = self.to_html()

        with open(output_path, 'w') as f:
            f.write(html)

    def to_json(self) -> str:
        """Export dashboard configuration and data as JSON."""
        return json.dumps(self.get_dashboard_data(), indent=2, default=str)


def create_dashboard(template: str = "overview", **kwargs) -> MonitoringDashboard:
    """Create a dashboard from a template."""
    if template not in MonitoringDashboard.TEMPLATES:
        raise ValueError(f"Unknown template: {template}. Available: {list(MonitoringDashboard.TEMPLATES.keys())}")

    config = MonitoringDashboard.TEMPLATES[template]

    # Apply customizations
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)

    return MonitoringDashboard(config)


# Import for system metrics
try:
    from pm4py.monitoring.metrics import SystemMetric
except ImportError:
    SystemMetric = None

__all__ = [
    'DashboardTheme',
    'RefreshInterval',
    'WidgetConfig',
    'DashboardConfig',
    'MonitoringDashboard',
    'create_dashboard',
]
