'''
PM4Py – Healthcare Schemas
Copyright (C) 2026 Process Intelligence Solutions GmbH

Patient journey event schemas and HIPAA compliance attributes.
'''

from typing import Dict, List, Any, Set
from dataclasses import dataclass, field
from enum import Enum


class ActivityType(Enum):
    """Healthcare activity types."""
    PATIENT_REGISTRATION = "Patient Registration"
    INSURANCE_VERIFICATION = "Insurance Verification"
    TRIAGE_ASSESSMENT = "Triage Assessment"
    PHYSICIAN_CONSULTATION = "Physician Consultation"
    LAB_TEST_ORDER = "Lab Test Order"
    DIAGNOSTIC_PROCEDURE = "Diagnostic Procedure"
    TREATMENT_ADMINISTRATION = "Treatment Administration"
    MEDICATION_DISPENSING = "Medication Dispensing"
    PATIENT_DISCHARGE = "Patient Discharge"
    FOLLOW_UP_SCHEDULING = "Follow-Up Scheduling"


class Department(Enum):
    """Hospital departments."""
    EMERGENCY = "Emergency"
    INPATIENT = "Inpatient"
    OUTPATIENT = "Outpatient"
    ICU = "Intensive Care"
    SURGERY = "Surgery"
    LABORATORY = "Laboratory"
    RADIOLOGY = "Radiology"
    PHARMACY = "Pharmacy"


# HIPAA Required Attributes (45 CFR 164.312)
HIPAA_REQUIRED_ATTRIBUTES = {
    "hipaa:access_control": {
        "description": "Access control mechanism (45 CFR 164.312(a)(1))",
        "required": True,
        "data_type": "string",
        "allowed_values": ["RBAC", "MFA", "SAML", "LDAP"],
    },
    "hipaa:audit_trail": {
        "description": "Complete audit trail (45 CFR 164.312(b))",
        "required": True,
        "data_type": "list",
        "validation": lambda x: isinstance(x, list) and len(x) > 0,
    },
    "hipaa:integrity": {
        "description": "Data integrity controls (45 CFR 164.312(c)(1))",
        "required": True,
        "data_type": "boolean",
    },
    "hipaa:transmission_security": {
        "description": "Transmission security (45 CFR 164.312(e)(1))",
        "required": True,
        "data_type": "boolean",
    },
    "hipaa:encryption": {
        "description": "Encryption at rest and in transit (45 CFR 164.312(e)(2)(ii))",
        "required": True,
        "data_type": "boolean",
    },
}


# Consent Tracking Attributes
CONSENT_TRACKING_ATTRIBUTES = {
    "consent:treatment": {
        "description": "Consent for treatment",
        "required": True,
        "data_type": "boolean",
    },
    "consent:data_sharing": {
        "description": "Consent for data sharing",
        "required": True,
        "data_type": "boolean",
    },
    "consent:timestamp": {
        "description": "Consent timestamp",
        "required": True,
        "data_type": "datetime",
    },
    "consent:withdrawn": {
        "description": "Whether consent has been withdrawn",
        "required": False,
        "data_type": "boolean",
    },
    "consent:withdrawal_timestamp": {
        "description": "Consent withdrawal timestamp",
        "required": False,
        "data_type": "datetime",
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
        # Patient identification
        "patient:Id": {
            "type": "string",
            "description": "Unique patient identifier",
            "required": True,
        },
        "case:concept:name": {
            "type": "string",
            "description": "Encounter/Case ID",
            "required": True,
        },
        # Clinical attributes
        "org:department": {
            "type": "string",
            "description": "Department/Unit",
            "allowed_values": [
                "Emergency", "ICU", "Surgery", "Radiology",
                "Laboratory", "Pharmacy", "Ward",
            ],
        },
        "org:resource": {
            "type": "string",
            "description": "Resource (doctor, nurse, etc.)",
        },
    },
}


# Standard Patient Journey Activities
PATIENT_ACTIVITIES = {
    "patient_registration": "Patient Registration",
    "triage": "Triage",
    "vital_signs": "Vital Signs",
    "physician_consultation": "Physician Consultation",
    "treatment": "Treatment",
    "patient_discharge": "Patient Discharge",
}


# Standard Clinical Pathways
STANDARD_PATHWAYS = {
    "emergency_pathway": [
        "patient_registration", "triage", "vital_signs",
        "physician_consultation", "treatment", "patient_discharge",
    ],
}


@dataclass
class PatientEvent:
    """Typed patient journey event."""
    activity: str
    timestamp: Any
    case_id: str
    patient_id: str
    department: str = "Emergency"
    resource: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "concept:name": self.activity,
            "time:timestamp": self.timestamp,
            "case:concept:name": self.case_id,
            "patient:Id": self.patient_id,
            "org:department": self.department,
            "org:resource": self.resource,
        }


def validate_schema(event: Dict[str, Any]) -> List[str]:
    """Validate a patient event against the schema."""
    errors = []
    event_level = PATIENT_JOURNEY_SCHEMA.get("event_level", {})
    for attr_name, attr_def in event_level.items():
        if attr_def.get("required", False) and attr_name not in event:
            errors.append(f"Missing required attribute: {attr_name}")
    return errors


def identify_pathway(activities: List[str], min_similarity: float = 0.7) -> tuple[str, float]:
    """Identify which clinical pathway a case follows."""
    from difflib import SequenceMatcher
    best_match = "unknown"
    best_similarity = 0.0
    for pathway_name, pathway_activities in STANDARD_PATHWAYS.items():
        matcher = SequenceMatcher(None, activities, pathway_activities)
        similarity = matcher.ratio()
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = pathway_name
    return best_match, best_similarity


__all__ = [
    'HIPAA_REQUIRED_ATTRIBUTES',
    'CONSENT_TRACKING_ATTRIBUTES',
    'PATIENT_JOURNEY_SCHEMA',
    'PATIENT_ACTIVITIES',
    'STANDARD_PATHWAYS',
    'PatientEvent',
    'validate_schema',
    'identify_pathway',
]
