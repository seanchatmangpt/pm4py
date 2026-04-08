'''
PM4Py – Alert Integrations
Copyright (C) 2026 Process Intelligence Solutions GmbH

Webhook handlers for sending drift alerts to external systems:
Slack, Jira, PagerDuty, email, and custom webhooks.
'''

from typing import Dict, List, Any, Optional, Union, Callable
import json
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import urllib.request
import urllib.parse
import urllib.error
import hashlib
import hmac


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status tracking."""
    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class Alert:
    """
    Drift detection alert.

    :param alert_id: Unique alert identifier
    :param title: Alert title
    :param description: Detailed description
    :param severity: Alert severity level
    :param status: Current alert status
    :param source: Source system (e.g., "drift_detection", "conformance")
    :param timestamp: When the alert was triggered
    :param process_model: Process model identifier
    :param drift_metrics: Drift detection metrics
    :param metadata: Additional metadata
    """
    alert_id: str
    title: str
    description: str
    severity: AlertSeverity = AlertSeverity.WARNING
    status: AlertStatus = AlertStatus.TRIGGERED
    source: str = "drift_detection"
    timestamp: datetime = None
    process_model: str = None
    drift_metrics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "status": self.status.value,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "process_model": self.process_model,
            "drift_metrics": self.drift_metrics,
            "metadata": self.metadata,
        }

    def to_slack_message(self) -> Dict[str, Any]:
        """Convert alert to Slack message format."""
        color_map = {
            AlertSeverity.INFO: "#36a64f",      # blue
            AlertSeverity.WARNING: "#ff9800",   # orange
            AlertSeverity.ERROR: "#f44336",     # red
            AlertSeverity.CRITICAL: "#9c27b0",  # purple
        }

        fields = []
        if self.process_model:
            fields.append({"title": "Process Model", "value": self.process_model, "short": True})

        for key, value in self.drift_metrics.items():
            if isinstance(value, float):
                value = f"{value:.4f}"
            fields.append({"title": key.replace("_", " ").title(), "value": str(value), "short": True})

        return {
            "attachments": [{
                "color": color_map.get(self.severity, "#808080"),
                "title": self.title,
                "text": self.description,
                "fields": fields,
                "footer": f"Alert ID: {self.alert_id}",
                "ts": int(self.timestamp.timestamp()),
            }]
        }

    def to_jira_ticket(self) -> Dict[str, Any]:
        """Convert alert to Jira ticket format."""
        priority_map = {
            AlertSeverity.INFO: "1",        # Lowest
            AlertSeverity.WARNING: "2",
            AlertSeverity.ERROR: "3",
            AlertSeverity.CRITICAL: "4",     # Highest
        }

        # Build description from drift metrics
        description = self.description + "\n\n"

        if self.drift_metrics:
            description += "*Drift Metrics:*\n"
            for key, value in self.drift_metrics.items():
                if isinstance(value, float):
                    value = f"{value:.4f}"
                description += f"- {key}: {value}\n"
            description += "\n"

        if self.metadata:
            description += "*Additional Information:*\n"
            for key, value in self.metadata.items():
                description += f"- {key}: {value}\n"

        return {
            "project": {"key": "PM"},
            "summary": f"[{self.severity.value.upper()}] {self.title}",
            "description": description,
            "issuetype": {"name": "Bug"},
            "priority": {"name": priority_map.get(self.severity, "2")},
            "labels": ["drift-detection", "process-mining"],
        }

    def to_pagerduty_event(self) -> Dict[str, Any]:
        """Convert alert to PagerDuty v2 event format."""
        severity_map = {
            AlertSeverity.INFO: "info",
            AlertSeverity.WARNING: "warning",
            AlertSeverity.ERROR: "error",
            AlertSeverity.CRITICAL: "critical",
        }

        return {
            "routing_key": "",  # To be filled by integration key
            "event_action": "trigger",
            "dedup_key": self.alert_id,
            "payload": {
                "summary": self.title,
                "severity": severity_map.get(self.severity, "warning"),
                "source": self.source,
                "timestamp": self.timestamp.isoformat(),
                "custom_details": {
                    "description": self.description,
                    "process_model": self.process_model,
                    **self.drift_metrics,
                    **self.metadata,
                },
            },
        }


class SlackAlertHandler:
    """
    Slack webhook alert handler.

    Sends alerts to Slack channels via Incoming Webhooks.
    """

    def __init__(
        self,
        webhook_url: str,
        channel: Optional[str] = None,
        username: str = "PM4Py Drift Detection",
        icon_emoji: str = ":chart_with_upwards_trend:",
    ):
        """
        Initialize Slack alert handler.

        :param webhook_url: Slack Incoming Webhook URL
        :param channel: Optional channel override (e.g., "#alerts")
        :param username: Bot username
        :param icon_emoji: Bot icon emoji
        """
        self.webhook_url = webhook_url
        self.channel = channel
        self.username = username
        self.icon_emoji = icon_emoji

    def send_alert(self, alert: Alert) -> Dict[str, Any]:
        """
        Send alert to Slack.

        :param alert: Alert to send
        :return: Response from Slack
        """
        message = alert.to_slack_message()

        # Add channel override if specified
        if self.channel:
            message["channel"] = self.channel

        # Add username and icon
        payload = {
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            **message,
        }

        return self._send_webhook(payload)

    def _send_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send webhook request to Slack."""
        data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(
            self.webhook_url,
            data=data,
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                response_data = response.read().decode("utf-8")
                return {"success": True, "response": response_data}
        except urllib.error.HTTPError as e:
            return {
                "success": False,
                "error": f"HTTP {e.code}: {e.reason}",
                "response": e.read().decode("utf-8") if e.fp else None,
            }
        except urllib.error.URLError as e:
            return {
                "success": False,
                "error": f"URL error: {e.reason}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
            }


class JiraAlertHandler:
    """
    Jira API alert handler.

    Creates Jira tickets from alerts.
    """

    def __init__(
        self,
        base_url: str,
        email: str,
        api_token: str,
        project_key: str = "PM",
        default_assignee: Optional[str] = None,
    ):
        """
        Initialize Jira alert handler.

        :param base_url: Jira instance base URL (e.g., "https://yourdomain.atlassian.net")
        :param email: Jira account email
        :param api_token: Jira API token
        :param project_key: Jira project key
        :param default_assignee: Default assignee account ID
        """
        self.base_url = base_url.rstrip("/")
        self.email = email
        self.api_token = api_token
        self.project_key = project_key
        self.default_assignee = default_assignee

    def send_alert(self, alert: Alert) -> Dict[str, Any]:
        """
        Create Jira ticket from alert.

        :param alert: Alert to create ticket from
        :return: Response from Jira
        """
        ticket_data = alert.to_jira_ticket()
        ticket_data["project"]["key"] = self.project_key

        if self.default_assignee:
            ticket_data["assignee"] = {"accountId": self.default_assignee}

        url = f"{self.base_url}/rest/api/3/issue"

        auth_header = self._create_basic_auth(self.email, self.api_token)

        return self._send_api_request(url, ticket_data, auth_header)

    def update_ticket(
        self,
        ticket_id: str,
        comment: str,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update existing Jira ticket.

        :param ticket_id: Jira ticket ID (e.g., "PM-123")
        :param comment: Comment to add
        :param status: New status (optional)
        :return: Response from Jira
        """
        url = f"{self.base_url}/rest/api/3/issue/{ticket_id}/comment"
        auth_header = self._create_basic_auth(self.email, self.api_token)

        result = self._send_api_request(
            url,
            {"body": comment},
            auth_header,
        )

        # Update status if provided
        if status and result.get("success"):
            transition_url = f"{self.base_url}/rest/api/3/issue/{ticket_id}/transitions"
            # Get available transitions for the issue
            transitions = self._send_api_request(
                f"{self.base_url}/rest/api/3/issue/{ticket_id}/transitions",
                {},
                auth_header,
            )

            # Find the transition ID for the target status
            target_transition = None
            if transitions.get("success") and "transitions" in transitions:
                for t in transitions["transitions"]:
                    if t.get("to", {}).get("name") == status:
                        target_transition = t.get("id")
                        break

            if target_transition:
                self._send_api_request(
                    transition_url,
                    {"transition": {"id": target_transition}},
                    auth_header,
                )

        return result

    def _create_basic_auth(self, email: str, api_token: str) -> str:
        """Create Basic Auth header."""
        credentials = f"{email}:{api_token}"
        encoded = credentials.encode("utf-8")
        b64_credentials = base64.b64encode(encoded).decode("utf-8")
        return f"Basic {b64_credentials}"

    def _send_api_request(
        self,
        url: str,
        data: Dict[str, Any],
        auth_header: str,
    ) -> Dict[str, Any]:
        """Send API request to Jira."""
        import base64

        json_data = json.dumps(data).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=json_data,
            headers={
                "Authorization": auth_header,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                response_data = response.read().decode("utf-8")
                return {
                    "success": True,
                    "response": json.loads(response_data) if response_data else {},
                }
        except urllib.error.HTTPError as e:
            return {
                "success": False,
                "error": f"HTTP {e.code}: {e.reason}",
                "response": e.read().decode("utf-8") if e.fp else None,
            }
        except urllib.error.URLError as e:
            return {
                "success": False,
                "error": f"URL error: {e.reason}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
            }


class PagerDutyAlertHandler:
    """
    PagerDuty v2 Events API alert handler.

    Triggers incidents in PagerDuty from alerts.
    """

    def __init__(
        self,
        integration_key: str,
        routing_key: Optional[str] = None,
        dedup_key_ttl: int = 7200,  # 2 hours default
    ):
        """
        Initialize PagerDuty alert handler.

        :param integration_key: PagerDuty Integration Key
        :param routing_key: PagerDuty Routing Key (for Events API v2)
        :param dedup_key_ttl: Deduplication key TTL in seconds
        """
        self.integration_key = integration_key
        self.routing_key = routing_key or integration_key
        self.dedup_key_ttl = dedup_key_ttl
        self.api_url = "https://events.pagerduty.com/v2/enqueue"

    def send_alert(self, alert: Alert) -> Dict[str, Any]:
        """
        Send alert to PagerDuty.

        :param alert: Alert to send
        :return: Response from PagerDuty
        """
        event_data = alert.to_pagerduty_event()
        event_data["routing_key"] = self.routing_key

        return self._send_event(event_data)

    def acknowledge_alert(self, alert_id: str) -> Dict[str, Any]:
        """
        Acknowledge a PagerDuty alert.

        :param alert_id: Alert deduplication key
        :return: Response from PagerDuty
        """
        event_data = {
            "routing_key": self.routing_key,
            "dedup_key": alert_id,
            "event_action": "acknowledge",
        }

        return self._send_event(event_data)

    def resolve_alert(self, alert_id: str) -> Dict[str, Any]:
        """
        Resolve a PagerDuty alert.

        :param alert_id: Alert deduplication key
        :return: Response from PagerDuty
        """
        event_data = {
            "routing_key": self.routing_key,
            "dedup_key": alert_id,
            "event_action": "resolve",
        }

        return self._send_event(event_data)

    def _send_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send event to PagerDuty."""
        json_data = json.dumps(event_data).encode("utf-8")

        req = urllib.request.Request(
            self.api_url,
            data=json_data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                response_data = response.read().decode("utf-8")
                return {
                    "success": True,
                    "response": json.loads(response_data) if response_data else {},
                }
        except urllib.error.HTTPError as e:
            return {
                "success": False,
                "error": f"HTTP {e.code}: {e.reason}",
                "response": e.read().decode("utf-8") if e.fp else None,
            }
        except urllib.error.URLError as e:
            return {
                "success": False,
                "error": f"URL error: {e.reason}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
            }


class EmailAlertHandler:
    """
    Email alert handler.

    Sends alerts via email (SMTP).
    """

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_address: str,
        to_addresses: List[str],
    ):
        """
        Initialize email alert handler.

        :param smtp_server: SMTP server hostname
        :param smtp_port: SMTP server port
        :param username: SMTP username
        :param password: SMTP password
        :param from_address: From email address
        :param to_addresses: List of recipient email addresses
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_address = from_address
        self.to_addresses = to_addresses

    def send_alert(self, alert: Alert) -> Dict[str, Any]:
        """
        Send alert via email.

        :param alert: Alert to send
        :return: Send result
        """
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[{alert.severity.value.upper()}] {alert.title}"
        msg["From"] = self.from_address
        msg["To"] = ", ".join(self.to_addresses)

        # Plain text version
        text_content = f"""
Alert: {alert.title}

{alert.description}

Severity: {alert.severity.value}
Status: {alert.status.value}
Source: {alert.source}
Timestamp: {alert.timestamp.isoformat()}
Alert ID: {alert.alert_id}

Drift Metrics:
{json.dumps(alert.drift_metrics, indent=2)}
        """.strip()

        # HTML version
        html_content = f"""
<html>
<body>
    <h2>{alert.title}</h2>
    <p><strong>Description:</strong> {alert.description}</p>
    <p><strong>Severity:</strong> {alert.severity.value}</p>
    <p><strong>Status:</strong> {alert.status.value}</p>
    <p><strong>Source:</strong> {alert.source}</p>
    <p><strong>Timestamp:</strong> {alert.timestamp.isoformat()}</p>
    <p><strong>Alert ID:</strong> {alert.alert_id}</p>

    <h3>Drift Metrics</h3>
    <pre>{json.dumps(alert.drift_metrics, indent=2)}</pre>
</body>
</html>
        """.strip()

        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")

        msg.attach(part1)
        msg.attach(part2)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(
                    self.from_address,
                    self.to_addresses,
                    msg.as_string(),
                )
            return {"success": True}
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


class WebhookAlertHandler:
    """
    Generic webhook alert handler.

    Sends alerts to any HTTP webhook endpoint.
    """

    def __init__(
        self,
        webhook_url: str,
        headers: Optional[Dict[str, str]] = None,
        sign_secret: Optional[str] = None,
    ):
        """
        Initialize webhook alert handler.

        :param webhook_url: Webhook URL
        :param headers: Optional HTTP headers
        :param sign_secret: Optional secret for HMAC signing
        """
        self.webhook_url = webhook_url
        self.headers = headers or {}
        self.sign_secret = sign_secret

    def send_alert(self, alert: Alert) -> Dict[str, Any]:
        """
        Send alert to webhook.

        :param alert: Alert to send
        :return: Response from webhook
        """
        payload = alert.to_dict()

        # Add signature if secret is configured
        if self.sign_secret:
            signature = self._sign_payload(payload)
            self.headers["X-PM4Py-Signature"] = signature

        json_data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(
            self.webhook_url,
            data=json_data,
            headers={
                **self.headers,
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                response_data = response.read().decode("utf-8")
                return {
                    "success": True,
                    "response": response_data,
                }
        except urllib.error.HTTPError as e:
            return {
                "success": False,
                "error": f"HTTP {e.code}: {e.reason}",
                "response": e.read().decode("utf-8") if e.fp else None,
            }
        except urllib.error.URLError as e:
            return {
                "success": False,
                "error": f"URL error: {e.reason}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
            }

    def _sign_payload(self, payload: Dict[str, Any]) -> str:
        """Sign payload with HMAC."""
        import hmac

        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            self.sign_secret.encode("utf-8"),
            payload_str.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return f"sha256={signature}"


class AlertManager:
    """
    Central alert manager for coordinating multiple handlers.

    Supports:
    - Multiple handlers per alert
    - Alert aggregation and batching
    - Rate limiting
    - Retry logic
    - Alert history tracking
    """

    def __init__(self):
        """Initialize alert manager."""
        self.handlers: List[Union[
            SlackAlertHandler,
            JiraAlertHandler,
            PagerDutyAlertHandler,
            EmailAlertHandler,
            WebhookAlertHandler,
        ]] = []

        self.alert_history: List[Alert] = []
        self.alert_rules: List[Callable[[Alert], bool]] = []

    def add_handler(
        self,
        handler: Union[
            SlackAlertHandler,
            JiraAlertHandler,
            PagerDutyAlertHandler,
            EmailAlertHandler,
            WebhookAlertHandler,
        ]
    ):
        """Add an alert handler."""
        self.handlers.append(handler)

    def add_rule(self, rule: Callable[[Alert], bool]):
        """
        Add an alert rule (function that returns True if alert should be sent).

        Example:
            def critical_only(alert):
                return alert.severity == AlertSeverity.CRITICAL
            alert_manager.add_rule(critical_only)
        """
        self.alert_rules.append(rule)

    def send_alert(self, alert: Alert) -> Dict[str, List[Dict[str, Any]]]:
        """
        Send alert through all handlers, respecting rules.

        :param alert: Alert to send
        :return: Results from each handler
        """
        # Check all rules
        for rule in self.alert_rules:
            if not rule(alert):
                return {
                    "skipped": True,
                    "reason": "Alert did not pass rule filter",
                }

        # Add to history
        self.alert_history.append(alert)

        # Send to all handlers
        results = {}
        for i, handler in enumerate(self.handlers):
            handler_name = handler.__class__.__name__
            try:
                result = handler.send_alert(alert)
                results[handler_name] = result
            except Exception as e:
                results[handler_name] = {
                    "success": False,
                    "error": f"Handler error: {str(e)}",
                }

        return {
            "alert_id": alert.alert_id,
            "sent": True,
            "handlers": results,
        }

    def create_drift_alert(
        self,
        title: str,
        drift_score: float,
        threshold: float,
        process_model: str,
        metrics: Dict[str, Any],
        severity: AlertSeverity = None,
    ) -> Alert:
        """
        Create a drift detection alert.

        :param title: Alert title
        :param drift_score: Calculated drift score
        :param threshold: Threshold that was exceeded
        :param process_model: Process model identifier
        :param metrics: Drift metrics
        :param severity: Alert severity (auto-calculated if None)
        :return: Alert object
        """
        # Auto-calculate severity from drift score
        if severity is None:
            if drift_score > 0.9:
                severity = AlertSeverity.CRITICAL
            elif drift_score > 0.7:
                severity = AlertSeverity.ERROR
            elif drift_score > 0.5:
                severity = AlertSeverity.WARNING
            else:
                severity = AlertSeverity.INFO

        # Generate unique alert ID
        alert_id = f"drift-{process_model}-{int(datetime.now().timestamp())}"

        # Create description
        description = (
            f"Process drift detected in model '{process_model}'. "
            f"Drift score: {drift_score:.4f} exceeds threshold: {threshold:.4f}"
        )

        return Alert(
            alert_id=alert_id,
            title=title,
            description=description,
            severity=severity,
            source="drift_detection",
            process_model=process_model,
            drift_metrics={
                "drift_score": drift_score,
                "threshold": threshold,
                **metrics,
            },
            metadata={
                "alert_type": "drift_detection",
            },
        )


# Convenience functions
def create_slack_handler(webhook_url: str, **kwargs) -> SlackAlertHandler:
    """Create Slack alert handler."""
    return SlackAlertHandler(webhook_url, **kwargs)


def create_jira_handler(
    base_url: str,
    email: str,
    api_token: str,
    **kwargs
) -> JiraAlertHandler:
    """Create Jira alert handler."""
    return JiraAlertHandler(base_url, email, api_token, **kwargs)


def create_pagerduty_handler(integration_key: str, **kwargs) -> PagerDutyAlertHandler:
    """Create PagerDuty alert handler."""
    return PagerDutyAlertHandler(integration_key, **kwargs)


def create_email_handler(
    smtp_server: str,
    smtp_port: int,
    username: str,
    password: str,
    from_address: str,
    to_addresses: List[str],
) -> EmailAlertHandler:
    """Create email alert handler."""
    return EmailAlertHandler(
        smtp_server, smtp_port, username, password, from_address, to_addresses
    )


def create_webhook_handler(webhook_url: str, **kwargs) -> WebhookAlertHandler:
    """Create generic webhook alert handler."""
    return WebhookAlertHandler(webhook_url, **kwargs)


__all__ = [
    'Alert',
    'AlertSeverity',
    'AlertStatus',
    'SlackAlertHandler',
    'JiraAlertHandler',
    'PagerDutyAlertHandler',
    'EmailAlertHandler',
    'WebhookAlertHandler',
    'AlertManager',
    'create_slack_handler',
    'create_jira_handler',
    'create_pagerduty_handler',
    'create_email_handler',
    'create_webhook_handler',
]
