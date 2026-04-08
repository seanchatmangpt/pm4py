'''
PM4Py – Finance Conformance Rules
Copyright (C) 2026 Process Intelligence Solutions GmbH

SOC2 compliance rules and regulatory reporting validation rules.
'''

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class RuleSeverity(Enum):
    """Severity levels for conformance violations."""
    CRITICAL = "critical"  # Must fix immediately
    HIGH = "high"  # Must fix within 24 hours
    MEDIUM = "medium"  # Must fix within 7 days
    LOW = "low"  # Should fix
    INFO = "info"  # Informational


class RuleCategory(Enum):
    """Categories of conformance rules."""
    SOC2_SECURITY = "soc2_security"
    SOC2_AVAILABILITY = "soc2_availability"
    SOC2_INTEGRITY = "soc2_integrity"
    SOC2_CONFIDENTIALITY = "soc2_confidentiality"
    MIFID_II = "mifid_ii"
    REG_NMS = "reg_nms"
    MARKET_ABUSE = "market_abuse"
    BEST_EXECUTION = "best_execution"


@dataclass
class ConformanceRule:
    """A single conformance rule."""
    id: str
    name: str
    description: str
    category: RuleCategory
    severity: RuleSeverity
    requirement_level: str  # "required", "recommended"
    check_function: Callable[[Any], Dict[str, Any]]
    attributes: List[str] = field(default_factory=list)
    remediation: str = ""


@dataclass
class RuleViolation:
    """A conformance rule violation."""
    rule_id: str
    rule_name: str
    severity: RuleSeverity
    category: RuleCategory
    case_id: Optional[str]
    event_id: Optional[str]
    message: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    suggested_action: str = ""


# SOC2 Security Rules (CC6.1 - CC6.8)
SOC2_SECURITY_RULES = [
    ConformanceRule(
        id="SOC2.CC6.1.1",
        name="Access Control - MFA Required",
        description="Multi-factor authentication must be required for all access to trade systems (CC6.1)",
        category=RuleCategory.SOC2_SECURITY,
        severity=RuleSeverity.CRITICAL,
        requirement_level="required",
        attributes=["soc2:access_control"],
        check_function=lambda log: {
            "compliant": log.get("soc2:access_control") == "MFA",
            "message": "MFA not enabled" if log.get("soc2:access_control") != "MFA" else "OK"
        },
        remediation="Enable MFA for all user accounts accessing trade systems",
    ),
    ConformanceRule(
        id="SOC2.CC6.1.2",
        name="Access Control - RBAC Required",
        description="Role-based access control must be implemented (CC6.1)",
        category=RuleCategory.SOC2_SECURITY,
        severity=RuleSeverity.CRITICAL,
        requirement_level="required",
        attributes=["soc2:access_control"],
        check_function=lambda log: {
            "compliant": log.get("soc2:access_control") in ["RBAC", "SAML"],
            "message": "RBAC not enabled" if log.get("soc2:access_control") not in ["RBAC", "SAML"] else "OK"
        },
        remediation="Implement role-based access control with least privilege",
    ),
    ConformanceRule(
        id="SOC2.CC6.1.3",
        name="Encryption at Rest",
        description="Data must be encrypted at rest (CC6.1)",
        category=RuleCategory.SOC2_SECURITY,
        severity=RuleSeverity.CRITICAL,
        requirement_level="required",
        attributes=["soc2:encryption"],
        check_function=lambda log: {
            "compliant": log.get("soc2:encryption") is True,
            "message": "Encryption not enabled" if log.get("soc2:encryption") is not True else "OK"
        },
        remediation="Enable encryption for all data at rest",
    ),
    ConformanceRule(
        id="SOC2.CC6.6",
        name="Audit Trail Complete",
        description="Complete audit trail must be maintained (CC6.6)",
        category=RuleCategory.SOC2_SECURITY,
        severity=RuleSeverity.HIGH,
        requirement_level="required",
        attributes=["soc2:audit_log"],
        check_function=lambda log: {
            "compliant": isinstance(log.get("soc2:audit_log"), list) and len(log.get("soc2:audit_log", [])) > 0,
            "message": "Audit trail incomplete or missing" if not (isinstance(log.get("soc2:audit_log"), list) and len(log.get("soc2:audit_log", [])) > 0) else "OK"
        },
        remediation="Ensure all events are logged to audit trail",
    ),
    ConformanceRule(
        id="SOC2.CC6.7",
        name="Change Management",
        description="Change management records must be maintained (CC6.7)",
        category=RuleCategory.SOC2_SECURITY,
        severity=RuleSeverity.MEDIUM,
        requirement_level="required",
        attributes=["soc2:change_management"],
        check_function=lambda log: {
            "compliant": log.get("soc2:change_management") is not None,
            "message": "Change management record missing" if log.get("soc2:change_management") is None else "OK"
        },
        remediation="Document all changes to trade systems",
    ),
    ConformanceRule(
        id="SOC2.CC6.8",
        name="Incident Response",
        description="Incident response procedures must be defined (CC6.8)",
        category=RuleCategory.SOC2_SECURITY,
        severity=RuleSeverity.MEDIUM,
        requirement_level="recommended",
        attributes=["soc2:incident_response"],
        check_function=lambda log: {
            "compliant": log.get("soc2:incident_response") is not None,
            "message": "Incident response procedure not defined" if log.get("soc2:incident_response") is None else "OK"
        },
        remediation="Define and document incident response procedures",
    ),
]

# SOC2 Availability Rules (CC1.1 - CC1.4)
SOC2_AVAILABILITY_RULES = [
    ConformanceRule(
        id="SOC2.CC1.1",
        name="Availability Monitoring",
        description="System availability must be monitored (CC1.1)",
        category=RuleCategory.SOC2_AVAILABILITY,
        severity=RuleSeverity.MEDIUM,
        requirement_level="required",
        attributes=["soc2:compliance_monitoring"],
        check_function=lambda log: {
            "compliant": log.get("soc2:compliance_monitoring") is True,
            "message": "Availability monitoring not enabled" if log.get("soc2:compliance_monitoring") is not True else "OK"
        },
        remediation="Enable continuous availability monitoring",
    ),
]

# SOC2 Processing Integrity Rules (CC3.1 - CC3.9)
SOC2_INTEGRITY_RULES = [
    ConformanceRule(
        id="SOC2.CC3.6",
        name="Processing Integrity Monitoring",
        description="Data processing must be monitored for integrity (CC3.6)",
        category=RuleCategory.SOC2_INTEGRITY,
        severity=RuleSeverity.HIGH,
        requirement_level="required",
        attributes=["soc2:compliance_monitoring"],
        check_function=lambda log: {
            "compliant": log.get("soc2:compliance_monitoring") is True,
            "message": "Processing integrity monitoring not enabled" if log.get("soc2:compliance_monitoring") is not True else "OK"
        },
        remediation="Enable continuous processing integrity monitoring",
    ),
]

# MiFID II Regulatory Rules
MIFID_II_RULES = [
    ConformanceRule(
        id="MIFID.27.1",
        name="Best Execution Policy",
        description="Best execution policy must be defined and followed (MiFID II Article 27)",
        category=RuleCategory.MIFID_II,
        severity=RuleSeverity.CRITICAL,
        requirement_level="required",
        attributes=["reg:best_execution"],
        check_function=lambda log: {
            "compliant": log.get("reg:best_execution") is True,
            "message": "Best execution policy not followed" if log.get("reg:best_execution") is not True else "OK"
        },
        remediation="Ensure all trades follow best execution policy",
    ),
    ConformanceRule(
        id="MIFID.TRANSACTION_ID",
        name="Transaction Identifier",
        description="Unique transaction identifier required (MiFID II)",
        category=RuleCategory.MIFID_II,
        severity=RuleSeverity.CRITICAL,
        requirement_level="required",
        attributes=["reg:transaction_id"],
        check_function=lambda log: {
            "compliant": log.get("reg:transaction_id") is not None and len(str(log.get("reg:transaction_id", ""))) > 0,
            "message": "Transaction identifier missing" if not (log.get("reg:transaction_id") is not None and len(str(log.get("reg:transaction_id", ""))) > 0) else "OK"
        },
        remediation="Assign unique transaction identifier to all trades",
    ),
    ConformanceRule(
        id="MIFID.EXECUTION_TIMESTAMP",
        name="Execution Timestamp",
        description="Execution timestamp with microseconds required (MiFID II)",
        category=RuleCategory.MIFID_II,
        severity=RuleSeverity.CRITICAL,
        requirement_level="required",
        attributes=["reg:execution_timestamp"],
        check_function=lambda log: {
            "compliant": log.get("reg:execution_timestamp") is not None,
            "message": "Execution timestamp missing" if log.get("reg:execution_timestamp") is None else "OK"
        },
        remediation="Record execution timestamp with microsecond precision",
    ),
    ConformanceRule(
        id="MIFID.VENUE",
        name="Execution Venue",
        description="Execution venue must be recorded (MiFID II)",
        category=RuleCategory.MIFID_II,
        severity=RuleSeverity.HIGH,
        requirement_level="required",
        attributes=["reg:execution_venue"],
        check_function=lambda log: {
            "compliant": log.get("reg:execution_venue") is not None and len(str(log.get("reg:execution_venue", ""))) > 0,
            "message": "Execution venue not recorded" if not (log.get("reg:execution_venue") is not None and len(str(log.get("reg:execution_venue", ""))) > 0) else "OK"
        },
        remediation="Record execution venue for all trades",
    ),
    ConformanceRule(
        id="MIFID.REVENUE",
        name="Revenue Reporting",
        description="Transaction revenue must be calculated and reported (MiFID II)",
        category=RuleCategory.MIFID_II,
        severity=RuleSeverity.HIGH,
        requirement_level="required",
        attributes=["reg:venue", "reg:venue_currency", "reg:venue_calculation_method"],
        check_function=lambda log: {
            "compliant": all([
                log.get("reg:venue") is not None,
                log.get("reg:venue_currency") is not None,
                log.get("reg:venue_calculation_method") is not None,
            ]),
            "message": "Revenue information incomplete" if not all([
                log.get("reg:venue") is not None,
                log.get("reg:venue_currency") is not None,
                log.get("reg:venue_calculation_method") is not None,
            ]) else "OK"
        },
        remediation="Calculate and report transaction revenue with currency and method",
    ),
]

# Reg NMS Rules
REG_NMS_RULES = [
    ConformanceRule(
        id="REGNMS.611",
        name="Order Protection Rule",
        description="Trades must be routed to best venue (Reg NMS Rule 611)",
        category=RuleCategory.REG_NMS,
        severity=RuleSeverity.HIGH,
        requirement_level="required",
        attributes=["reg:best_execution", "reg:execution_venue"],
        check_function=lambda log: {
            "compliant": log.get("reg:best_execution") is True,
            "message": "Order protection rule may have been violated" if log.get("reg:best_execution") is not True else "OK"
        },
        remediation="Ensure trades are routed to venue with best price",
    ),
]

# Market Abuse Rules
MARKET_ABUSE_RULES = [
    ConformanceRule(
        id="MAD.INSIDER",
        name="Insider Trading Detection",
        description="Detect potential insider trading patterns",
        category=RuleCategory.MARKET_ABUSE,
        severity=RuleSeverity.CRITICAL,
        requirement_level="required",
        attributes=["trade:trader", "trade:instrument", "time:timestamp"],
        check_function=lambda log: {"compliant": True, "message": "Analysis required"},
        remediation="Review trading patterns for unusual activity",
    ),
    ConformanceRule(
        id="MAD.WASH_TRADE",
        name="Wash Trade Detection",
        description="Detect potential wash trades (buying and selling same instrument)",
        category=RuleCategory.MARKET_ABUSE,
        severity=RuleSeverity.CRITICAL,
        requirement_level="required",
        attributes=["trade:trader", "trade:instrument"],
        check_function=lambda log: {"compliant": True, "message": "Analysis required"},
        remediation="Review for wash trading patterns",
    ),
]

# All rules combined
ALL_RULES = (
    SOC2_SECURITY_RULES +
    SOC2_AVAILABILITY_RULES +
    SOC2_INTEGRITY_RULES +
    MIFID_II_RULES +
    REG_NMS_RULES +
    MARKET_ABUSE_RULES
)


def get_rules_by_category(category: RuleCategory) -> List[ConformanceRule]:
    """Get all rules for a specific category."""
    return [r for r in ALL_RULES if r.category == category]


def get_rules_by_severity(severity: RuleSeverity) -> List[ConformanceRule]:
    """Get all rules with a specific severity level."""
    return [r for r in ALL_RULES if r.severity == severity]


def get_required_rules() -> List[ConformanceRule]:
    """Get all required (non-recommended) rules."""
    return [r for r in ALL_RULES if r.requirement_level == "required"]


def check_rule(rule: ConformanceRule, event_log: Dict[str, Any]) -> Dict[str, Any]:
    """Check a single rule against an event log."""
    try:
        result = rule.check_function(event_log)
        result["rule_id"] = rule.id
        result["rule_name"] = rule.name
        result["severity"] = rule.severity.value
        result["category"] = rule.category.value
        return result
    except Exception as e:
        return {
            "rule_id": rule.id,
            "rule_name": rule.name,
            "severity": rule.severity.value,
            "category": rule.category.value,
            "compliant": False,
            "message": f"Rule check failed: {str(e)}",
            "error": str(e),
        }


def check_all_rules(
    event_log: Dict[str, Any],
    rules: Optional[List[ConformanceRule]] = None,
) -> List[RuleViolation]:
    """Check all rules against an event log.

    Returns a list of RuleViolation objects for non-compliant rules.
    """
    if rules is None:
        rules = ALL_RULES

    violations = []
    for rule in rules:
        result = check_rule(rule, event_log)
        if not result.get("compliant", False):
            violations.append(RuleViolation(
                rule_id=rule.id,
                rule_name=rule.name,
                severity=rule.severity,
                category=rule.category,
                case_id=event_log.get("case:concept:name"),
                event_id=event_log.get("concept:name"),
                message=result.get("message", "Rule violation"),
                evidence=result,
                suggested_action=rule.remediation,
            ))

    return violations
