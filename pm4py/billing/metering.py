"""
PM4Py SaaS Usage Metering

Tracks resource usage for billing and limit enforcement.
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import time
import threading
from collections import defaultdict


class MetricType(Enum):
    """Types of usage metrics."""
    EVENTS_PROCESSED = "events_processed"
    PROCESS_MODELS = "process_models"
    AI_REQUESTS = "ai_requests"
    API_CALLS = "api_calls"
    STORAGE_BYTES = "storage_bytes"
    WEBHOOK_CALLS = "webhook_calls"
    CONFORMANCE_CHECKS = "conformance_checks"


@dataclass
class MetricRecord:
    """A single usage metric record."""
    metric_type: MetricType
    value: float
    tenant_id: str
    timestamp: datetime
    resource_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class UsageMeter:
    """
    Thread-safe usage meter for tracking resource consumption.

    Records metrics in memory and persists to storage periodically.
    """

    def __init__(self, flush_interval_seconds: int = 60):
        """
        Initialize the usage meter.

        Args:
            flush_interval_seconds: How often to flush metrics to storage
        """
        self._metrics: Dict[str, List[MetricRecord]] = defaultdict(list)
        self._counters: Dict[str, Dict[MetricType, float]] = defaultdict(
            lambda: defaultdict(float)
        )
        self._lock = threading.Lock()
        self._flush_interval = flush_interval_seconds
        self._last_flush = datetime.utcnow()

        # Callbacks for limit enforcement
        self._limit_callbacks: List[Callable[[str, MetricType, float], None]] = []

    def record(
        self,
        metric_type: MetricType,
        value: float,
        tenant_id: str,
        resource_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record a usage metric.

        Args:
            metric_type: Type of metric being recorded
            value: Value to add (can be negative for corrections)
            tenant_id: Tenant identifier
            resource_id: Optional resource identifier
            metadata: Optional metadata about the usage
        """
        with self._lock:
            record = MetricRecord(
                metric_type=metric_type,
                value=value,
                tenant_id=tenant_id,
                timestamp=datetime.utcnow(),
                resource_id=resource_id,
                metadata=metadata or {},
            )
            self._metrics[tenant_id].append(record)
            self._counters[tenant_id][metric_type] += value

            # Check if any limits are exceeded
            self._check_limits(tenant_id, metric_type, self._counters[tenant_id][metric_type])

            # Auto-flush if needed
            if (datetime.utcnow() - self._last_flush).total_seconds() >= self._flush_interval:
                self._flush_metrics()

    def increment(
        self,
        metric_type: MetricType,
        tenant_id: str,
        delta: float = 1.0,
        **kwargs,
    ) -> None:
        """Increment a counter by delta."""
        self.record(metric_type, delta, tenant_id, **kwargs)

    def get_usage(
        self,
        tenant_id: str,
        metric_type: Optional[MetricType] = None,
        since: Optional[datetime] = None,
    ) -> Dict[str, float]:
        """
        Get usage statistics for a tenant.

        Args:
            tenant_id: Tenant identifier
            metric_type: Specific metric type, or None for all
            since: Only include records since this time

        Returns:
            Dictionary of metric types to total values
        """
        with self._lock:
            if metric_type:
                return {metric_type.value: self._counters[tenant_id][metric_type]}

            result = {}
            for mt, value in self._counters[tenant_id].items():
                result[mt.value] = value
            return result

    def get_usage_records(
        self,
        tenant_id: str,
        since: Optional[datetime] = None,
    ) -> List[MetricRecord]:
        """
        Get raw usage records for a tenant.

        Args:
            tenant_id: Tenant identifier
            since: Only include records since this time

        Returns:
            List of metric records
        """
        with self._lock:
            records = self._metrics.get(tenant_id, [])
            if since:
                records = [r for r in records if r.timestamp >= since]
            return records

    def reset_period(self, tenant_id: str) -> None:
        """Reset counters for a new billing period."""
        with self._lock:
            self._counters[tenant_id] = defaultdict(float)
            # Keep historical records but mark new period
            # In production, this would archive old records

    def add_limit_callback(
        self,
        callback: Callable[[str, MetricType, float], None],
    ) -> None:
        """
        Add a callback to be invoked when a limit is approached.

        Callback signature: (tenant_id, metric_type, current_value)
        """
        self._limit_callbacks.append(callback)

    def _check_limits(
        self,
        tenant_id: str,
        metric_type: MetricType,
        current_value: float,
    ) -> None:
        """Check if limits are exceeded and invoke callbacks."""
        for callback in self._limit_callbacks:
            try:
                callback(tenant_id, metric_type, current_value)
            except Exception as e:
                # Log error but don't interrupt metering
                print(f"Limit callback error: {e}")

    def _flush_metrics(self) -> None:
        """Flush metrics to persistent storage."""
        # In production, this would write to database
        self._last_flush = datetime.utcnow()

    def get_tenant_summary(
        self,
        tenant_id: str,
    ) -> Dict[str, Any]:
        """
        Get a summary of usage for a tenant.

        Returns:
            Dictionary with usage statistics and formatted info
        """
        with self._lock:
            usage = self._counters.get(tenant_id, defaultdict(float))

            # Convert bytes to GB
            storage_gb = usage.get(MetricType.STORAGE_BYTES, 0) / (1024**3)

            return {
                'tenant_id': tenant_id,
                'events_processed': int(usage.get(MetricType.EVENTS_PROCESSED, 0)),
                'process_models': int(usage.get(MetricType.PROCESS_MODELS, 0)),
                'ai_requests': int(usage.get(MetricType.AI_REQUESTS, 0)),
                'api_calls': int(usage.get(MetricType.API_CALLS, 0)),
                'webhook_calls': int(usage.get(MetricType.WEBHOOK_CALLS, 0)),
                'conformance_checks': int(usage.get(MetricType.CONFORMANCE_CHECKS, 0)),
                'storage_gb': round(storage_gb, 2),
                'last_updated': datetime.utcnow().isoformat(),
            }


# Global usage meter instance
_global_meter: Optional[UsageMeter] = None
_meter_lock = threading.Lock()


def get_usage_meter() -> UsageMeter:
    """Get the global usage meter instance."""
    global _global_meter
    with _meter_lock:
        if _global_meter is None:
            _global_meter = UsageMeter()
        return _global_meter


# Convenience decorators for metering
def meter_event_processing(metric_type: MetricType = MetricType.EVENTS_PROCESSED):
    """Decorator to meter event processing operations."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            meter = get_usage_meter()
            tenant_id = kwargs.get('tenant_id', 'default')

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time

                # Count events processed (estimate from result)
                event_count = _extract_event_count(result)
                meter.record(metric_type, event_count, tenant_id)

                return result
            except Exception as e:
                # Still record the attempt
                meter.increment(MetricType.API_CALLS, tenant_id)
                raise

        return wrapper
    return decorator


def meter_api_call(func):
    """Decorator to meter API calls."""
    def wrapper(*args, **kwargs):
        meter = get_usage_meter()
        tenant_id = kwargs.get('tenant_id', 'default')

        meter.increment(MetricType.API_CALLS, tenant_id)
        return func(*args, **kwargs)
    return wrapper


def meter_ai_request(func):
    """Decorator to meter AI process design requests."""
    def wrapper(*args, **kwargs):
        meter = get_usage_meter()
        tenant_id = kwargs.get('tenant_id', 'default')

        meter.increment(MetricType.AI_REQUESTS, tenant_id)
        return func(*args, **kwargs)
    return wrapper


def _extract_event_count(result: Any) -> int:
    """Extract event count from function result."""
    if isinstance(result, int):
        return result
    if hasattr(result, '__len__'):
        return len(result)
    return 1


__all__ = [
    'MetricType',
    'MetricRecord',
    'UsageMeter',
    'get_usage_meter',
    'meter_event_processing',
    'meter_api_call',
    'meter_ai_request',
]
