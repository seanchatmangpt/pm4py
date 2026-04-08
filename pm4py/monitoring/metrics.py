'''
PM4Py – Metrics Collection Module
Copyright (C) 2026 Process Intelligence Solutions GmbH

Real-time metrics collection for process mining operations.
'''

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import time
import threading


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"  # Monotonically increasing value
    GAUGE = "gauge"  # Value that can go up or down
    HISTOGRAM = "histogram"  # Distribution of values
    SUMMARY = "summary"  # Count, sum, and quantiles


@dataclass
class MetricValue:
    """A single metric value."""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE


@dataclass
class HistogramBucket:
    """A histogram bucket."""
    upper_bound: float
    count: int


class Metric(ABC):
    """Base class for metrics."""

    def __init__(self, name: str, description: str, labels: Optional[Dict[str, str]] = None):
        self.name = name
        self.description = description
        self.labels = labels or {}
        self.created_at = datetime.utcnow()

    @abstractmethod
    def get_value(self) -> MetricValue:
        """Get current metric value."""
        pass

    @abstractmethod
    def reset(self):
        """Reset metric value."""
        pass


class Counter(Metric):
    """A counter metric that only increases."""

    def __init__(
        self,
        name: str,
        description: str,
        initial_value: float = 0.0,
        labels: Optional[Dict[str, str]] = None,
    ):
        super().__init__(name, description, labels)
        self._value = initial_value
        self._lock = threading.Lock()

    def inc(self, delta: float = 1.0):
        """Increment the counter."""
        with self._lock:
            if delta < 0:
                raise ValueError("Counter can only be incremented")
            self._value += delta

    def get_value(self) -> MetricValue:
        """Get current counter value."""
        with self._lock:
            return MetricValue(
                name=self.name,
                value=self._value,
                timestamp=datetime.utcnow(),
                labels=self.labels,
                metric_type=MetricType.COUNTER,
            )

    def reset(self):
        """Reset counter to initial value."""
        with self._lock:
            self._value = 0.0


class Gauge(Metric):
    """A gauge metric that can go up or down."""

    def __init__(
        self,
        name: str,
        description: str,
        initial_value: float = 0.0,
        labels: Optional[Dict[str, str]] = None,
    ):
        super().__init__(name, description, labels)
        self._value = initial_value
        self._lock = threading.Lock()

    def set(self, value: float):
        """Set the gauge value."""
        with self._lock:
            self._value = value

    def inc(self, delta: float = 1.0):
        """Increment the gauge."""
        with self._lock:
            self._value += delta

    def dec(self, delta: float = 1.0):
        """Decrement the gauge."""
        with self._lock:
            self._value -= delta

    def get_value(self) -> MetricValue:
        """Get current gauge value."""
        with self._lock:
            return MetricValue(
                name=self.name,
                value=self._value,
                timestamp=datetime.utcnow(),
                labels=self.labels,
                metric_type=MetricType.GAUGE,
            )

    def reset(self):
        """Reset gauge to zero."""
        with self._lock:
            self._value = 0.0


class Histogram(Metric):
    """A histogram metric that tracks distribution."""

    def __init__(
        self,
        name: str,
        description: str,
        buckets: Optional[List[float]] = None,
        labels: Optional[Dict[str, str]] = None,
    ):
        super().__init__(name, description, labels)
        self.buckets = buckets or [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        self._bucket_counts = {b: 0 for b in self.buckets}
        self._bucket_counts[float('inf')] = 0
        self._count = 0
        self._sum = 0.0
        self._lock = threading.Lock()

    def observe(self, value: float):
        """Observe a value."""
        with self._lock:
            self._count += 1
            self._sum += value

            for bucket in self.buckets:
                if value <= bucket:
                    self._bucket_counts[bucket] += 1

            self._bucket_counts[float('inf')] += 1

    def get_value(self) -> MetricValue:
        """Get current histogram value."""
        with self._lock:
            # Calculate approximate percentile
            return MetricValue(
                name=self.name,
                value=self._sum / self._count if self._count > 0 else 0,
                timestamp=datetime.utcnow(),
                labels=self.labels,
                metric_type=MetricType.HISTOGRAM,
            )

    def reset(self):
        """Reset histogram."""
        with self._lock:
            self._bucket_counts = {b: 0 for b in self.buckets}
            self._bucket_counts[float('inf')] = 0
            self._count = 0
            self._sum = 0.0

    def get_percentile(self, percentile: float) -> float:
        """Get approximate percentile value."""
        # Simplified percentile calculation
        with self._lock:
            if self._count == 0:
                return 0.0

            target = self._count * percentile
            cumulative = 0

            for bucket in sorted(self.buckets):
                cumulative += self._bucket_counts[bucket]
                if cumulative >= target:
                    return bucket

            return float('inf')


class Summary(Metric):
    """A summary metric with count, sum, and quantiles."""

    def __init__(
        self,
        name: str,
        description: str,
        quantiles: List[float] = None,
        labels: Optional[Dict[str, str]] = None,
    ):
        super().__init__(name, description, labels)
        self.quantiles = quantiles or [0.5, 0.9, 0.95, 0.99]
        self._values = []
        self._count = 0
        self._sum = 0.0
        self._lock = threading.Lock()
        self._max_values = 1000  # Keep last 1000 values for quantile calculation

    def observe(self, value: float):
        """Observe a value."""
        with self._lock:
            self._values.append(value)
            if len(self._values) > self._max_values:
                self._values.pop(0)
            self._count += 1
            self._sum += value

    def get_value(self) -> MetricValue:
        """Get current summary value."""
        with self._lock:
            return MetricValue(
                name=self.name,
                value=self._sum / self._count if self._count > 0 else 0,
                timestamp=datetime.utcnow(),
                labels=self.labels,
                metric_type=MetricType.SUMMARY,
            )

    def reset(self):
        """Reset summary."""
        with self._lock:
            self._values = []
            self._count = 0
            self._sum = 0.0

    def get_quantile(self, quantile: float) -> float:
        """Get quantile value."""
        with self._lock:
            if not self._values:
                return 0.0

            sorted_values = sorted(self._values)
            index = int(quantile * len(sorted_values))
            return sorted_values[min(index, len(sorted_values) - 1)]


class MetricCollector:
    """
    Central metrics collector for PM4Py.

    Tracks system and process mining metrics.
    """

    def __init__(self):
        self._metrics: Dict[str, Metric] = {}
        self._lock = threading.Lock()

        # Initialize default system metrics
        self._init_system_metrics()

        # Initialize default process metrics
        self._init_process_metrics()

    def _init_system_metrics(self):
        """Initialize system health metrics."""
        self.register(Counter(
            name="pm4py_discovery_total",
            description="Total number of process discoveries",
        ))

        self.register(Gauge(
            name="pm4py_active_discoveries",
            description="Currently active process discoveries",
        ))

        self.register(Histogram(
            name="pm4py_discovery_duration_seconds",
            description="Process discovery duration in seconds",
        ))

        self.register(Counter(
            name="pm4py_errors_total",
            description="Total number of errors",
        ))

        self.register(Gauge(
            name="pm4py_memory_usage_bytes",
            description="Current memory usage in bytes",
        ))

    def _init_process_metrics(self):
        """Initialize process mining specific metrics."""
        self.register(Counter(
            name="pm4py_events_processed_total",
            description="Total number of events processed",
        ))

        self.register(Gauge(
            name="pm4py_log_size_events",
            description="Current event log size in events",
        ))

        self.register(Histogram(
            name="pm4py_conformance_check_duration_seconds",
            description="Conformance check duration in seconds",
        ))

        self.register(Gauge(
            name="pm4py_fitness_score",
            description="Current fitness score",
        ))

        self.register(Gauge(
            name="pm4py_precision_score",
            description="Current precision score",
        ))

        self.register(Counter(
            name="pm4py_drift_detected_total",
            description="Total number of drift detections",
        ))

    def register(self, metric: Metric) -> None:
        """Register a metric."""
        with self._lock:
            self._metrics[metric.name] = metric

    def get(self, name: str) -> Optional[Metric]:
        """Get a metric by name."""
        return self._metrics.get(name)

    def counter(self, name: str, **kwargs) -> Counter:
        """Get or create a counter."""
        metric = self.get(name)
        if metric is None:
            metric = Counter(name, name, **kwargs)
            self.register(metric)
        elif not isinstance(metric, Counter):
            raise ValueError(f"Metric {name} is not a Counter")
        return metric

    def gauge(self, name: str, **kwargs) -> Gauge:
        """Get or create a gauge."""
        metric = self.get(name)
        if metric is None:
            metric = Gauge(name, name, **kwargs)
            self.register(metric)
        elif not isinstance(metric, Gauge):
            raise ValueError(f"Metric {name} is not a Gauge")
        return metric

    def histogram(self, name: str, **kwargs) -> Histogram:
        """Get or create a histogram."""
        metric = self.get(name)
        if metric is None:
            metric = Histogram(name, name, **kwargs)
            self.register(metric)
        elif not isinstance(metric, Histogram):
            raise ValueError(f"Metric {name} is not a Histogram")
        return metric

    def summary(self, name: str, **kwargs) -> Summary:
        """Get or create a summary."""
        metric = self.get(name)
        if metric is None:
            metric = Summary(name, name, **kwargs)
            self.register(metric)
        elif not isinstance(metric, Summary):
            raise ValueError(f"Metric {name} is not a Summary")
        return metric

    def get_all_metrics(self) -> List[MetricValue]:
        """Get values for all metrics."""
        with self._lock:
            return [metric.get_value() for metric in self._metrics.values()]

    def reset_all(self):
        """Reset all metrics."""
        with self._lock:
            for metric in self._metrics.values():
                metric.reset()

    def to_prometheus_format(self) -> str:
        """Export metrics in Prometheus text format."""
        lines = []

        for metric in self._metrics.values():
            value = metric.get_value()

            # HELP line
            lines.append(f"# HELP {value.name} {metric.description}")

            # TYPE line
            lines.append(f"# TYPE {value.name} {value.metric_type.value}")

            # Metric line
            label_str = ""
            if value.labels:
                label_pairs = [f'{k}="{v}"' for k, v in value.labels.items()]
                label_str = "{" + ",".join(label_pairs) + "}"

            lines.append(f"{value.name}{label_str} {value.value} {int(value.timestamp.timestamp())}")

        return "\n".join(lines)


# Process-specific metric classes
@dataclass
class ProcessMetric:
    """A process mining specific metric."""
    log_id: str
    discovery_algorithm: str
    event_count: int
    case_count: int
    activity_count: int
    fitness: Optional[float] = None
    precision: Optional[float] = None
    f_measure: Optional[float] = None
    discovery_time_seconds: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        from dataclasses import asdict
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class SystemMetric:
    """A system health metric."""
    cpu_percent: float
    memory_usage_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    active_discoveries: int
    queued_jobs: int
    uptime_seconds: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        from dataclasses import asdict
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    @classmethod
    def collect(cls) -> "SystemMetric":
        """Collect current system metrics."""
        import psutil
        import time

        boot_time = psutil.boot_time()
        uptime = time.time() - boot_time

        return cls(
            cpu_percent=psutil.cpu_percent(interval=0.1),
            memory_usage_mb=psutil.virtual_memory().used / (1024 * 1024),
            memory_available_mb=psutil.virtual_memory().available / (1024 * 1024),
            disk_usage_percent=psutil.disk_usage('/').percent,
            active_discoveries=0,  # To be tracked by application
            queued_jobs=0,  # To be tracked by application
            uptime_seconds=uptime,
        )


__all__ = [
    'MetricType',
    'MetricValue',
    'HistogramBucket',
    'Metric',
    'Counter',
    'Gauge',
    'Histogram',
    'Summary',
    'MetricCollector',
    'ProcessMetric',
    'SystemMetric',
]
