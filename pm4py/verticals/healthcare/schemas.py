'''
PM4Py – Healthcare Schemas
Copyright (C) 2026 Process Intelligence Solutions GmbH

HIPAA compliance, patient journey, and consent tracking schemas.
'''

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class ConsentStatus(Enum):
    """Patient consent status."""
    GRANTED = "granted"
    DENIED = "denied"
    REVOKED = "revoked"
    PENDING = "pending"


class PatientJourneyStage(Enum):
    """Patient journey stages."""
    ADMISSION = "admission"
    TRIAGE = "triage"
    EXAMINATION = "examination"
    TREATMENT = "treatment"
    DISCHARGE = "discharge"
    FOLLOW_UP = "follow_up"


# HIPAA Required Attributes
HIPAA_REQUIRED_ATTRIBUTES = {
    "patient:Id": {
        "description": "Patient identifier (de-identified)",
        "required": True,
        "data_type": "string",
    },
    "patient:birth_date": {
        "description": "Patient date of birth (de-identified, year only for privacy)",
        "required": False,
        "data_type": "date",
    },
    "patient:gender": {
        "description": "Patient gender (de-identified)",
        "required": False,
        "data_type": "string",
    },
}

# Consent Tracking Attributes
CONSENT_TRACKING_ATTRIBUTES = {
    "consent:status": {
        "description": "Consent status",
        "allowed_values": [s.value for s in ConsentStatus],
        "required": True,
    },
    "consent:type": {
        "description": "Type of consent (treatment, data sharing, research)",
        "required": True,
    },
    "consent:timestamp": {
        "description": "When consent was recorded",
        "required": True,
    },
    "consent:provider": {
        "description": "Healthcare provider who obtained consent",
        "required": True,
    },
}

# Patient Journey Event Schema
PATIENT_JOURNEY_SCHEMA = {
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

        # Patient identification (de-identified)
        "patient:Id": {
            "type": "string",
            "description": "De-identified patient ID",
            "required": True,
        },
        "patient:age_group": {
            "type": "string",
            "description": "Age group for privacy (e.g., 18-30, 31-50, 51+)",
        },
        "patient:gender": {
            "type": "string",
            "description": "Patient gender",
        },

        # Encounter/Case identification
        "case:concept:name": {
            "type": "string",
            "description": "Encounter/Case ID",
            "required": True,
        },
        "encounter:id": {
            "type": "string",
            "description": "Unique encounter identifier",
            "required": True,
        },
        "encounter:type": {
            "type": "string",
            "description": "Type of encounter (inpatient, outpatient, emergency)",
            "allowed_values": ["inpatient", "outpatient", "emergency", "telehealth"],
        },

        # Department/Location
        "org:department": {
            "type": "string",
            "description": "Department or unit",
            "required": True,
        },
        "org:location": {
            "type": "string",
            "description": "Physical location (room, bed)",
        },

        # Clinical data
        "clinical:chief_complaint": {
            "type": "string",
            "description": "Chief complaint or reason for visit",
        },
        "clinical:diagnosis_code": {
            "type": "string",
            "description": "Diagnosis code (ICD-10)",
        },
        "clinical:procedure_code": {
            "type": "string",
            "description": "Procedure code (CPT/HCPCS)",
        },
        "clinical:acuity": {
            "type": "string",
            "description": "Patient acuity level",
            "allowed_values": ["low", "moderate", "high", "critical"],
        },

        # Consent
        "consent:status": {
            "type": "string",
            "description": "Consent status",
            "allowed_values": [s.value for s in ConsentStatus],
        },

        # Resource/Staff
        "resource:staff_id": {
            "type": "string",
            "description": "Staff identifier (de-identified)",
        },
        "resource:staff_role": {
            "type": "string",
            "description": "Staff role (physician, nurse, technician)",
        },
    },

    "trace_level": {
        "patient:arrival_mode": {
            "type": "string",
            "description": "How patient arrived (walk-in, ambulance, transfer)",
        },
        "patient:disposition": {
            "type": "string",
            "description": "Discharge disposition (home, admission, transfer)",
        },
        "encounter:priority": {
            "type": "string",
            "description": "Encounter priority",
            "allowed_values": ["routine", "urgent", "emergent", "stat"],
        },
    },
}


__all__ = [
    'ConsentStatus',
    'PatientJourneyStage',
    'HIPAA_REQUIRED_ATTRIBUTES',
    'CONSENT_TRACKING_ATTRIBUTES',
    'PATIENT_JOURNEY_SCHEMA',
]
