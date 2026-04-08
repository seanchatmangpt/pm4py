'''
PM4Py – Alert Integration Module
Copyright (C) 2026 Process Intelligence Solutions GmbH

Multi-channel alert notifications for process mining events.

Supports:
- Slack (webhook)
- Jira (REST API)
- PagerDuty (Events API v2)
- Email (SMTP)
'''

import json
import smtplib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
import urllib.request
import urllib.error


class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "critical"  # System down, data loss
    HIGH = "high"  # Significant degradation
    MEDIUM = "medium"  # Minor issues
    LOW = "low"  # Informational
    INFO = "info"  # Debug/info


class AlertCategory(Enum):
    """Alert categories."""
    SYSTEM = "system"  # System health
    PROCESS = "process"  # Process discovery issues
    CONFORMANCE = "conformance"  # Compliance violations
    PERFORMANCE = "performance"  # Performance degradation
    DRIFT = "drift"  # Process drift detected
    SECURITY = "security"  # Security incidents
    COMPLIANCE = "compliance"  # Regulatory compliance


@dataclass
class Alert:
    """An alert notification."""
    id: str
    title: str
    description: str
    severity: AlertSeverity
    category: AlertCategory
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = "pm4py"
    metadata: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    assignee: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        data = asdict(self)
        data['severity'] = self.severity.value
        data['category'] = self.category.value
        data['timestamp'] = self.timestamp.isoformat()
        if self.resolved_at:
            data['resolved_at'] = self.resolved_at.isoformat()
        return data

    def to_slack_message(self) -> Dict[str, Any]:
        """Format alert for Slack."""
        color_map = {
            AlertSeverity.CRITICAL: "danger",
            AlertSeverity.HIGH: "danger",
            AlertSeverity.MEDIUM: "warning",
            AlertSeverity.LOW: "good",
            AlertSeverity.INFO: "good",
        }

        fields = [
            {"title": "Severity", "value": self.severity.value.upper(), "short": True},
            {"title": "Category", "value": self.category.value, "short": True},
            {"title": "Source", "value": self.source, "short": True},
        ]

        if self.assignee:
            fields.append({"title": "Assignee", "value": self.assignee, "short": True})

        return {
            "attachments": [{
                "color": color_map.get(self.severity, "good"),
                "title": f"[{self.severity.value.upper()}] {self.title}",
                "text": self.description,
                "fields": fields,
                "footer": "PM4Py Alert",
                "ts": int(self.timestamp.timestamp()),
            }]
        }

    def to_jira_payload(self) -> Dict[str, Any]:
        """Format alert for Jira issue creation."""
        priority_map = {
            AlertSeverity.CRITICAL: "Highest",
            AlertSeverity.HIGH: "High",
            AlertSeverity.MEDIUM: "Medium",
            AlertSeverity.LOW: "Low",
            AlertSeverity.INFO: "Lowest",
        }

        issue_type = "Bug" if self.category in [AlertCategory.SYSTEM, AlertCategory.SECURITY] else "Task"

        return {
            "fields": {
                "project": {"key": "PM4"},  # Configure your project key
                "summary": f"[{self.severity.value.upper()}] {self.title}",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": self.description,
                                }
                            ]
                        },
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"\n\nSource: {self.source}",
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {"name": issue_type},
                "priority": {"name": priority_map.get(self.severity, "Medium")},
                "labels": self.tags + [self.category.value],
            }
        }

    def to_pagerduty_event(self, dedup_key: Optional[str] = None) -> Dict[str, Any]:
        """Format alert for PagerDuty Events API v2."""
        severity_map = {
            AlertSeverity.CRITICAL: "critical",
            AlertSeverity.HIGH: "error",
            AlertSeverity.MEDIUM: "warning",
            AlertSeverity.LOW: "info",
            AlertSeverity.INFO: "info",
        }

        payload = {
            "routing_key": "",  # Set from integration key
            "event_action": "trigger",
            "payload": {
                "summary": self.title,
                "severity": severity_map.get(self.severity, "info"),
                "source": self.source,
                "timestamp": self.timestamp.isoformat(),
                "custom_details": {
                    "description": self.description,
                    "category": self.category.value,
                    **self.metadata
                }
            },
            "dedup_key": dedup_key or self.id,
        }

        if self.assignee:
            payload["payload"]["custom_details"]["assignee"] = self.assignee

        return payload


class Notifier(ABC):
    """Base class for alert notifiers."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    @abstractmethod
    def send(self, alert: Alert) -> Dict[str, Any]:
        """Send an alert notification."""
        pass

    def send_batch(self, alerts: List[Alert]) -> List[Dict[str, Any]]:
        """Send multiple alerts."""
        return [self.send(alert) for alert in alerts]


class SlackNotifier(Notifier):
    """
    Slack webhook notifier.

    Sends alerts to Slack channels using incoming webhooks.
    """

    def __init__(
        self,
        webhook_url: str,
        channel: Optional[str] = None,
        username: str = "PM4Py Bot",
        icon_emoji: str = ":warning:",
        enabled: bool = True,
    ):
        super().__init__(enabled)
        self.webhook_url = webhook_url
        self.channel = channel
        self.username = username
        self.icon_emoji = icon_emoji

    def send(self, alert: Alert) -> Dict[str, Any]:
        """Send alert to Slack."""
        if not self.enabled:
            return {"status": "disabled"}

        message = alert.to_slack_message()

        if self.channel:
            message["channel"] = self.channel
        message["username"] = self.username
        message["icon_emoji"] = self.icon_emoji

        try:
            data = json.dumps(message).encode("utf-8")
            req = urllib.request.Request(
                self.webhook_url,
                data=data,
                headers={"Content-Type": "application/json"},
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                response_data = response.read().decode("utf-8")

            return {
                "status": "sent",
                "notifier": "slack",
                "alert_id": alert.id,
                "response": response_data,
            }

        except urllib.error.HTTPError as e:
            return {
                "status": "error",
                "notifier": "slack",
                "alert_id": alert.id,
                "error": str(e),
                "code": e.code,
            }
        except Exception as e:
            return {
                "status": "error",
                "notifier": "slack",
                "alert_id": alert.id,
                "error": str(e),
            }


class JiraNotifier(Notifier):
    """
    Jira REST API notifier.

    Creates and updates Jira issues for alerts.
    """

    def __init__(
        self,
        base_url: str,
        username: str,
        api_token: str,
        project_key: str = "PM4",
        default_assignee: Optional[str] = None,
        enabled: bool = True,
    ):
        super().__init__(enabled)
        self.base_url = base_url.rstrip("/")
        self.auth = (username, api_token)
        self.project_key = project_key
        self.default_assignee = default_assignee

    def send(self, alert: Alert) -> Dict[str, Any]:
        """Create Jira issue for alert."""
        if not self.enabled:
            return {"status": "disabled"}

        payload = alert.to_jira_payload()
        payload["fields"]["project"]["key"] = self.project_key

        if alert.assignee:
            # Try to find user by email or username
            payload["fields"]["assignee"] = {"name": alert.assignee}
        elif self.default_assignee:
            payload["fields"]["assignee"] = {"name": self.default_assignee}

        try:
            import base64

            # Create basic auth header
            credentials = base64.b64encode(
                f"{self.auth[0]}:{self.auth[1]}".encode()
            ).decode()

            headers = {
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/json",
            }

            data = json.dumps(payload).encode("utf-8")
            url = f"{self.base_url}/rest/api/3/issue"

            req = urllib.request.Request(url, data=data, headers=headers, method="POST")

            with urllib.request.urlopen(req, timeout=10) as response:
                response_data = json.loads(response.read().decode("utf-8"))

            return {
                "status": "created",
                "notifier": "jira",
                "alert_id": alert.id,
                "issue_key": response_data.get("key"),
                "issue_id": response_data.get("id"),
            }

        except urllib.error.HTTPError as e:
            try:
                error_body = e.read().decode("utf-8")
            except:
                error_body = str(e)

            return {
                "status": "error",
                "notifier": "jira",
                "alert_id": alert.id,
                "error": error_body,
                "code": e.code,
            }
        except Exception as e:
            return {
                "status": "error",
                "notifier": "jira",
                "alert_id": alert.id,
                "error": str(e),
            }

    def update_issue(self, issue_key: str, transition: str, comment: Optional[str] = None) -> Dict[str, Any]:
        """Update Jira issue status."""
        if not self.enabled:
            return {"status": "disabled"}

        try:
            import base64

            credentials = base64.b64encode(
                f"{self.auth[0]}:{self.auth[1]}".encode()
            ).decode()

            headers = {
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/json",
            }

            # Get transitions
            url = f"{self.base_url}/rest/api/3/issue/{issue_key}/transitions"
            req = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(req, timeout=10) as response:
                transitions_data = json.loads(response.read().decode("utf-8"))

            # Find transition ID
            transition_id = None
            for t in transitions_data.get("transitions", []):
                if t["name"].lower() == transition.lower():
                    transition_id = t["id"]
                    break

            if not transition_id:
                return {"status": "error", "error": f"Transition '{transition}' not found"}

            # Execute transition
            transition_payload = {"transition": {"id": transition_id}}
            if comment:
                transition_payload["update"] = {
                    "comment": [{"add": {"body": comment}}]
                }

            data = json.dumps(transition_payload).encode("utf-8")
            url = f"{self.base_url}/rest/api/3/issue/{issue_key}/transitions"

            req = urllib.request.Request(url, data=data, headers=headers, method="POST")

            with urllib.request.urlopen(req, timeout=10) as response:
                return {"status": "updated", "issue_key": issue_key}

        except Exception as e:
            return {"status": "error", "error": str(e)}


class PagerDutyNotifier(Notifier):
    """
    PagerDuty Events API v2 notifier.

    Sends alerts to PagerDuty for on-call notification.
    """

    def __init__(
        self,
        integration_key: str,
        api_key: Optional[str] = None,
        enabled: bool = True,
    ):
        super().__init__(enabled)
        self.integration_key = integration_key
        self.api_key = api_key
        self.events_url = "https://events.pagerduty.com/v2/enqueue"

    def send(self, alert: Alert) -> Dict[str, Any]:
        """Send event to PagerDuty."""
        if not self.enabled:
            return {"status": "disabled"}

        payload = alert.to_pagerduty_event()
        payload["routing_key"] = self.integration_key

        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                self.events_url,
                data=data,
                headers={"Content-Type": "application/json"},
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                response_data = json.loads(response.read().decode("utf-8"))

            return {
                "status": "sent",
                "notifier": "pagerduty",
                "alert_id": alert.id,
                "dedup_key": response_data.get("dedup_key"),
            }

        except urllib.error.HTTPError as e:
            try:
                error_body = e.read().decode("utf-8")
            except:
                error_body = str(e)

            return {
                "status": "error",
                "notifier": "pagerduty",
                "alert_id": alert.id,
                "error": error_body,
                "code": e.code,
            }
        except Exception as e:
            return {
                "status": "error",
                "notifier": "pagerduty",
                "alert_id": alert.id,
                "error": str(e),
            }

    def resolve(self, dedup_key: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Resolve a PagerDuty incident."""
        if not self.enabled:
            return {"status": "disabled"}

        payload = {
            "routing_key": self.integration_key,
            "event_action": "resolve",
            "dedup_key": dedup_key,
        }

        if description:
            payload["payload"] = {
                "summary": description,
            }

        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                self.events_url,
                data=data,
                headers={"Content-Type": "application/json"},
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                return {"status": "resolved", "dedup_key": dedup_key}

        except Exception as e:
            return {"status": "error", "error": str(e)}


class EmailNotifier(Notifier):
    """
    Email (SMTP) notifier.

    Sends alerts via email.
    """

    def __init__(
        self,
        smtp_server: str,
        username: str,
        password: str,
        from_address: str,
        smtp_port: int = 587,
        use_tls: bool = True,
        enabled: bool = True,
    ):
        super().__init__(enabled)
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_address = from_address
        self.use_tls = use_tls

    def send(
        self,
        alert: Alert,
        to_addresses: List[str],
        subject_prefix: str = "[PM4Py Alert]",
    ) -> Dict[str, Any]:
        """Send alert via email."""
        if not self.enabled:
            return {"status": "disabled"}

        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"{subject_prefix} [{alert.severity.value.upper()}] {alert.title}"
        msg["From"] = self.from_address
        msg["To"] = ", ".join(to_addresses)

        # Build email body
        severity_icon = {
            AlertSeverity.CRITICAL: "🔴",
            AlertSeverity.HIGH: "🟠",
            AlertSeverity.MEDIUM: "🟡",
            AlertSeverity.LOW: "🟢",
            AlertSeverity.INFO: "🔵",
        }

        html_body = f"""
        <html>
        <body>
            <h2>{severity_icon.get(alert.severity, '⚪')} {alert.title}</h2>
            <p><strong>Severity:</strong> {alert.severity.value.upper()}</p>
            <p><strong>Category:</strong> {alert.category.value}</p>
            <p><strong>Source:</strong> {alert.source}</p>
            <p><strong>Time:</strong> {alert.timestamp.isoformat()}</p>
            <hr>
            <p>{alert.description}</p>
        """

        if alert.metadata:
            html_body += "<h3>Details</h3><ul>"
            for key, value in alert.metadata.items():
                html_body += f"<li><strong>{key}:</strong> {value}</li>"
            html_body += "</ul>"

        html_body += """
        </body>
        </html>
        """

        html_part = MIMEText(html_body, "html")
        msg.attach(html_part)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            return {
                "status": "sent",
                "notifier": "email",
                "alert_id": alert.id,
                "recipients": to_addresses,
            }

        except Exception as e:
            return {
                "status": "error",
                "notifier": "email",
                "alert_id": alert.id,
                "error": str(e),
            }


class AlertManager:
    """
    Central alert manager with routing rules and throttling.

    Routes alerts to appropriate notifiers based on severity and category.
    """

    def __init__(
        self,
        notifiers: Optional[List[Notifier]] = None,
        throttle_seconds: int = 300,  # 5 minutes
        max_alerts_per_hour: int = 100,
    ):
        self.notifiers = notifiers or []
        self.throttle_seconds = throttle_seconds
        self.max_alerts_per_hour = max_alerts_per_hour
        self._alert_history: Dict[str, datetime] = {}
        self._hourly_count = 0
        self._hourly_reset = datetime.utcnow()

    def add_notifier(self, notifier: Notifier):
        """Add a notifier to the manager."""
        self.notifiers.append(notifier)

    def send_alert(self, alert: Alert) -> Dict[str, Any]:
        """Send alert through all configured notifiers."""
        # Check throttling
        now = datetime.utcnow()

        # Reset hourly counter
        if (now - self._hourly_reset).seconds >= 3600:
            self._hourly_count = 0
            self._hourly_reset = now

        # Check rate limit
        if self._hourly_count >= self.max_alerts_per_hour:
            return {
                "status": "throttled",
                "alert_id": alert.id,
                "reason": "max_alerts_per_hour exceeded",
            }

        # Check deduplication
        alert_key = f"{alert.category.value}:{alert.title}"
        if alert_key in self._alert_history:
            last_sent = self._alert_history[alert_key]
            if (now - last_sent).seconds < self.throttle_seconds:
                return {
                    "status": "throttled",
                    "alert_id": alert.id,
                    "reason": "duplicate alert within throttle window",
                }

        # Route based on severity
        results = []
        for notifier in self.notifiers:
            # Skip lower severity alerts for some notifiers
            if isinstance(notifier, PagerDutyNotifier) and alert.severity not in [
                AlertSeverity.CRITICAL, AlertSeverity.HIGH
            ]:
                continue

            result = notifier.send(alert)
            results.append(result)

        # Update history
        self._alert_history[alert_key] = now
        self._hourly_count += 1

        return {
            "status": "sent",
            "alert_id": alert.id,
            "notifiers": results,
        }

    def send_alert_batch(self, alerts: List[Alert]) -> List[Dict[str, Any]]:
        """Send multiple alerts."""
        return [self.send_alert(alert) for alert in alerts]

    def create_alert(
        self,
        title: str,
        description: str,
        severity: AlertSeverity = AlertSeverity.MEDIUM,
        category: AlertCategory = AlertCategory.SYSTEM,
        **kwargs,
    ) -> Alert:
        """Create and optionally send an alert."""
        import uuid

        alert = Alert(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            severity=severity,
            category=category,
            **kwargs,
        )

        return alert


# Convenience functions
def send_slack_alert(
    webhook_url: str,
    title: str,
    description: str,
    severity: AlertSeverity = AlertSeverity.MEDIUM,
    **kwargs,
) -> Dict[str, Any]:
    """Quick Slack alert."""
    notifier = SlackNotifier(webhook_url=webhook_url)
    manager = AlertManager(notifiers=[notifier])

    alert = manager.create_alert(
        title=title,
        description=description,
        severity=severity,
        **kwargs,
    )

    return manager.send_alert(alert)


def send_jira_alert(
    base_url: str,
    username: str,
    api_token: str,
    title: str,
    description: str,
    severity: AlertSeverity = AlertSeverity.MEDIUM,
    **kwargs,
) -> Dict[str, Any]:
    """Quick Jira alert."""
    notifier = JiraNotifier(
        base_url=base_url,
        username=username,
        api_token=api_token,
    )
    manager = AlertManager(notifiers=[notifier])

    alert = manager.create_alert(
        title=title,
        description=description,
        severity=severity,
        **kwargs,
    )

    return manager.send_alert(alert)


__all__ = [
    'AlertSeverity',
    'AlertCategory',
    'Alert',
    'Notifier',
    'SlackNotifier',
    'JiraNotifier',
    'PagerDutyNotifier',
    'EmailNotifier',
    'AlertManager',
    'send_slack_alert',
    'send_jira_alert',
]
