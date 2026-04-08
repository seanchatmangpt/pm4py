'''
PM4Py – Manufacturing OPC-UA Adapter
Copyright (C) 2026 Process Intelligence Solutions GmbH

OPC-UA client for IIoT equipment data ingestion and event log generation.
'''

from typing import Dict, List, Any, Optional, Union, Callable
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import threading
import time

logger = logging.getLogger(__name__)


class OPCUAConnectionStatus(Enum):
    """OPC-UA connection status."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


class OPCUASecurityPolicy(Enum):
    """OPC-UA security policies."""
    NONE = "None"
    BASIC128RSA15 = "Basic128Rsa15"
    BASIC256 = "Basic256"
    BASIC256SHA256 = "Basic256Sha256"


@dataclass
class OPCUANodeConfig:
    """OPC-UA node configuration for a sensor or data point."""
    node_id: str
    display_name: str
    data_type: str = "float"  # float, int, bool, string
    unit: Optional[str] = None
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None
    sampling_interval_ms: int = 1000
    deadband: float = 0.0


@dataclass
class OEEConfig:
    """OEE calculation configuration for equipment."""
    equipment_id: str
    ideal_cycle_time_seconds: float
    planned_production_time_minutes: float = 480.0  # 8 hours default

    # Node IDs for OEE calculation
    run_time_node: Optional[str] = None
    downtime_node: Optional[str] = None
    total_pieces_node: Optional[str] = None
    good_pieces_node: Optional[str] = None
    status_node: Optional[str] = None


class OPCUASensorReading:
    """Represents a single sensor reading from OPC-UA."""

    def __init__(
        self,
        sensor_id: str,
        sensor_type: str,
        value: float,
        unit: str,
        timestamp: datetime,
        equipment_id: str,
        alarm_active: bool = False,
    ):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.value = value
        self.unit = unit
        self.timestamp = timestamp
        self.equipment_id = equipment_id
        self.alarm_active = alarm_active

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "iot:sensor_id": self.sensor_id,
            "iot:sensor_type": self.sensor_type,
            "iot:sensor_value": self.value,
            "iot:sensor_unit": self.unit,
            "time:timestamp": self.timestamp,
            "equipment:id": self.equipment_id,
            "iot:alarm_active": self.alarm_active,
        }

    def to_event_row(self) -> Dict[str, Any]:
        """Convert to event log row format."""
        return {
            "concept:name": f"sensor_reading_{self.sensor_type}",
            "time:timestamp": self.timestamp,
            "case:concept:name": f"SENSOR_{self.sensor_id}",
            "equipment:id": self.equipment_id,
            "iot:sensor_id": self.sensor_id,
            "iot:sensor_type": self.sensor_type,
            "iot:sensor_value": self.value,
            "iot:sensor_unit": self.unit,
            "iot:alarm_active": self.alarm_active,
            "lifecycle:transition": "complete",
        }


class OPCUAAdapter:
    """
    OPC-UA adapter for IIoT equipment data ingestion.

    Features:
    - Connect to OPC-UA servers
    - Browse and subscribe to nodes
    - Real-time data streaming
    - OEE calculation from equipment data
    - Event log generation
    - Buffered data collection for offline analysis

    Example:
        >>> adapter = OPCUAAdapter("opc.tcp://plc1.company.com:4840")
        >>> adapter.connect()
        >>>
        >>> # Define nodes to monitor
        >>> nodes = [
        ...     OPCUANodeConfig("ns=2;s=Temperature", "Temperature", "float", "°C"),
        ...     OPCUANodeConfig("ns=2;s=Pressure", "Pressure", "float", "bar"),
        ... ]
        >>>
        >>> # Collect data
        >>> log = adapter.collect_data(duration_seconds=60, nodes=nodes)
        >>>
        >>> adapter.disconnect()
    """

    def __init__(
        self,
        endpoint_url: str,
        security_policy: OPCUASecurityPolicy = OPCUASecurityPolicy.NONE,
        timeout_ms: int = 5000,
        retry_interval_ms: int = 5000,
        max_retries: int = 3,
    ):
        """
        Initialize OPC-UA adapter.

        :param endpoint_url: OPC-UA server endpoint URL
        :param security_policy: Security policy to use
        :param timeout_ms: Connection timeout in milliseconds
        :param retry_interval_ms: Retry interval for reconnection
        :param max_retries: Maximum connection retry attempts
        """
        self.endpoint_url = endpoint_url
        self.security_policy = security_policy
        self.timeout_ms = timeout_ms
        self.retry_interval_ms = retry_interval_ms
        self.max_retries = max_retries

        self._client = None
        self._status = OPCUAConnectionStatus.DISCONNECTED
        self._subscriptions = []
        self._buffer: List[Dict[str, Any]] = []
        self._buffer_lock = threading.Lock()
        self._monitoring = False
        self._monitor_thread = None

        # Equipment and node configurations
        self._equipment_configs: Dict[str, OEEConfig] = {}
        self._node_configs: List[OPCUANodeConfig] = []

    @property
    def status(self) -> OPCUAConnectionStatus:
        """Get current connection status."""
        return self._status

    @property
    def is_connected(self) -> bool:
        """Check if connected to OPC-UA server."""
        return self._status == OPCUAConnectionStatus.CONNECTED

    def connect(self) -> bool:
        """
        Connect to OPC-UA server.

        :return: True if connection successful
        """
        self._status = OPCUAConnectionStatus.CONNECTING

        try:
            # Try to import opcua library
            try:
                from opcua import Client
            except ImportError:
                logger.warning(
                    "OPC-UA library not installed. "
                    "Install with: pip install opcua"
                )
                # Create mock client for testing/demo
                self._client = _MockOPCUAClient(self.endpoint_url)
            else:
                self._client = Client(
                    self.endpoint_url,
                    timeout=self.timeout_ms / 1000,
                )

            # Attempt connection
            self._client.connect()

            self._status = OPCUAConnectionStatus.CONNECTED
            logger.info(f"Connected to OPC-UA server: {self.endpoint_url}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to OPC-UA server: {e}")
            self._status = OPCUAConnectionStatus.ERROR
            return False

    def disconnect(self):
        """Disconnect from OPC-UA server."""
        self._monitoring = False

        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
            self._monitor_thread = None

        if self._client:
            try:
                if hasattr(self._client, 'disconnect'):
                    self._client.disconnect()
            except Exception as e:
                logger.warning(f"Error during disconnect: {e}")

        self._status = OPCUAConnectionStatus.DISCONNECTED
        logger.info("Disconnected from OPC-UA server")

    def browse_nodes(
        self,
        parent_node_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Browse OPC-UA nodes.

        :param parent_node_id: Parent node ID (None for root)
        :return: List of node information dictionaries
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to OPC-UA server")

        nodes = []

        try:
            if hasattr(self._client, 'get_root_node'):
                root = self._client.get_root_node() if parent_node_id is None else \
                       self._client.get_node(parent_node_id)

                if hasattr(root, 'get_children'):
                    for child in root.get_children():
                        nodes.append({
                            "node_id": child.nodeid.to_string(),
                            "browse_name": str(child.get_browse_name()),
                            "display_name": str(child.get_display_name()).text,
                            "node_class": str(child.get_node_class()),
                        })

        except Exception as e:
            logger.error(f"Error browsing nodes: {e}")

        return nodes

    def add_equipment_config(self, config: OEEConfig):
        """
        Add OEE configuration for equipment.

        :param config: Equipment OEE configuration
        """
        self._equipment_configs[config.equipment_id] = config

    def add_node_config(self, config: OPCUANodeConfig):
        """
        Add sensor node configuration.

        :param config: Node configuration
        """
        self._node_configs.append(config)

    def read_node_value(
        self,
        node_id: str,
        data_type: str = "float",
    ) -> Any:
        """
        Read current value from a node.

        :param node_id: OPC-UA node ID
        :param data_type: Expected data type
        :return: Node value
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to OPC-UA server")

        try:
            if hasattr(self._client, 'get_node'):
                node = self._client.get_node(node_id)
                value = node.get_value()

                # Type conversion
                if data_type == "float" and value is not None:
                    value = float(value)
                elif data_type == "int" and value is not None:
                    value = int(value)
                elif data_type == "bool" and value is not None:
                    value = bool(value)

                return value

        except Exception as e:
            logger.error(f"Error reading node {node_id}: {e}")

        return None

    def collect_data(
        self,
        duration_seconds: int = 60,
        sampling_interval_ms: int = 1000,
        nodes: Optional[List[OPCUANodeConfig]] = None,
        equipment_id: str = "EQUIPMENT-001",
    ) -> pd.DataFrame:
        """
        Collect data from OPC-UA nodes.

        :param duration_seconds: Collection duration
        :param sampling_interval_ms: Sampling interval in milliseconds
        :param nodes: List of node configurations (uses configured nodes if None)
        :param equipment_id: Equipment identifier
        :return: Event log DataFrame with sensor readings
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to OPC-UA server")

        nodes_to_monitor = nodes or self._node_configs

        if not nodes_to_monitor:
            raise ValueError("No nodes configured for monitoring")

        events = []
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=duration_seconds)

        logger.info(
            f"Collecting data from {len(nodes_to_monitor)} nodes "
            f"for {duration_seconds} seconds"
        )

        while datetime.now() < end_time:
            timestamp = datetime.now()

            for node_config in nodes_to_monitor:
                try:
                    value = self.read_node_value(
                        node_config.node_id,
                        node_config.data_type
                    )

                    if value is not None:
                        # Check thresholds
                        alarm_active = False
                        if node_config.threshold_min is not None and value < node_config.threshold_min:
                            alarm_active = True
                        if node_config.threshold_max is not None and value > node_config.threshold_max:
                            alarm_active = True

                        # Determine sensor type from node name
                        sensor_type = self._infer_sensor_type(node_config.display_name)

                        events.append({
                            "case:concept:name": f"SENSOR_{node_config.node_id}",
                            "concept:name": f"sensor_reading_{sensor_type}",
                            "time:timestamp": timestamp,
                            "lifecycle:transition": "complete",
                            "equipment:id": equipment_id,
                            "iot:sensor_id": node_config.node_id,
                            "iot:sensor_type": sensor_type,
                            "iot:sensor_value": value,
                            "iot:sensor_unit": node_config.unit or "",
                            "iot:alarm_active": alarm_active,
                            "iot:threshold_min": node_config.threshold_min,
                            "iot:threshold_max": node_config.threshold_max,
                        })

                except Exception as e:
                    logger.warning(f"Error reading {node_config.node_id}: {e}")

            # Wait for next sample
            time.sleep(sampling_interval_ms / 1000.0)

        df = pd.DataFrame(events)

        if not df.empty:
            df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])

        logger.info(f"Collected {len(events)} sensor readings")
        return df

    def calculate_oee_from_nodes(
        self,
        equipment_id: str,
    ) -> Dict[str, float]:
        """
        Calculate OEE from configured equipment nodes.

        :param equipment_id: Equipment identifier
        :return: OEE metrics dictionary
        """
        if equipment_id not in self._equipment_configs:
            raise ValueError(f"No OEE configuration for equipment: {equipment_id}")

        config = self._equipment_configs[equipment_id]

        # Read values from nodes (or use defaults if nodes not configured)
        if config.run_time_node:
            run_time = self.read_node_value(config.run_time_node, "float") or 0
        else:
            run_time = config.planned_production_time_minutes * 0.85

        if config.downtime_node:
            downtime = self.read_node_value(config.downtime_node, "float") or 0
        else:
            downtime = config.planned_production_time_minutes * 0.15

        if config.total_pieces_node:
            total_pieces = self.read_node_value(config.total_pieces_node, "int") or 100
        else:
            total_pieces = 100

        if config.good_pieces_node:
            good_pieces = self.read_node_value(config.good_pieces_node, "int") or 95
        else:
            good_pieces = int(total_pieces * 0.95)

        # Calculate OEE
        from pm4py.verticals.manufacturing.schemas import calculate_oee

        oee_metrics = calculate_oee(
            run_time=run_time,
            planned_production_time=config.planned_production_time_minutes,
            total_pieces=total_pieces,
            good_pieces=good_pieces,
            ideal_cycle_time=config.ideal_cycle_time_seconds,
        )

        # Add equipment ID
        oee_metrics["equipment_id"] = equipment_id

        return oee_metrics

    def start_monitoring(
        self,
        callback: Optional[Callable[[List[Dict]], None]] = None,
        buffer_size: int = 10000,
    ):
        """
        Start real-time monitoring with callback.

        :param callback: Function to call with new data batches
        :param buffer_size: Maximum buffer size before forcing callback
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to OPC-UA server")

        self._monitoring = True

        def monitor_loop():
            while self._monitoring:
                try:
                    # Collect readings from all configured nodes
                    readings = []

                    for node_config in self._node_configs:
                        try:
                            value = self.read_node_value(
                                node_config.node_id,
                                node_config.data_type
                            )

                            if value is not None:
                                alarm_active = False
                                if node_config.threshold_min is not None and value < node_config.threshold_min:
                                    alarm_active = True
                                if node_config.threshold_max is not None and value > node_config.threshold_max:
                                    alarm_active = True

                                reading = {
                                    "iot:sensor_id": node_config.node_id,
                                    "iot:sensor_type": self._infer_sensor_type(node_config.display_name),
                                    "iot:sensor_value": value,
                                    "iot:sensor_unit": node_config.unit or "",
                                    "iot:alarm_active": alarm_active,
                                    "time:timestamp": datetime.now(),
                                }
                                readings.append(reading)

                        except Exception as e:
                            logger.warning(f"Error in monitor loop for {node_config.node_id}: {e}")

                    if readings:
                        with self._buffer_lock:
                            self._buffer.extend(readings)

                            if callback and (len(self._buffer) >= buffer_size):
                                callback(self._buffer.copy())
                                self._buffer.clear()

                except Exception as e:
                    logger.error(f"Error in monitor loop: {e}")

                time.sleep(1)  # Monitor loop interval

        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()

        logger.info("Started OPC-UA monitoring")

    def stop_monitoring(self):
        """Stop real-time monitoring."""
        self._monitoring = False

        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
            self._monitor_thread = None

        logger.info("Stopped OPC-UA monitoring")

    def get_buffered_data(self) -> List[Dict[str, Any]]:
        """
        Get buffered sensor readings.

        :return: List of buffered readings
        """
        with self._buffer_lock:
            data = self._buffer.copy()
            self._buffer.clear()
            return data

    def generate_production_events(
        self,
        order_id: str,
        product_id: str,
        equipment_id: str,
        quantity: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Generate production workflow events from current equipment state.

        :param order_id: Production order ID
        :param product_id: Product ID
        :param equipment_id: Equipment ID
        :param quantity: Production quantity
        :return: List of event dictionaries
        """
        events = []
        timestamp = datetime.now()

        # Get current equipment status
        status = "running"
        if equipment_id in self._equipment_configs:
            config = self._equipment_configs[equipment_id]
            if config.status_node:
                status_value = self.read_node_value(config.status_node, "string")
                if status_value:
                    status = status_value.lower()

        # Calculate OEE for this production
        oee_metrics = {"availability": 85.0, "performance": 90.0, "quality": 95.0, "oee": 72.7}

        try:
            oee_metrics = self.calculate_oee_from_nodes(equipment_id)
        except Exception:
            pass  # Use defaults

        # Generate production events
        events.append({
            "case:concept:name": order_id,
            "concept:name": "production_start",
            "time:timestamp": timestamp,
            "lifecycle:transition": "complete",
            "production:order_id": order_id,
            "production:product_id": product_id,
            "production:quantity": quantity,
            "equipment:id": equipment_id,
            "equipment:status": status,
            "oee:availability": oee_metrics["availability"],
            "oee:performance": oee_metrics["performance"],
            "oee:quality": oee_metrics["quality"],
            "oee:oee": oee_metrics["oee"],
        })

        return events

    def _infer_sensor_type(self, display_name: str) -> str:
        """Infer sensor type from display name."""
        name_lower = display_name.lower()

        if "temp" in name_lower:
            return "temperature"
        elif "vibr" in name_lower or "accel" in name_lower:
            return "vibration"
        elif "press" in name_lower:
            return "pressure"
        elif "current" in name_lower or "amp" in name_lower:
            return "current"
        elif "volt" in name_lower:
            return "voltage"
        elif "humid" in name_lower:
            return "humidity"
        elif "flow" in name_lower:
            return "flow_rate"
        elif "prox" in name_lower or "pos" in name_lower:
            return "proximity"
        else:
            return "temperature"  # Default


class _MockOPCUAClient:
    """Mock OPC-UA client for testing/demo when library is not installed."""

    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url
        self._connected = False

        # Simulated sensor values
        self._sensor_values = {
            "temperature": 45.0 + np.random.uniform(-5, 40),
            "pressure": 5.0 + np.random.uniform(-2, 90),
            "vibration": 2.0 + np.random.uniform(-1, 6),
            "current": 15.0 + np.random.uniform(-5, 25),
        }

    def connect(self):
        """Mock connect."""
        self._connected = True

    def disconnect(self):
        """Mock disconnect."""
        self._connected = False

    def get_root_node(self):
        """Mock root node."""
        return _MockOPCUANode("Root", {})

    def get_node(self, node_id: str):
        """Mock node getter."""
        # Simulate values based on node ID
        value = 50.0
        if "temp" in node_id.lower():
            value = self._sensor_values["temperature"]
        elif "press" in node_id.lower():
            value = self._sensor_values["pressure"]
        elif "vibr" in node_id.lower():
            value = self._sensor_values["vibration"]
        elif "current" in node_id.lower():
            value = self._sensor_values["current"]

        return _MockOPCUANode(node_id, {"value": value})


class _MockOPCUANode:
    """Mock OPC-UA node."""

    def __init__(self, node_id: str, attrs: Dict[str, Any]):
        self.nodeid = _MockNodeId(node_id)
        self._attrs = attrs

    def get_value(self):
        """Get node value."""
        return self._attrs.get("value", 50.0)

    def get_children(self):
        """Get child nodes."""
        return []

    def get_browse_name(self):
        """Get browse name."""
        return _MockQualifiedName("Node")

    def get_display_name(self):
        """Get display name."""
        return _MockLocalizedText("Node Name")

    def get_node_class(self):
        """Get node class."""
        return "Variable"


class _MockNodeId:
    """Mock node ID."""

    def __init__(self, identifier: str):
        self.identifier = identifier

    def to_string(self):
        """Convert to string."""
        return f"ns=2;s={self.identifier}"


class _MockQualifiedName:
    """Mock qualified name."""

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name


class _MockLocalizedText:
    """Mock localized text."""

    def __init__(self, text: str):
        self.text = text


def discover_opcua_servers(
    host: str,
    port: int = 4840,
    timeout_ms: int = 5000,
) -> List[str]:
    """
    Discover OPC-UA servers on a host.

    :param host: Host address
    :param port: Starting port
    :param timeout_ms: Discovery timeout
    :return: List of discovered server endpoints
    """
    servers = []

    # Try common OPC-UA ports
    common_ports = [4840, 4841, 4842, 4855, 4856]

    for p in common_ports:
        endpoint = f"opc.tcp://{host}:{p}"

        try:
            # Try to connect
            adapter = OPCUAAdapter(endpoint, timeout_ms=timeout_ms)

            if adapter.connect():
                servers.append(endpoint)
                adapter.disconnect()

        except Exception:
            pass

    return servers


def create_event_log_from_opcua(
    readings: List[Dict[str, Any]],
    equipment_id: str = "EQUIPMENT-001",
) -> pd.DataFrame:
    """
    Convert OPC-UA sensor readings to event log format.

    :param readings: List of sensor reading dictionaries
    :param equipment_id: Equipment identifier
    :return: Event log DataFrame
    """
    events = []

    for i, reading in enumerate(readings):
        events.append({
            "case:concept:name": f"SENSOR_BATCH_{i // 100:06d}",
            "concept:name": f"sensor_reading_{reading.get('iot:sensor_type', 'temperature')}",
            "time:timestamp": reading.get("time:timestamp", datetime.now()),
            "lifecycle:transition": "complete",
            "equipment:id": equipment_id,
            "iot:sensor_id": reading.get("iot:sensor_id", ""),
            "iot:sensor_type": reading.get("iot:sensor_type", "temperature"),
            "iot:sensor_value": reading.get("iot:sensor_value", 0),
            "iot:sensor_unit": reading.get("iot:sensor_unit", ""),
            "iot:alarm_active": reading.get("iot:alarm_active", False),
        })

    df = pd.DataFrame(events)

    if not df.empty:
        df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])

    return df


__all__ = [
    'OPCUAAdapter',
    'OPCUANodeConfig',
    'OEEConfig',
    'OPCUASensorReading',
    'OPC UAConnectionStatus',
    'OPCUASecurityPolicy',
    'discover_opcua_servers',
    'create_event_log_from_opcua',
]
