# PM4Py Healthcare Vertical

HIPAA-ready patient journey mining with pre-built schemas, compliance rules, and dashboards.

## Features

- **Patient Journey Discovery**: Discover clinical pathways from event logs
- **HIPAA Compliance Checking**: Validate HIPAA 45 CFR 164.312 compliance
- **Consent Tracking**: Verify treatment and data sharing consent documentation
- **Patient Flow Analysis**: Visualize patient flow, wait times, and bottlenecks
- **Clinical Pathway Validation**: Compare actual journeys against expected pathways
- **Synthetic Data Generation**: Generate de-identified test data

## Installation

```bash
pip install pm4py[healthcare]
```

## Quick Start

```python
from pm4py.verticals import HealthcareVertical

# Generate demo data
log = HealthcareVertical.generate_demo_data(n_patients=100)

# Initialize vertical
vertical = HealthcareVertical(log)

# Discover patient journey model
model = vertical.discover_journey()

# Check HIPAA compliance
compliance = vertical.check_hipaa_compliance()
print(f"Compliance Score: {compliance['compliance_score']}%")

# Analyze wait times
wait_analysis = vertical.analyze_wait_times()
print(f"Average Wait: {wait_analysis['mean_wait_minutes']} minutes")

# Detect bottlenecks
bottlenecks = vertical.detect_bottlenecks()
for b in bottlenecks:
    print(f"{b['severity']} bottleneck at {b['name']}: {b['recommendation']}")

# Visualize patient flow
vertical.visualize_patient_flow(output_path="patient_flow.png")
```

## Patient Journey Event Schema

The healthcare vertical uses a standardized event schema for patient journeys:

### Required Event Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `concept:name` | string | Activity name (e.g., "Physician Consultation") |
| `time:timestamp` | datetime | Event timestamp |
| `case:concept:name` | string | Encounter/case ID |
| `patient:Id` | string | Patient identifier (should be hashed/pseudonymized) |

### HIPAA Compliance Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `phi:audit_trail` | list | Yes | Complete audit trail of PHI accesses |
| `phi:access_control` | string | Yes | Access control level (provider/admin/billing/emergency) |
| `phi:minimum_necessary` | boolean | Yes | Minimum necessary standard compliance |
| `phi:encrypted` | boolean | Yes | PHI encryption status |

### Consent Tracking Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `consent:treatment` | boolean | Yes | Consent for medical treatment |
| `consent:data_sharing` | boolean | Yes | Consent for data sharing with providers |
| `consent:research` | boolean | No | Consent for research use |
| `consent:timestamp` | datetime | Yes | Timestamp of consent acquisition |
| `consent:withdrawn` | boolean | Yes | Whether consent has been withdrawn |

### Clinical Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `org:department` | string | Department/unit (e.g., "Emergency Department") |
| `org:resource` | string | Healthcare provider ID |
| `org:role` | string | Provider role (Physician/Nurse/Technician/etc.) |
| `clinical:severity` | string | Acuity level (Low/Medium/High/Critical) |
| `clinical:priority` | string | Clinical priority (Routine/Urgent/Emergency) |
| `wait:time_minutes` | numeric | Wait time in minutes |

## Standard Activities

The healthcare vertical includes these standard activity types:

- **Intake**: Patient Registration, Insurance Verification, Triage Assessment
- **Clinical**: Physician Consultation, Nurse Assessment, Diagnostic Test, Laboratory Test, Radiology Exam
- **Treatment**: Treatment Procedure, Surgery, Therapy Session, Medication Administration
- **Discharge**: Discharge Planning, Patient Discharge, Billing
- **Transfers**: Department Transfer, Admission, Emergency Admission

## Standard Departments

- Emergency Department
- Intensive Care Unit (ICU)
- Surgery
- Radiology
- Laboratory
- Cardiology
- Orthopedics
- Pediatrics
- Obstetrics
- Oncology
- General Ward
- Outpatient Clinic
- Rehabilitation

## Clinical Pathways

Predefined clinical pathways for common care scenarios:

1. **Emergency Admission Pathway**: Triage → Physician Consultation → Diagnostic Test → Laboratory Test → Admission
2. **Elective Surgery Pathway**: Registration → Insurance Verification → Physician Consultation → Laboratory Test → Surgery → Rehabilitation → Discharge
3. **Outpatient Visit Pathway**: Registration → Nurse Assessment → Physician Consultation → Treatment Procedure → Billing
4. **Diagnostic Workup Pathway**: Physician Consultation → Laboratory Test → Radiology Exam → Diagnostic Test → Physician Consultation

## Compliance Reports

### HIPAA Compliance Check

```python
compliance = vertical.check_hipaa_compliance()

# Compliance score (0-100)
print(f"Score: {compliance['compliance_score']}%")

# Status
print(f"Status: {compliance['status']}")  # COMPLIANT or NON_COMPLIANT

# Violations
for violation in compliance['violations']:
    print(f"{violation['severity']}: {violation['description']}")
    print(f"  Section: {violation['section']}")

# Recommendations
for rec in compliance['recommendations']:
    print(f"- {rec}")
```

### Consent Tracking Check

```python
consent = vertical.check_consent_tracking()

# Completeness score
print(f"Completeness: {consent['completeness_score']}%")

# Check for missing consents
for violation in consent['violations']:
    print(f"Missing: {violation['attribute']}")
```

### Export for Audit

```python
vertical.export_for_compliance_audit("hipaa_audit_export.json")
```

## Analysis Examples

### Wait Time Analysis

```python
# Overall wait times
wait_analysis = vertical.analyze_wait_times()
print(f"Mean wait: {wait_analysis['mean_wait_minutes']} min")
print(f"P95 wait: {wait_analysis['p95_wait_minutes']} min")
print(f"Breach rate: {wait_analysis['breach_rate_percent']}%")

# Per-department wait times
for dept in ["Emergency Department", "Radiology", "Laboratory"]:
    analysis = vertical.analyze_wait_times(department=dept)
    print(f"{dept}: {analysis['mean_wait_minutes']} min average")
```

### Bottleneck Detection

```python
bottlenecks = vertical.detect_bottlenecks(threshold_percentile=75)

for b in bottlenecks:
    print(f"{b['type'].upper()}: {b['name']}")
    print(f"  Severity: {b['severity']}")
    print(f"  Recommendation: {b['recommendation']}")
```

### Clinical Pathway Analysis

```python
pathways = vertical.get_clinical_pathways()

for pathway in pathways[:5]:  # Top 5 pathways
    print(f"{pathway['pathway']}")
    print(f"  Frequency: {pathway['frequency']}")
    print(f"  Percentage: {pathway['percentage']:.1f}%")
```

### Department Statistics

```python
stats = vertical.get_department_statistics()

for dept, metrics in stats.items():
    print(f"{dept}:")
    print(f"  Cases: {metrics['case_count']}")
    print(f"  Avg duration: {metrics['avg_duration']}")
    print(f"  Activities: {metrics['activities']}")
```

## Generating Demo Data

```python
from pm4py.verticals.healthcare import generate_synthetic_patient_data

# Generate synthetic patient journeys
log = generate_synthetic_patient_data(
    n_patients=100,
    n_departments=5,
    seed=42,
    return_dataframe=True
)

# Generate benchmark scenarios
typical_data = generate_synthetic_patient_data(n_patients=500)
high_volume = generate_synthetic_patient_data(n_patients=1000, variability=0.5)
with_bottlenecks = generate_synthetic_patient_data(n_patients=500, variability=0.3)
```

## Running the Demo

```bash
python -m pm4py.verticals.healthcare.demo
```

This will:
1. Generate synthetic patient journey data
2. Discover patient journey process model
3. Run HIPAA compliance check
4. Analyze wait times and detect bottlenecks
5. Generate visualizations

## Privacy and Security

**Important**: This vertical handles Protected Health Information (PHI). Always:

1. **Hash/pseudonymize patient IDs** before analysis
2. **Enable encryption** for PHI at rest and in transit
3. **Maintain audit trails** for all PHI access
4. **Follow minimum necessary standard** - only access PHI needed for the task
5. **Verify consent** before data sharing or research use
6. **Comply with HIPAA** 45 CFR 164.312 requirements

The demo data generator automatically hashes patient IDs and includes all required HIPAA attributes.

## License

Apache License 2.0 - Copyright (C) 2026 Process Intelligence Solutions GmbH

## References

- HIPAA Privacy Rule: 45 CFR Parts 160 and 164
- HIPAA Security Rule: 45 CFR 164.302-318
- ICD-10-CM Official Guidelines for Coding and Reporting
- CPT (Current Procedural Terminology) - American Medical Association
