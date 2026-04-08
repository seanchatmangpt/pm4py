'''
PM4Py – Healthcare Demo Data Generator
Copyright (C) 2026 Process Intelligence Solutions GmbH

Generates synthetic patient journey data for testing and demos.
'''

from typing import List, Dict, Any, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from pm4py.verticals.healthcare.schemas import (
    PatientEvent,
    STANDARD_PATHWAYS,
    PATIENT_ACTIVITIES,
    PATIENT_JOURNEY_SCHEMA,
)


def generate_synthetic_patient_data(
    n_patients: int = 100,
    n_departments: int = 5,
    seed: int = 42,
    return_dataframe: bool = True,
    start_date: Optional[datetime] = None,
    variability: float = 0.3,
) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Generate synthetic patient journey event log.

    Creates realistic patient journeys with:
    - Proper activity sequences
    - Realistic timing distributions
    - HIPAA-compliant attributes
    - Consent tracking
    - Department assignments

    :param n_patients: Number of patients to generate
    :param n_departments: Number of departments to simulate
    :param seed: Random seed for reproducibility
    :param return_dataframe: Return DataFrame instead of list of dicts
    :param start_date: Start date for events (default: 30 days ago)
    :param variability: Timing variability (0-1)
    :return: Synthetic patient journey log
    """
    np.random.seed(seed)

    if start_date is None:
        start_date = datetime.now() - timedelta(days=30)

    # Select departments to use
    available_depts = list(Department)[:n_departments]

    # Generate patient journeys
    events = []
    case_id = 0

    # Pathway weights (more common pathways selected more often)
    pathways = list(STANDARD_PATHWAYS.values())
    pathway_weights = [0.3, 0.25, 0.35, 0.1]  # Elective surgery, emergency, etc.

    for patient_idx in range(n_patients):
        # Select a clinical pathway
        pathway_idx = np.random.choice(len(pathways), p=pathway_weights)
        pathway = pathways[pathway_idx]

        # Generate case ID
        case_id += 1
        case_id_str = f"PATIENT_{case_id:06d}"

        # Patient attributes
        patient_id = f"P{patient_idx + 1000:06d}"
        age = np.random.randint(18, 90)
        gender = np.random.choice(["M", "F", "X"], p=[0.48, 0.48, 0.04])

        # Select primary department
        primary_dept = np.random.choice(available_depts)

        # Generate events following the pathway
        current_time = start_date + timedelta(
            hours=np.random.randint(0, 24 * 30)  # Spread across 30 days
        )

        consent_granted = np.random.choice([True, True, True, False])  # 75% granted
        consent_timestamp = current_time - timedelta(hours=np.random.uniform(0, 24))

        for activity_idx, activity in enumerate(pathway.activities):
            # Add variability to timing
            base_duration = _get_activity_duration(activity)
            duration = base_duration * (1 + np.random.uniform(-variability, variability))

            # Generate event
            event = {
                "case:concept:name": case_id_str,
                "concept:name": activity,
                "time:timestamp": current_time,
                "lifecycle:transition": "complete",
                "patient:Id": _hash_patient_id(patient_id),  # Hash for HIPAA
                "patient:age": age if activity_idx == 0 else None,  # Only in first event
                "patient:gender": gender if activity_idx == 0 else None,
                "org:department": _get_department_for_activity(activity, primary_dept, available_depts),
                "org:resource": f"STAFF_{np.random.randint(1, 50):04d}",
                "org:role": _get_role_for_activity(activity),
                "clinical:severity": np.random.choice(["Low", "Medium", "High", "Critical"],
                                                      p=[0.4, 0.35, 0.2, 0.05]),
                "clinical:priority": np.random.choice(["Routine", "Urgent", "Emergency"],
                                                      p=[0.7, 0.25, 0.05]),
                "wait:time_minutes": max(0, np.random.normal(15, 10)),
                "consent:status": "granted" if consent_granted else "withdrawn",
                "consent:timestamp": consent_timestamp.isoformat(),

                # HIPAA compliance attributes
                "phi:audit_trail": f"[{datetime.now().isoformat()}] ACCESS by STAFF",
                "phi:access_control": np.random.choice(["provider", "admin", "billing"]),
                "phi:minimum_necessary": True,
                "phi:encrypted": True,
            }

            events.append(event)

            # Move to next event time
            current_time += timedelta(minutes=duration)

        # Add discharge event
        events.append({
            "case:concept:name": case_id_str,
            "concept:name": ActivityType.PATIENT_DISCHARGE.value,
            "time:timestamp": current_time + timedelta(minutes=30),
            "lifecycle:transition": "complete",
            "patient:Id": _hash_patient_id(patient_id),
            "org:department": primary_dept.value,
            "org:resource": f"STAFF_{np.random.randint(1, 50):04d}",
            "org:role": "Administrator",
            "outcome:disposition": np.random.choice(["Home", "Transfer", "Admission"],
                                                   p=[0.85, 0.12, 0.03]),
            "consent:status": "granted" if consent_granted else "withdrawn",
            "phi:audit_trail": f"[{datetime.now().isoformat()}] DISCHARGE",
            "phi:access_control": "provider",
            "phi:minimum_necessary": True,
            "phi:encrypted": True,
        })

    # Create DataFrame
    df = pd.DataFrame(events)

    # Ensure proper datetime
    df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])

    # Convert to EventLog if requested
    if not return_dataframe:
        from pm4py.conversion import convert_to_event_log
        return convert_to_event_log(df)

    return df


def _hash_patient_id(patient_id: str) -> str:
    """Hash patient ID for HIPAA compliance."""
    import hashlib
    return hashlib.sha256(patient_id.encode()).hexdigest()[:16]


def _get_activity_duration(activity: str) -> float:
    """Get typical duration for an activity in minutes."""
    durations = {
        ActivityType.PATIENT_REGISTRATION.value: 10,
        ActivityType.INSURANCE_VERIFICATION.value: 15,
        ActivityType.TRIAGE_ASSESSMENT.value: 20,
        ActivityType.PHYSICIAN_CONSULTATION.value: 30,
        ActivityType.NURSE_ASSESSMENT.value: 15,
        ActivityType.DIAGNOSTIC_TEST.value: 45,
        ActivityType.LABORATORY_TEST.value: 30,
        ActivityType.RADIOLOGY_EXAM.value: 40,
        ActivityType.MEDICATION_ADMINISTRATION.value: 5,
        ActivityType.TREATMENT_PROCEDURE.value: 60,
        ActivityType.SURGERY.value: 180,
        ActivityType.THERAPY_SESSION.value: 45,
        ActivityType.DISCHARGE_PLANNING.value: 30,
        ActivityType.PATIENT_DISCHARGE.value: 20,
        ActivityType.DEPARTMENT_TRANSFER.value: 15,
        ActivityType.ADMISSION.value: 40,
        ActivityType.EMERGENCY_ADMISSION.value: 20,
        ActivityType.BILLING.value: 10,
    }
    return float(durations.get(activity, 30))


def _get_department_for_activity(
    activity: str,
    primary_dept: Department,
    available_depts: List[Department],
) -> str:
    """Get appropriate department for an activity."""
    # Map activities to typical departments
    dept_map = {
        ActivityType.RADIOLOGY_EXAM.value: Department.RADIOLOGY,
        ActivityType.LABORATORY_TEST.value: Department.LABORATORY,
        ActivityType.SURGERY.value: Department.SURGERY,
        ActivityType.EMERGENCY_ADMISSION.value: Department.EMERGENCY,
        ActivityType.TRIAGE_ASSESSMENT.value: Department.EMERGENCY,
    }

    if activity in dept_map and dept_map[activity] in available_depts:
        return dept_map[activity].value

    # Specialized departments for specific activities
    if "Cardiology" in activity and Department.CARDIOLOGY in available_depts:
        return Department.CARDIOLOGY.value
    if "Orthopedic" in activity and Department.ORTHOPEDICS in available_depts:
        return Department.ORTHOPEDICS.value

    return primary_dept.value


def _get_role_for_activity(activity: str) -> str:
    """Get appropriate role for an activity."""
    if "PHYSICIAN" in activity or "Consultation" in activity:
        return "Physician"
    elif "NURSE" in activity or "Assessment" in activity:
        return "Nurse"
    elif "TEST" in activity or "Exam" in activity or "Laboratory" in activity:
        return "Technician"
    elif "THERAPY" in activity:
        return "Therapist"
    elif "Registration" in activity or "Billing" in activity or "Discharge" in activity:
        return "Administrator"
    return "Nurse"


def generate_benchmark_dataset(
    variant: str = "typical",
    n_patients: int = 500,
) -> pd.DataFrame:
    """
    Generate benchmark datasets for different scenarios.

    :param variant: Dataset variant ('typical', 'high_volume', 'bottlenecks', 'compliant')
    :param n_patients: Number of patients
    :return: Benchmark dataset
    """
    if variant == "typical":
        return generate_synthetic_patient_data(n_patients=n_patients)

    elif variant == "high_volume":
        # High volume emergency department
        return generate_synthetic_patient_data(
            n_patients=n_patients * 2,
            n_departments=3,
            variability=0.5,
        )

    elif variant == "bottlenecks":
        # Dataset with intentional bottlenecks
        data = generate_synthetic_patient_data(n_patients=n_patients)
        # Add extra wait times to specific activities
        mask = data["concept:name"].isin([
            ActivityType.PHYSICIAN_CONSULTATION.value,
            ActivityType.RADIOLOGY_EXAM.value,
        ])
        data.loc[mask, "wait:time_minutes"] = data.loc[mask, "wait:time_minutes"] * 3
        return data

    elif variant == "compliant":
        # Fully HIPAA-compliant dataset
        data = generate_synthetic_patient_data(n_patients=n_patients)
        # Ensure all compliance flags are True
        data["phi:minimum_necessary"] = True
        data["phi:encrypted"] = True
        return data

    else:
        return generate_synthetic_patient_data(n_patients=n_patients)


__all__ = [
    'generate_synthetic_patient_data',
    'generate_benchmark_dataset',
]
