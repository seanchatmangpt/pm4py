'''
PM4Py – Finance Schemas
Copyright (C) 2026 Process Intelligence Solutions GmbH

Trade workflow event schemas and SOC2 compliance attributes.
'''

from typing import Dict, List, Any, Set
from dataclasses import dataclass, field
from enum import Enum


class MarketType(Enum):
    """Financial market types."""
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    LSE = "London Stock Exchange"
    FX = "Foreign Exchange"
    CRYPTO = "Cryptocurrency"
    DERIVATIVES = "Derivatives"
    COMMODITIES = "Commodities"


class TradeType(Enum):
    """Trade execution types."""
    MARKET = "Market Order"
    LIMIT = "Limit Order"
    STOP = "Stop Order"
    STOP_LIMIT = "Stop Limit"
    ICEBERG = "Iceberg"
    ALGORITHM = "Algorithmic"


class AssetClass(Enum):
    """Financial asset classes."""
    EQUITY = "Equity"
    FIXED_INCOME = "Fixed Income"
    DERIVATIVE = "Derivative"
    FX = "Foreign Exchange"
    COMMODITY = "Commodity"
    CRYPTO = "Cryptocurrency"


# SOC2 Required Attributes (Trust Services Criteria)
SOC2_REQUIRED_ATTRIBUTES = {
    "soc2:access_control": {
        "description": "Access control mechanism (CC6.1)",
        "required": True,
        "data_type": "string",
        "allowed_values": ["MFA", "RBAC", "SAML", "LDAP"],
    },
    "soc2:encryption": {
        "description": "Data encryption at rest and in transit (CC6.1)",
        "required": True,
        "data_type": "boolean",
    },
    "soc2:audit_log": {
        "description": "Complete audit trail (CC6.6)",
        "required": True,
        "data_type": "list",
        "validation": lambda x: isinstance(x, list) and len(x) > 0,
    },
    "soc2:change_management": {
        "description": "Change management record (CC6.7)",
        "required": True,
        "data_type": "string",
    },
    "soc2:incident_response": {
        "description": "Incident response procedure (CC6.8)",
        "required": False,
        "data_type": "string",
    },
    "soc2:data_classification": {
        "description": "Data classification level (CC6.1)",
        "required": True,
        "data_type": "string",
        "allowed_values": ["public", "internal", "confidential", "restricted"],
    },
    "soc2:compliance_monitoring": {
        "description": "Continuous compliance monitoring (CC3.6)",
        "required": True,
        "data_type": "boolean",
    },
}


# Regulatory Reporting Attributes (MiFID II, Reg NMS, etc.)
REGULATORY_REPORTING_ATTRIBUTES = {
    "reg:transaction_id": {
        "description": "Unique transaction identifier (MiFID II)",
        "required": True,
        "data_type": "string",
    },
    "reg:execution_timestamp": {
        "description": "Execution timestamp with microseconds (Reg NMS)",
        "required": True,
        "data_type": "datetime",
    },
    "reg:venue": {
        "description": "Transaction revenue (MiFID II)",
        "required": True,
        "data_type": "numeric",
    },
    "reg:venue_currency": {
        "description": "Currency for revenue field",
        "required": True,
        "data_type": "string",
    },
    "reg:venue_calculation_method": {
        "description": "Revenue calculation method (MiFID II)",
        "required": True,
        "data_type": "string",
        "allowed_values": ["mark_to_market", "accrual", "cash", "estimation"],
    },
    "reg:venue_share_details": {
        "description": "Revenue sharing with third parties (MiFID II)",
        "required": False,
        "data_type": "object",
    },
    "reg:best_execution": {
        "description": "Best execution policy (MiFID II Article 27)",
        "required": True,
        "data_type": "boolean",
    },
    "reg:venue_share_indicators": {
        "description": "Indicators of revenue sharing arrangements (MiFID II)",
        "required": True,
        "data_type": "boolean",
    },
    "reg:execution_venue": {
        "description": "Venue where trade was executed (MiFID II)",
        "required": True,
        "data_type": "string",
    },
    "reg:short_selling_indicator": {
        "description": "Short selling indicator (MiFIR)",
        "required": True,
        "data_type": "boolean",
    },
}


# Trade Workflow Event Schema
TRADE_WORKFLOW_SCHEMA = {
    "event_level": {
        # Core XES attributes
        "concept:name": {
            "type": "string",
            "description": "Activity name",
            "required": True,
        },
        "time:timestamp": {
            "type": "datetime",
            "description": "Event timestamp (with microseconds for regulatory)",
            "required": True,
        },
        "lifecycle:transition": {
            "type": "string",
            "description": "Lifecycle state",
            "allowed_values": ["start", "complete", "suspend", "resume"],
            "default": "complete",
        },

        # Trade identification
        "trade:Id": {
            "type": "string",
            "description": "Unique trade identifier",
            "required": True,
        },
        "trade:instrument": {
            "type": "string",
            "description": "Financial instrument (ticker, ISIN)",
            "required": True,
        },
        "trade:asset_class": {
            "type": "string",
            "description": "Asset class",
            "allowed_values": [a.value for a in AssetClass],
        },
        "trade:type": {
            "type": "string",
            "description": "Order/trade type",
            "allowed_values": [t.value for t in TradeType],
        },
        "trade:side": {
            "type": "string",
            "description": "Trade direction",
            "allowed_values": ["BUY", "SELL", "SHORT"],
        },
        "trade:quantity": {
            "type": "numeric",
            "description": "Quantity/shares",
        },
        "trade:price": {
            "type": "numeric",
            "description": "Execution price",
        },
        "trade:notional": {
            "type": "numeric",
            "description": "Notional value (quantity * price)",
        },

        # Case/Order identification
        "case:concept:name": {
            "type": "string",
            "description": "Order/Case ID",
            "required": True,
        },

        # Organizational attributes
        "org:trader": {
            "type": "string",
            "description": "Trader ID (not name)",
        },
        "org:desk": {
            "type": "string",
            "description": "Trading desk",
            "allowed_values": [
                "Equities",
                "Fixed Income",
                "FX",
                "Commodities",
                "Derivatives",
                "Crypto",
            ],
        },
        "org:approver": {
            "type": "string",
            "description": "Approver ID",
        },

        # Client/Counterparty
        "client:Id": {
            "type": "string",
            "description": "Client identifier",
        },
        "counterparty:Id": {
            "type": "string",
            "description": "Counterparty identifier",
        },

        # Risk attributes
        "risk:limit_check": {
            "type": "boolean",
            "description": "Whether limit check passed",
        },
        "risk:limit_breach": {
            "type": "boolean",
            "description": "Whether limit was breached",
        },
        "risk:var_contribution": {
            "type": "numeric",
            "description": "Value at Risk contribution",
        },

        # Compliance attributes
        "compliance:pre_trade_check": {
            "type": "boolean",
            "description": "Pre-trade compliance check result",
        },
        "compliance:post_trade_verify": {
            "type": "boolean",
            "description": "Post-trade verification result",
        },
        "compliance:surveillance_flag": {
            "type": "boolean",
            "description": "Surveillance system flag",
        },

        # Market attributes
        "market:venue": {
            "type": "string",
            "description": "Execution venue",
            "allowed_values": [m.value for m in MarketType],
        },
        "market:session": {
            "type": "string",
            "description": "Trading session",
            "allowed_values": ["Pre-market", "Regular", "After-hours", "Overnight"],
        },
    },

    "trace_level": {
        "order:type": {
            "type": "string",
            "description": "Order type",
            "allowed_values": ["Market", "Limit", "Stop", "Stop-Limit", "Trailing Stop"],
        },
        "order:time_in_force": {
            "type": "string",
            "description": "Time in force",
            "allowed_values": ["DAY", "GTC", "IOC", "FOK", "AON"],
        },
        "order:status": {
            "type": "string",
            "description": "Order status",
            "allowed_values": [
                "New",
                "Partial Fill",
                "Filled",
                "Cancelled",
                "Rejected",
                "Expired",
            ],
        },
        "order:average_price": {
            "type": "numeric",
            "description": "Average execution price",
        },
        "order:total_quantity": {
            "type": "numeric",
            "description": "Total order quantity",
        },
        "order:filled_quantity": {
            "type": "numeric",
            "description": "Filled quantity",
        },
        "order:commission": {
            "type": "numeric",
            "description": "Commission amount",
        },
        "order:fees": {
            "type": "numeric",
            "description": "Total fees",
        },
    },
}


# Standard Trade Workflow Activities
TRADE_ACTIVITIES = {
    # Pre-trade
    "order_received": "Order Received from Client",
    "order_validation": "Order Validation",
    "pre_trade_compliance": "Pre-Trade Compliance Check",
    "risk_check": "Risk Management Check",
    "limit_check": "Position Limit Check",
    "credit_check": "Credit Check",

    # Execution
    "order_routing": "Order Routing",
    "order_submission": "Order Submission to Market",
    "price_quotation": "Price Quotation",
    "execution": "Trade Execution",
    "partial_fill": "Partial Fill",
    "fill": "Order Fill",

    # Post-trade
    "trade_confirmation": "Trade Confirmation",
    "post_trade_verification": "Post-Trade Verification",
    "settlement_instruction": "Settlement Instruction",
    "clearing": "Clearing",
    "settlement": "Settlement",
    "custody_transfer": "Custody Transfer",

    # Reporting
    "trade_reporting": "Regulatory Trade Reporting",
    "client_reporting": "Client Reporting",
    "internal_p&l": "Internal P&L Calculation",
    "risk_update": "Risk Position Update",

    # Exceptions
    "order_rejection": "Order Rejection",
    "order_cancellation": "Order Cancellation",
    "order_modification": "Order Modification",
    "break": "Trade Break",
    "bust": "Trade Bust",
}


@dataclass
class TradeEvent:
    """Typed trade event."""

    activity: str
    timestamp: Any
    case_id: str
    trade_id: str
    instrument: str
    side: str = "BUY"
    quantity: float = 0.0
    price: float = 0.0
    trader: str = ""
    desk: str = "Equities"
    venue: str = "NYSE"
    limit_check_passed: bool = True
    compliance_passed: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "concept:name": self.activity,
            "time:timestamp": self.timestamp,
            "case:concept:name": self.case_id,
            "trade:Id": self.trade_id,
            "trade:instrument": self.instrument,
            "trade:side": self.side,
            "trade:quantity": self.quantity,
            "trade:price": self.price,
            "org:trader": self.trader,
            "org:desk": self.desk,
            "market:venue": self.venue,
            "risk:limit_check": self.limit_check_passed,
            "compliance:pre_trade_check": self.compliance_passed,
        }


# Risk Metrics
RISK_METRICS = {
    "value_at_risk": {
        "description": "Value at Risk (VaR)",
        "calculation": "Historical simulation at 95% confidence",
        "threshold": "Alert if daily VaR > 1% of portfolio",
    },
    "concentration_risk": {
        "description": "Concentration risk by instrument/sector",
        "calculation": "Sum of positions / Total portfolio",
        "threshold": "Alert if single position > 10% of portfolio",
    },
    "liquidity_risk": {
        "description": "Liquidity risk (average daily volume)",
        "calculation": "Order quantity / Average daily volume",
        "threshold": "Alert if order > 20% of ADV",
    },
    "leverage_ratio": {
        "description": "Leverage ratio",
        "calculation": "Total exposure / Equity",
        "threshold": "Alert if leverage > 3:1",
    },
    "counterparty_risk": {
        "description": "Counterparty exposure",
        "calculation": "Total exposure to single counterparty",
        "threshold": "Alert if exposure > 5% of capital",
    },
}


def validate_trade_schema(event: Dict[str, Any]) -> List[str]:
    """Validate a trade event against the schema."""
    errors = []
    event_level = TRADE_WORKFLOW_SCHEMA.get("event_level", {})

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


def identify_market_from_instrument(instrument: str) -> str:
    """Identify likely market from instrument symbol."""
    # Simple heuristic mapping
    if len(instrument) <= 5 and instrument.isalpha():
        return MarketType.NYSE.value
    elif "^" in instrument or "-" in instrument:
        return MarketType.DERIVATIVES.value
    elif "/" in instrument:
        return MarketType.FX.value
    else:
        return MarketType.NASDAQ.value


__all__ = [
    'MarketType',
    'TradeType',
    'AssetClass',
    'SOC2_REQUIRED_ATTRIBUTES',
    'REGULATORY_REPORTING_ATTRIBUTES',
    'TRADE_WORKFLOW_SCHEMA',
    'TRADE_ACTIVITIES',
    'TradeEvent',
    'RISK_METRICS',
    'validate_trade_schema',
    'identify_market_from_instrument',
]
