'''
PM4Py – Manufacturing Schemas
Copyright (C) 2026 Process Intelligence Solutions GmbH

OEE calculation, IIoT sensor data, and equipment event schemas.
'''

from typing import Dict, List, Any, Set
from dataclasses import dataclass, field
from enum import Enum


class EquipmentType(Enum):
    """Manufacturing equipment types."""
    CNC_MACHINE = "CNC Machine"
    PRESS = "Hydraulic Press"
    ROBOT = "Industrial Robot"
    CONVEYOR = "Conveyor System"
    PRINTER_3D = "3D Printer"
    LASER_CUTTER = "Laser Cutter"
    WELDING_ROBOT = "Welding Robot"
    ASSEMBLY_STATION = "Assembly Station"
    TESTING_STATION = "Testing Station"
    PACKAGING_LINE = "Packaging Line"


class ProductType(Enum):
    """Product categories."""
    ELECTRONICS = "Electronics"
    AUTOMOTIVE = "Automotive"
    AEROSPACE = "Aerospace"
    CONSUMER_GOODS = "Consumer Goods"
    PHARMACEUTICALS = "Pharmaceuticals"
    FOOD_BEVERAGE = "Food & Beverage"
    CHEMICALS = "Chemicals"
    TEXTILES = "Textiles"


class MaintenanceType(Enum):
    """Maintenance operation types."""
    PREVENTIVE = "Preventive Maintenance"
    CORRECTIVE = "Corrective Maintenance"
    PREDICTIVE = "Predictive Maintenance"
    EMERGENCY = "Emergency Repair"


class QualityIssue(Enum):
    """Quality defect types."""
    DIMENSIONAL = "Dimensional Defect"
    SURFACE_FINISH = "Surface Finish Issue"
    MATERIAL = "Material Defect"
    ASSEMBLY = "Assembly Error"
    FUNCTIONAL = "Functional Failure"
    COSMETIC = "Cosmetic Defect"


# OEE (Overall Equipment Effectiveness) Attributes
OEE_ATTRIBUTES = {
    "oee:availability": {
        "description": "Availability percentage (run time / planned production time)",
        "required": True,
        "data_type": "float",
        "unit": "percentage",
        "min_value": 0.0,
        "max_value": 100.0,
    },
    "oee:performance": {
        "description": "Performance percentage (ideal cycle time / actual cycle time)",
        "required": True,
        "data_type": "float",
        "unit": "percentage",
        "min_value": 0.0,
        "max_value": 100.0,
    },
    "oee:quality": {
        "description": "Quality percentage (good pieces / total pieces)",
        "required": True,
        "data_type": "float",
        "unit": "percentage",
        "min_value": 0.0,
        "max_value": 100.0,
    },
    "oee:oee": {
        "description": "Overall OEE (availability * performance * quality)",
        "required": True,
        "data_type": "float",
        "unit": "percentage",
        "min_value": 0.0,
        "max_value": 100.0,
    },
    "oee:run_time": {
        "description": "Actual production run time",
        "required": True,
        "data_type": "float",
        "unit": "minutes",
    },
    "oee:planned_production_time": {
        "description": "Planned available production time",
        "required": True,
        "data_type": "float",
        "unit": "minutes",
    },
    "oee:downtime": {
        "description": "Unplanned downtime duration",
        "required": True,
        "data_type": "float",
        "unit": "minutes",
    },
    "oee:total_pieces": {
        "description": "Total pieces produced (including defects)",
        "required": True,
        "data_type": "integer",
    },
    "oee:good_pieces": {
        "description": "Good pieces (quality passed)",
        "required": True,
        "data_type": "integer",
    },
    "oee:defective_pieces": {
        "description": "Defective pieces (quality failed)",
        "required": True,
        "data_type": "integer",
    },
    "oee:ideal_cycle_time": {
        "description": "Theoretical fastest cycle time per piece",
        "required": True,
        "data_type": "float",
        "unit": "seconds",
    },
}


# IIoT (Industrial IoT) Sensor Attributes
IIOT_SENSOR_ATTRIBUTES = {
    "iot:sensor_id": {
        "description": "Unique sensor identifier",
        "required": True,
        "data_type": "string",
    },
    "iot:sensor_type": {
        "description": "Type of sensor (temperature, vibration, pressure, etc.)",
        "required": True,
        "data_type": "string",
        "allowed_values": [
            "temperature",
            "vibration",
            "pressure",
            "humidity",
            "flow_rate",
            "current",
            "voltage",
            "proximity",
            "acceleration",
            "acoustic",
        ],
    },
    "iot:sensor_value": {
        "description": "Raw sensor reading value",
        "required": True,
        "data_type": "float",
    },
    "iot:sensor_unit": {
        "description": "Unit of measurement",
        "required": True,
        "data_type": "string",
        "allowed_values": ["°C", "°F", "Pa", "bar", "psi", "%", "A", "V", "Hz", "g", "m/s"],
    },
    "iot:threshold_min": {
        "description": "Minimum acceptable threshold",
        "required": False,
        "data_type": "float",
    },
    "iot:threshold_max": {
        "description": "Maximum acceptable threshold",
        "required": False,
        "data_type": "float",
    },
    "iot:alarm_active": {
        "description": "Whether sensor value triggered an alarm",
        "required": True,
        "data_type": "boolean",
    },
    "iot:sample_rate": {
        "description": "Sensor sampling rate",
        "required": False,
        "data_type": "float",
        "unit": "Hz",
    },
}


# Manufacturing Workflow Event Schema
MANUFACTURING_WORKFLOW_SCHEMA = {
    "event_level": {
        # Core XES attributes
        "concept:name": {
            "type": "string",
            "description": "Activity name",
            "required": True,
        },
        "time:timestamp": {
            "type": "datetime",
            "description": "Event timestamp",
            "required": True,
        },
        "lifecycle:transition": {
            "type": "string",
            "description": "Lifecycle state",
            "allowed_values": ["start", "complete", "suspend", "resume"],
            "default": "complete",
        },

        # Production identification
        "production:order_id": {
            "type": "string",
            "description": "Production order identifier",
            "required": True,
        },
        "production:batch_id": {
            "type": "string",
            "description": "Batch identifier",
        },
        "production:product_id": {
            "type": "string",
            "description": "Product identifier",
            "required": True,
        },
        "production:product_type": {
            "type": "string",
            "description": "Product category",
            "allowed_values": [t.value for t in ProductType],
        },
        "production:serial_number": {
            "type": "string",
            "description": "Unique serial number",
        },
        "production:quantity": {
            "type": "integer",
            "description": "Quantity processed",
        },
        "production:cycle_time": {
            "type": "float",
            "description": "Actual cycle time",
            "unit": "seconds",
        },

        # Equipment attributes
        "equipment:id": {
            "type": "string",
            "description": "Equipment identifier",
            "required": True,
        },
        "equipment:type": {
            "type": "string",
            "description": "Equipment type",
            "allowed_values": [t.value for t in EquipmentType],
        },
        "equipment:location": {
            "type": "string",
            "description": "Physical location (line, cell, zone)",
        },
        "equipment:status": {
            "type": "string",
            "description": "Current equipment status",
            "allowed_values": ["running", "idle", "maintenance", "breakdown", "setup"],
        },
        "equipment:operator": {
            "type": "string",
            "description": "Operator ID",
        },

        # Quality attributes
        "quality:status": {
            "type": "string",
            "description": "Quality inspection result",
            "allowed_values": ["pass", "fail", "rework", "scrap"],
        },
        "quality:defect_code": {
            "type": "string",
            "description": "Defect type code",
            "allowed_values": [t.value for t in QualityIssue],
        },
        "quality:defect_description": {
            "type": "string",
            "description": "Detailed defect description",
        },
        "quality:inspector": {
            "type": "string",
            "description": "Inspector ID",
        },

        # Maintenance attributes
        "maintenance:type": {
            "type": "string",
            "description": "Maintenance type",
            "allowed_values": [t.value for t in MaintenanceType],
        },
        "maintenance:duration": {
            "type": "float",
            "description": "Maintenance duration",
            "unit": "minutes",
        },
        "maintenance:technician": {
            "type": "string",
            "description": "Technician ID",
        },
        "maintenance:reason_code": {
            "type": "string",
            "description": "Failure/issue reason code",
        },

        # Case/Order identification
        "case:concept:name": {
            "type": "string",
            "description": "Production order/Case ID",
            "required": True,
        },
    },

    "trace_level": {
        "production:shift": {
            "type": "string",
            "description": "Production shift",
            "allowed_values": ["Day", "Evening", "Night"],
        },
        "production:work_order": {
            "type": "string",
            "description": "Work order number",
        },
        "production:priority": {
            "type": "string",
            "description": "Order priority",
            "allowed_values": ["urgent", "high", "normal", "low"],
        },
        "production:due_date": {
            "type": "datetime",
            "description": "Scheduled completion date",
        },
        "production:customer": {
            "type": "string",
            "description": "Customer identifier",
        },
        "production:route": {
            "type": "string",
            "description": "Production route ID",
        },
    },
}


# Standard Manufacturing Activities
MANUFACTURING_ACTIVITIES = {
    # Order processing
    "order_received": "Order Received from Customer",
    "order_review": "Order Review and Planning",
    "material_picking": "Material Picking from Warehouse",
    "material_preparation": "Material Preparation",

    # Production setup
    "equipment_setup": "Equipment Setup and Configuration",
    "tool_loading": "Tool Loading and Calibration",
    "program_loading": "CNC Program Loading",
    "first_piece_inspection": "First Piece Inspection",

    # Production execution
    "production_start": "Production Start",
    "machining": "Machining Operation",
    "assembly": "Assembly Operation",
    "welding": "Welding Operation",
    "painting": "Painting/Coating Operation",
    "testing": "Product Testing",
    "inspection": "Quality Inspection",
    "packaging": "Packaging Operation",

    # Quality control
    "quality_check": "Quality Control Check",
    "dimensional_inspection": "Dimensional Inspection",
    "surface_inspection": "Surface Finish Inspection",
    "functional_test": "Functional Testing",

    # Material handling
    "material_loading": "Material Loading to Equipment",
    "material_unloading": "Material Unloading from Equipment",
    "workpiece_transfer": "Workpiece Transfer between Stations",
    "finished_goods_storage": "Finished Goods to Storage",

    # Maintenance
    "preventive_maintenance": "Preventive Maintenance",
    "corrective_maintenance": "Corrective Maintenance",
    "emergency_repair": "Emergency Repair",
    "calibration": "Equipment Calibration",

    # Exceptions
    "production_pause": "Production Pause",
    "equipment_breakdown": "Equipment Breakdown",
    "quality_rejection": "Quality Rejection",
    "rework": "Rework Operation",
    "scrap": "Scrap Declaration",
    "order_completion": "Order Completion",
    "shipping": "Shipping to Customer",
}


@dataclass
class ManufacturingEvent:
    """Typed manufacturing event."""

    activity: str
    timestamp: Any
    case_id: str
    order_id: str
    product_id: str
    equipment_id: str
    quantity: int = 1
    cycle_time: float = 0.0
    quality_status: str = "pass"
    equipment_status: str = "running"
    operator: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "concept:name": self.activity,
            "time:timestamp": self.timestamp,
            "case:concept:name": self.case_id,
            "production:order_id": self.order_id,
            "production:product_id": self.product_id,
            "production:quantity": self.quantity,
            "production:cycle_time": self.cycle_time,
            "equipment:id": self.equipment_id,
            "equipment:status": self.equipment_status,
            "equipment:operator": self.operator,
            "quality:status": self.quality_status,
        }


# OEE Calculation Standards
OEE_CALCULATION_STANDARDS = {
    "availability": {
        "description": "Run Time / Planned Production Time",
        "formula": "Run Time = Planned Production Time - Downtime",
        "world_class": 90.0,  # World-class OEE availability
        "acceptable": 80.0,
    },
    "performance": {
        "description": "Ideal Cycle Time / Actual Cycle Time",
        "formula": "Performance = (Total Pieces * Ideal Cycle Time) / Run Time",
        "world_class": 95.0,  # World-class OEE performance
        "acceptable": 85.0,
    },
    "quality": {
        "description": "Good Pieces / Total Pieces",
        "formula": "Quality = Good Pieces / Total Pieces",
        "world_class": 99.9,  # World-class OEE quality
        "acceptable": 95.0,
    },
    "oee": {
        "description": "Overall Equipment Effectiveness",
        "formula": "OEE = Availability * Performance * Quality",
        "world_class": 85.0,  # World-class OEE
        "acceptable": 60.0,
    },
}


def calculate_oee(
    run_time: float,
    planned_production_time: float,
    total_pieces: int,
    good_pieces: int,
    ideal_cycle_time: float,
) -> Dict[str, float]:
    """
    Calculate OEE metrics.

    :param run_time: Actual production run time (minutes)
    :param planned_production_time: Planned available time (minutes)
    :param total_pieces: Total pieces produced
    :param good_pieces: Good pieces (passed quality)
    :param ideal_cycle_time: Ideal cycle time per piece (seconds)
    :return: Dictionary with availability, performance, quality, and OEE
    """
    # Availability = Run Time / Planned Production Time
    availability = (run_time / planned_production_time * 100) if planned_production_time > 0 else 0.0

    # Performance = (Total Pieces * Ideal Cycle Time) / (Run Time * 60)
    # Convert run_time from minutes to seconds
    run_time_seconds = run_time * 60
    performance = ((total_pieces * ideal_cycle_time) / run_time_seconds * 100) if run_time_seconds > 0 else 0.0

    # Quality = Good Pieces / Total Pieces
    quality = (good_pieces / total_pieces * 100) if total_pieces > 0 else 0.0

    # OEE = Availability * Performance * Quality / 10000
    oee = availability * performance * quality / 10000

    return {
        "availability": round(availability, 2),
        "performance": round(performance, 2),
        "quality": round(quality, 2),
        "oee": round(oee, 2),
    }


def validate_manufacturing_schema(event: Dict[str, Any]) -> List[str]:
    """Validate a manufacturing event against the schema."""
    errors = []
    event_level = MANUFACTURING_WORKFLOW_SCHEMA.get("event_level", {})

    for attr_name, attr_def in event_level.items():
        if attr_def.get("required", False) and attr_name not in event:
            errors.append(f"Missing required attribute: {attr_name}")

        if attr_name in event:
            allowed = attr_def.get("allowed_values")
            if allowed and event[attr_name] not in allowed:
                errors.append(
                    f"Invalid value for {attr_name}: {event[attr_name]}. "
                    f"Expected one of: {allowed}"
                )

    return errors


__all__ = [
    'EquipmentType',
    'ProductType',
    'MaintenanceType',
    'QualityIssue',
    'OEE_ATTRIBUTES',
    'IIOT_SENSOR_ATTRIBUTES',
    'MANUFACTURING_WORKFLOW_SCHEMA',
    'MANUFACTURING_ACTIVITIES',
    'ManufacturingEvent',
    'OEE_CALCULATION_STANDARDS',
    'calculate_oee',
    'validate_manufacturing_schema',
]
