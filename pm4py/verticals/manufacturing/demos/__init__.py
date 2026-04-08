'''
PM4Py – Manufacturing Demo Data Generator
Copyright (C) 2026 Process Intelligence Solutions GmbH

Generates synthetic manufacturing event data for testing and demos.
'''

from typing import List, Dict, Any, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from pm4py.verticals.manufacturing.schemas import (
    EquipmentType,
    ProductType,
    MaintenanceType,
    QualityIssue,
    MANUFACTURING_ACTIVITIES,
    OEE_CALCULATION_STANDARDS,
    calculate_oee,
)


def generate_synthetic_manufacturing_data(
    n_orders: int = 500,
    n_equipment: int = 15,
    n_products: int = 20,
    seed: int = 42,
    return_dataframe: bool = True,
    start_date: Optional[datetime] = None,
    variability: float = 0.3,
) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Generate synthetic manufacturing workflow event log.

    Creates realistic manufacturing workflows with:
    - Proper activity sequences (order → setup → production → quality → shipping)
    - Realistic timing distributions
    - OEE calculation attributes
    - Quality inspection results
    - Maintenance events
    - IIoT sensor data

    :param n_orders: Number of production orders to generate
    :param n_equipment: Number of equipment units to simulate
    :param n_products: Number of product types
    :param seed: Random seed for reproducibility
    :param return_dataframe: Return DataFrame instead of list of dicts
    :param start_date: Start date for events (default: 30 days ago)
    :param variability: Timing variability (0-1)
    :return: Synthetic manufacturing workflow log
    """
    np.random.seed(seed)

    if start_date is None:
        start_date = datetime.now() - timedelta(days=30)

    # Generate equipment
    equipment = _generate_equipment(n_equipment)

    # Generate products
    products = _generate_products(n_products)

    # Generate operators
    operators = [f"OPERATOR_{i:04d}" for i in range(1, 31)]

    # Generate technicians
    technicians = [f"TECH_{i:04d}" for i in range(1, 11)]

    # Generate inspectors
    inspectors = [f"INSP_{i:04d}" for i in range(1, 11)]

    # Generate orders
    events = []
    case_id = 0

    for _ in range(n_orders):
        case_id += 1
        case_id_str = f"ORDER_{case_id:06d}"

        # Select product and equipment
        product = np.random.choice(products)
        equipment_unit = np.random.choice(equipment)

        # Generate order details
        order_id = f"PO-{datetime.now().strftime('%Y%m%d')}-{case_id:06d}"
        quantity = np.random.choice([10, 50, 100, 500, 1000])
        priority = np.random.choice(["urgent", "high", "normal", "normal", "normal", "low"],
                                    p=[0.05, 0.1, 0.6, 0.15, 0.05, 0.05])

        # Generate production events following the workflow
        current_time = start_date + timedelta(
            hours=np.random.randint(0, 24 * 30),
            minutes=np.random.randint(0, 60),
            seconds=np.random.randint(0, 60),
            microseconds=np.random.randint(0, 1000000),
        )

        # Generate unique serial numbers for pieces
        serial_numbers = [f"SN-{case_id:06d}-{i:04d}" for i in range(quantity)]

        # Quality outcome (mostly pass)
        quality_pass = np.random.choice([True, True, True, True, False])  # 80% pass
        defect_code = np.random.choice([t.value for t in QualityIssue]) if not quality_pass else None

        # Calculate OEE metrics for this order
        planned_production_time = 480  # 8 hours in minutes
        maintenance_downtime = np.random.choice([0, 0, 0, 15, 30, 60])  # Some downtime
        breakdown_downtime = np.random.choice([0, 0, 0, 0, 30, 60, 120])  # Occasional breakdown
        total_downtime = maintenance_downtime + breakdown_downtime
        run_time = planned_production_time - total_downtime

        # Calculate pieces
        defective_count = int(quantity * 0.02) if quality_pass else int(quantity * np.random.uniform(0.05, 0.15))
        good_pieces = quantity - defective_count

        # Ideal cycle time based on product
        ideal_cycle_time = _get_ideal_cycle_time(product)

        # Calculate OEE
        oee_metrics = calculate_oee(
            run_time=run_time,
            planned_production_time=planned_production_time,
            total_pieces=quantity,
            good_pieces=good_pieces,
            ideal_cycle_time=ideal_cycle_time,
        )

        # Generate events for the production lifecycle
        activities = [
            ("order_received", 0),
            ("order_review", 5),
            ("material_picking", 15),
            ("equipment_setup", 30),
            ("tool_loading", 45),
            ("first_piece_inspection", 60),
            ("production_start", 75),
            ("machining", 120),
            ("inspection", 180),
            ("quality_check", 240),
            ("packaging", 300),
            ("order_completion", 360),
            ("shipping", 420),
        ]

        # Add maintenance events
        maintenance_events = []
        if maintenance_downtime > 0:
            maintenance_events.append(("preventive_maintenance", 90))

        if breakdown_downtime > 0:
            maintenance_events.append(("emergency_repair", 150))

        # Combine activities with maintenance
        all_activities = activities[:4]  # Before production
        all_activities.extend(maintenance_events)
        all_activities.extend(activities[4:])  # After setup

        # Add randomness to timing
        for activity, base_offset in all_activities:
            offset = base_offset * (1 + np.random.uniform(-variability, variability))
            event_time = current_time + timedelta(minutes=offset)

            # Determine equipment status
            if activity == "preventive_maintenance":
                equipment_status = "maintenance"
            elif activity == "emergency_repair":
                equipment_status = "breakdown"
            elif "production" in activity or "machining" in activity:
                equipment_status = "running"
            elif "setup" in activity or "loading" in activity:
                equipment_status = "setup"
            else:
                equipment_status = "running"

            # Determine quality status
            if activity in ["inspection", "quality_check", "first_piece_inspection"]:
                q_status = "pass" if quality_pass else "fail"
            else:
                q_status = None

            # IIoT sensor data (simulated)
            sensor_data = _generate_sensor_data() if activity in ["machining", "production_start"] else {}

            events.append({
                "case:concept:name": case_id_str,
                "concept:name": activity,
                "time:timestamp": event_time,
                "lifecycle:transition": "complete",
                "production:order_id": order_id,
                "production:product_id": product,
                "production:product_type": _get_product_type(product),
                "production:serial_number": serial_numbers[0] if activity == "order_completion" else None,
                "production:quantity": quantity if activity == "order_completion" else None,
                "production:cycle_time": ideal_cycle_time * (1 + np.random.uniform(-0.1, 0.2)) if activity == "machining" else None,
                "equipment:id": equipment_unit,
                "equipment:type": _get_equipment_type(equipment_unit),
                "equipment:status": equipment_status,
                "equipment:operator": np.random.choice(operators) if activity in ["machining", "assembly"] else None,
                "quality:status": q_status,
                "quality:defect_code": defect_code if q_status == "fail" else None,
                "quality:inspector": np.random.choice(inspectors) if activity in ["inspection", "quality_check"] else None,
                "maintenance:type": np.random.choice([t.value for t in MaintenanceType]) if "maintenance" in activity or "repair" in activity else None,
                "maintenance:duration": maintenance_downtime if activity == "preventive_maintenance" else (breakdown_downtime if activity == "emergency_repair" else None),
                "maintenance:technician": np.random.choice(technicians) if "maintenance" in activity or "repair" in activity else None,
                # OEE attributes (only on production_start and order_completion)
                "oee:availability": oee_metrics["availability"] if activity == "order_completion" else None,
                "oee:performance": oee_metrics["performance"] if activity == "order_completion" else None,
                "oee:quality": oee_metrics["quality"] if activity == "order_completion" else None,
                "oee:oee": oee_metrics["oee"] if activity == "order_completion" else None,
                "oee:run_time": run_time if activity == "order_completion" else None,
                "oee:planned_production_time": planned_production_time if activity == "order_completion" else None,
                "oee:downtime": total_downtime if activity == "order_completion" else None,
                "oee:total_pieces": quantity if activity == "order_completion" else None,
                "oee:good_pieces": good_pieces if activity == "order_completion" else None,
                "oee:defective_pieces": defective_count if activity == "order_completion" else None,
                "oee:ideal_cycle_time": ideal_cycle_time if activity == "order_completion" else None,
                # IIoT sensor attributes
                "iot:sensor_id": sensor_data.get("sensor_id"),
                "iot:sensor_type": sensor_data.get("sensor_type"),
                "iot:sensor_value": sensor_data.get("sensor_value"),
                "iot:sensor_unit": sensor_data.get("sensor_unit"),
                "iot:alarm_active": sensor_data.get("alarm_active"),
            })

        # Add rework events for quality failures
        if not quality_pass:
            rework_time = current_time + timedelta(minutes=250)
            events.append({
                "case:concept:name": case_id_str,
                "concept:name": "rework",
                "time:timestamp": rework_time,
                "lifecycle:transition": "complete",
                "production:order_id": order_id,
                "equipment:id": equipment_unit,
                "equipment:status": "running",
                "quality:defect_code": defect_code,
            })

    # Create DataFrame
    df = pd.DataFrame(events)

    # Clean up None values
    df = df.replace({None: np.nan})

    # Ensure proper datetime
    df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])

    # Convert to EventLog if requested
    if not return_dataframe:
        from pm4py.conversion import convert_to_event_log
        return convert_to_event_log(df)

    return df


def _generate_equipment(n: int) -> List[str]:
    """Generate synthetic equipment IDs."""
    equipment = []
    equipment_types = [
        ("CNC", 3),
        ("PRESS", 2),
        ("ROBOT", 3),
        ("CONVEYOR", 2),
        ("WELD", 2),
        ("ASSEMBLY", 2),
        ("TEST", 1),
    ]

    idx = 0
    for prefix, count in equipment_types:
        for i in range(min(count, n - idx)):
            equipment.append(f"{prefix}-{i+1:02d}")
            idx += 1
        if idx >= n:
            break

    # Fill remaining with generic equipment
    while len(equipment) < n:
        equipment.append(f"EQUIP-{len(equipment)+1:02d}")

    return equipment[:n]


def _generate_products(n: int) -> List[str]:
    """Generate synthetic product IDs."""
    products = []

    # Electronics
    for i in range(min(n // 4, 5)):
        products.append(f"ELEC-{i+1:03d}")

    # Automotive parts
    for i in range(min(n // 4, 5)):
        products.append(f"AUTO-{i+1:03d}")

    # Consumer goods
    for i in range(min(n // 4, 5)):
        products.append(f"CONS-{i+1:03d}")

    # Fill remaining with generic products
    while len(products) < n:
        products.append(f"PROD-{len(products)+1:03d}")

    return products[:n]


def _get_ideal_cycle_time(product: str) -> float:
    """Get ideal cycle time for a product (seconds)."""
    if "ELEC" in product:
        return 45.0  # Electronics: 45 seconds
    elif "AUTO" in product:
        return 120.0  # Automotive: 2 minutes
    elif "CONS" in product:
        return 30.0  # Consumer: 30 seconds
    else:
        return 60.0  # Default: 1 minute


def _get_product_type(product: str) -> str:
    """Get product type category."""
    if "ELEC" in product:
        return ProductType.ELECTRONICS.value
    elif "AUTO" in product:
        return ProductType.AUTOMOTIVE.value
    elif "CONS" in product:
        return ProductType.CONSUMER_GOODS.value
    else:
        return ProductType.CONSUMER_GOODS.value


def _get_equipment_type(equipment: str) -> str:
    """Get equipment type from equipment ID."""
    if "CNC" in equipment:
        return EquipmentType.CNC_MACHINE.value
    elif "PRESS" in equipment:
        return EquipmentType.PRESS.value
    elif "ROBOT" in equipment or "WELD" in equipment:
        return EquipmentType.ROBOT.value
    elif "CONVEYOR" in equipment:
        return EquipmentType.CONVEYOR.value
    elif "ASSEMBLY" in equipment:
        return EquipmentType.ASSEMBLY_STATION.value
    elif "TEST" in equipment:
        return EquipmentType.TESTING_STATION.value
    else:
        return EquipmentType.ASSEMBLY_STATION.value


def _generate_sensor_data() -> Dict[str, Any]:
    """Generate synthetic IIoT sensor data."""
    sensor_types = ["temperature", "vibration", "pressure", "current"]

    sensor_type = np.random.choice(sensor_types)
    sensor_id = f"SENSOR-{sensor_type[:3].upper()}-{np.random.randint(1, 100):03d}"

    # Generate value based on sensor type
    if sensor_type == "temperature":
        value = np.random.uniform(20, 85)  # Celsius
        unit = "°C"
        alarm_active = value > 80
    elif sensor_type == "vibration":
        value = np.random.uniform(0, 10)  # mm/s
        unit = "mm/s"
        alarm_active = value > 8
    elif sensor_type == "pressure":
        value = np.random.uniform(0, 100)  # bar
        unit = "bar"
        alarm_active = value > 95 or value < 5
    else:  # current
        value = np.random.uniform(0, 50)  # Amps
        unit = "A"
        alarm_active = value > 45

    return {
        "sensor_id": sensor_id,
        "sensor_type": sensor_type,
        "sensor_value": round(value, 2),
        "sensor_unit": unit,
        "alarm_active": alarm_active,
    }


def generate_benchmark_dataset(
    variant: str = "typical",
    n_orders: int = 500,
) -> pd.DataFrame:
    """
    Generate benchmark datasets for different scenarios.

    :param variant: Dataset variant ('typical', 'high_oee', 'low_oee', 'quality_issues')
    :param n_orders: Number of production orders
    :return: Benchmark dataset
    """
    if variant == "typical":
        return generate_synthetic_manufacturing_data(n_orders=n_orders)

    elif variant == "high_oee":
        # High OEE dataset (world-class performance)
        return generate_synthetic_manufacturing_data(
            n_orders=n_orders,
            variability=0.1,  # Low variability = consistent performance
        )

    elif variant == "low_oee":
        # Low OEE dataset with issues
        data = generate_synthetic_manufacturing_data(n_orders=n_orders)

        # Reduce OEE values
        if "oee:oee" in data.columns:
            data["oee:oee"] = data["oee:oee"] * np.random.uniform(0.5, 0.8)

        if "oee:availability" in data.columns:
            data["oee:availability"] = data["oee:availability"] * np.random.uniform(0.6, 0.85)

        # Increase downtime
        if "oee:downtime" in data.columns:
            data["oee:downtime"] = data["oee:downtime"] * np.random.uniform(1.5, 3.0)

        return data

    elif variant == "quality_issues":
        # Dataset with quality problems
        data = generate_synthetic_manufacturing_data(n_orders=n_orders)

        # Increase quality failures
        quality_indices = data[data["quality:status"] == "pass"].index
        if len(quality_indices) > 0:
            fail_count = len(quality_indices) // 3  # Make 33% fail
            fail_indices = np.random.choice(quality_indices, fail_count, replace=False)
            data.loc[fail_indices, "quality:status"] = "fail"
            data.loc[fail_indices, "quality:defect_code"] = np.random.choice([
                "Dimensional Defect",
                "Surface Finish Issue",
                "Material Defect",
                "Assembly Error",
            ], size=fail_count)

        # Add more rework events
        rework_orders = data["case:concept:name"].unique()[:len(data["case:concept:name"].unique()) // 10]
        for order_id in rework_orders:
            order_data = data[data["case:concept:name"] == order_id]
            if len(order_data) > 0:
                last_event = order_data.iloc[-1]
                new_rework = {
                    "case:concept:name": order_id,
                    "concept:name": "rework",
                    "time:timestamp": last_event["time:timestamp"] + timedelta(minutes=5),
                    "lifecycle:transition": "complete",
                    "quality:status": "fail",
                }
                data = pd.concat([data, pd.DataFrame([new_rework])], ignore_index=True)

        return data

    else:
        return generate_synthetic_manufacturing_data(n_orders=n_orders)


__all__ = [
    'generate_synthetic_manufacturing_data',
    'generate_benchmark_dataset',
]
