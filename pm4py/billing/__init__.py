"""
PM4Py SaaS Billing System

Handles pricing tiers, usage metering, subscription management,
and billing for the PM4Py cloud platform.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json


class PlanTier(Enum):
    """Subscription plan tiers."""
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class BillingCycle(Enum):
    """Billing cycles."""
    MONTHLY = "monthly"
    ANNUAL = "annual"


class AddOnType(Enum):
    """Available add-ons."""
    DEDICATED_SUPPORT = "dedicated_support"
    ON_PREMISE = "on_premise"
    CUSTOM_VERTICAL = "custom_vertical"
    TRAINING_WORKSHOP = "training_workshop"
    DATA_MIGRATION = "data_migration"


@dataclass
class PlanLimits:
    """Resource limits for a plan."""
    events_per_month: int
    process_models: int
    team_members: int
    storage_gb: int
    ai_requests_per_month: int
    api_calls_per_month: int
    webhooks: int


@dataclass
class PlanFeatures:
    """Features included in a plan."""
    discovery_algorithms: bool
    visualizations: bool
    conformance_checking: bool
    ai_process_design: bool
    verticals: List[str]
    real_time_drift: bool
    api_access: str  # "none", "read_only", "full"
    sso: List[str]  # SSO methods
    support_level: str
    sla_uptime: float
    soc2_reporting: bool


@dataclass
class PlanPricing:
    """Pricing for a plan."""
    monthly_price: int  # in USD
    annual_price: int  # in USD (12 months for price of 10)
    annual_discount: float = 0.17  # 17% discount for annual


@dataclass
class AddOnPricing:
    """Pricing for add-ons."""
    monthly_price: int
    setup_price: int = 0


# Plan definitions
PLAN_LIMITS = {
    PlanTier.STARTER: PlanLimits(
        events_per_month=100_000,
        process_models=10,
        team_members=3,
        storage_gb=5,
        ai_requests_per_month=10,
        api_calls_per_month=10_000,
        webhooks=0,
    ),
    PlanTier.PROFESSIONAL: PlanLimits(
        events_per_month=1_000_000,
        process_models=100,
        team_members=20,
        storage_gb=50,
        ai_requests_per_month=100,
        api_calls_per_month=100_000,
        webhooks=10,
    ),
    PlanTier.ENTERPRISE: PlanLimits(
        events_per_month=float('inf'),
        process_models=float('inf'),
        team_members=float('inf'),
        storage_gb=float('inf'),
        ai_requests_per_month=float('inf'),
        api_calls_per_month=float('inf'),
        webhooks=float('inf'),
    ),
}


PLAN_FEATURES = {
    PlanTier.STARTER: PlanFeatures(
        discovery_algorithms=True,
        visualizations=True,
        conformance_checking=True,
        ai_process_design=True,
        verticals=[],
        real_time_drift=False,
        api_access="read_only",
        sso=[],
        support_level="community",
        sla_uptime=0.0,
        soc2_reporting=False,
    ),
    PlanTier.PROFESSIONAL: PlanFeatures(
        discovery_algorithms=True,
        visualizations=True,
        conformance_checking=True,
        ai_process_design=True,
        verticals=["finance", "healthcare", "manufacturing"],
        real_time_drift=True,
        api_access="full",
        sso=[],
        support_level="email",
        sla_uptime=99.5,
        soc2_reporting=False,
    ),
    PlanTier.ENTERPRISE: PlanFeatures(
        discovery_algorithms=True,
        visualizations=True,
        conformance_checking=True,
        ai_process_design=True,
        verticals=["finance", "healthcare", "manufacturing", "custom"],
        real_time_drift=True,
        api_access="full",
        sso=["saml", "oidc"],
        support_level="dedicated",
        sla_uptime=99.99,
        soc2_reporting=True,
    ),
}


PLAN_PRICING = {
    PlanTier.STARTER: PlanPricing(monthly_price=49, annual_price=490),
    PlanTier.PROFESSIONAL: PlanPricing(monthly_price=199, annual_price=1990),
    PlanTier.ENTERPRISE: PlanPricing(monthly_price=0, annual_price=0),  # Custom pricing
}


ADD_ON_PRICING = {
    AddOnType.DEDICATED_SUPPORT: AddOnPricing(monthly_price=499),
    AddOnType.ON_PREMISE: AddOnPricing(monthly_price=5000, setup_price=25000),
    AddOnType.CUSTOM_VERTICAL: AddOnPricing(monthly_price=500, setup_price=2500),
    AddOnType.TRAINING_WORKSHOP: AddOnPricing(monthly_price=0, setup_price=2500),
    AddOnType.DATA_MIGRATION: AddOnPricing(monthly_price=0, setup_price=1500),
}


@dataclass
class UsageRecord:
    """Usage record for billing."""
    tenant_id: str
    period_start: datetime
    period_end: datetime
    events_processed: int = 0
    process_models_created: int = 0
    ai_requests_made: int = 0
    api_calls_made: int = 0
    storage_used_gb: float = 0.0
    active_webhooks: int = 0


@dataclass
class Subscription:
    """Customer subscription."""
    tenant_id: str
    plan_tier: PlanTier
    billing_cycle: BillingCycle
    start_date: datetime
    next_billing_date: datetime
    add_ons: List[AddOnType] = field(default_factory=list)
    status: str = "active"  # active, canceled, past_due, suspended


@dataclass
class Invoice:
    """Billing invoice."""
    invoice_id: str
    tenant_id: str
    period_start: datetime
    period_end: datetime
    plan_tier: PlanTier
    subtotal: int  # in cents
    add_ons_total: int = 0
    usage_overages: int = 0
    tax: int = 0
    total: int = 0
    status: str = "pending"  # pending, paid, voided
    due_date: Optional[datetime] = None
    paid_date: Optional[datetime] = None


class BillingEngine:
    """
    Billing engine for PM4Py SaaS platform.

    Handles subscription management, usage tracking, overage calculation,
    and invoice generation.
    """

    # Usage-based pricing (per million units)
    EVENT_PRICE_PER_MILLION = 0.50  # USD
    STORAGE_PRICE_PER_GB = 0.10  # USD per GB per month
    API_CALL_PRICE = 0.001  # USD per call
    WEBHOOK_PRICE = 5  # USD per webhook per month

    def __init__(self):
        self.subscriptions: Dict[str, Subscription] = {}
        self.usage_records: Dict[str, List[UsageRecord]] = {}
        self.invoices: Dict[str, List[Invoice]] = {}

    def create_subscription(
        self,
        tenant_id: str,
        plan_tier: PlanTier,
        billing_cycle: BillingCycle = BillingCycle.MONTHLY,
        add_ons: Optional[List[AddOnType]] = None,
    ) -> Subscription:
        """Create a new subscription."""
        now = datetime.utcnow()

        if billing_cycle == BillingCycle.ANNUAL:
            next_billing = now + timedelta(days=365)
        else:
            # Monthly billing - same day next month
            if now.day == 31:
                # Handle months with fewer days
                next_billing = (now.replace(day=1) + timedelta(days=32)).replace(day=1)
            else:
                next_billing = (now.replace(day=1) + timedelta(days=32)).replace(day=now.day)

        subscription = Subscription(
            tenant_id=tenant_id,
            plan_tier=plan_tier,
            billing_cycle=billing_cycle,
            start_date=now,
            next_billing_date=next_billing,
            add_ons=add_ons or [],
        )

        self.subscriptions[tenant_id] = subscription
        return subscription

    def get_subscription(self, tenant_id: str) -> Optional[Subscription]:
        """Get subscription for a tenant."""
        return self.subscriptions.get(tenant_id)

    def record_usage(self, usage: UsageRecord) -> None:
        """Record usage for a tenant."""
        if usage.tenant_id not in self.usage_records:
            self.usage_records[usage.tenant_id] = []
        self.usage_records[usage.tenant_id].append(usage)

    def calculate_overages(
        self,
        subscription: Subscription,
        usage: UsageRecord,
    ) -> Dict[str, Any]:
        """Calculate usage overages and costs."""
        limits = PLAN_LIMITS[subscription.plan_tier]
        overages = {}
        total_cost = 0

        # Events overage
        if usage.events_processed > limits.events_per_month:
            events_over = usage.events_processed - limits.events_per_month
            events_over_millions = events_over / 1_000_000
            cost = events_over_millions * self.EVENT_PRICE_PER_MILLION
            overages['events'] = {
                'limit': limits.events_per_month,
                'used': usage.events_processed,
                'over': events_over,
                'cost': round(cost, 2),
            }
            total_cost += cost

        # Storage overage
        if usage.storage_used_gb > limits.storage_gb:
            storage_over = usage.storage_used_gb - limits.storage_gb
            cost = storage_over * self.STORAGE_PRICE_PER_GB
            overages['storage'] = {
                'limit': limits.storage_gb,
                'used': usage.storage_used_gb,
                'over': storage_over,
                'cost': round(cost, 2),
            }
            total_cost += cost

        # API calls overage
        if usage.api_calls_made > limits.api_calls_per_month:
            api_over = usage.api_calls_made - limits.api_calls_per_month
            cost = api_over * self.API_CALL_PRICE
            overages['api_calls'] = {
                'limit': limits.api_calls_per_month,
                'used': usage.api_calls_made,
                'over': api_over,
                'cost': round(cost, 2),
            }
            total_cost += cost

        # Webhooks overage
        if usage.active_webhooks > limits.webhooks:
            webhooks_over = usage.active_webhooks - limits.webhooks
            cost = webhooks_over * self.WEBHOOK_PRICE
            overages['webhooks'] = {
                'limit': limits.webhooks,
                'used': usage.active_webhooks,
                'over': webhooks_over,
                'cost': round(cost, 2),
            }
            total_cost += cost

        overages['total_cost'] = round(total_cost, 2)
        return overages

    def generate_invoice(
        self,
        tenant_id: str,
        period_start: datetime,
        period_end: datetime,
    ) -> Invoice:
        """Generate an invoice for a billing period."""
        subscription = self.get_subscription(tenant_id)
        if not subscription:
            raise ValueError(f"No subscription found for tenant {tenant_id}")

        # Calculate base price
        pricing = PLAN_PRICING[subscription.plan_tier]
        if subscription.billing_cycle == BillingCycle.ANNUAL:
            base_price = pricing.annual_price * 100  # Convert to cents
        else:
            base_price = pricing.monthly_price * 100

        # Calculate add-on costs
        add_ons_total = 0
        for add_on in subscription.add_ons:
            add_on_pricing = ADD_ON_PRICING[add_on]
            if subscription.billing_cycle == BillingCycle.ANNUAL:
                add_ons_total += add_on_pricing.monthly_price * 12 * 100
                add_ons_total += add_on_pricing.setup_price * 100
            else:
                add_ons_total += add_on_pricing.monthly_price * 100
                add_ons_total += add_on_pricing.setup_price * 100

        # Calculate usage overages
        usage_overages = 0
        if tenant_id in self.usage_records:
            for usage in self.usage_records[tenant_id]:
                if usage.period_start >= period_start and usage.period_end <= period_end:
                    overages = self.calculate_overages(subscription, usage)
                    usage_overages += int(overages.get('total_cost', 0) * 100)

        # Calculate tax (simplified - assume 8% for all regions)
        tax_rate = 0.08
        subtotal = base_price + add_ons_total + usage_overages
        tax = int(subtotal * tax_rate)
        total = subtotal + tax

        invoice = Invoice(
            invoice_id=f"INV_{tenant_id}_{int(period_end.timestamp())}",
            tenant_id=tenant_id,
            period_start=period_start,
            period_end=period_end,
            plan_tier=subscription.plan_tier,
            subtotal=subtotal,
            add_ons_total=add_ons_total,
            usage_overages=usage_overages,
            tax=tax,
            total=total,
            due_date=period_end + timedelta(days=15),
        )

        if tenant_id not in self.invoices:
            self.invoices[tenant_id] = []
        self.invoices[tenant_id].append(invoice)

        return invoice

    def check_usage_limits(
        self,
        tenant_id: str,
        current_usage: UsageRecord,
    ) -> Dict[str, Any]:
        """Check if tenant is approaching or exceeding limits."""
        subscription = self.get_subscription(tenant_id)
        if not subscription:
            return {'error': 'No subscription found'}

        limits = PLAN_LIMITS[subscription.plan_tier]
        warnings = []
        exceeded = []

        # Check each limit
        usage_ratio = current_usage.events_processed / limits.events_per_month if limits.events_per_month != float('inf') else 0
        if usage_ratio >= 1.0:
            exceeded.append('events')
        elif usage_ratio >= 0.8:
            warnings.append('events')

        if current_usage.process_models_created >= limits.process_models:
            exceeded.append('process_models')
        elif current_usage.process_models_created >= limits.process_models * 0.8:
            warnings.append('process_models')

        if current_usage.storage_used_gb >= limits.storage_gb:
            exceeded.append('storage')
        elif current_usage.storage_used_gb >= limits.storage_gb * 0.8:
            warnings.append('storage')

        return {
            'warnings': warnings,
            'exceeded': exceeded,
            'usage_percentage': {
                'events': min(usage_ratio * 100, 100),
            }
        }

    def estimate_monthly_cost(
        self,
        plan_tier: PlanTier,
        billing_cycle: BillingCycle,
        estimated_events: int,
        estimated_storage_gb: float,
        add_ons: Optional[List[AddOnType]] = None,
    ) -> Dict[str, Any]:
        """Estimate monthly cost for a given configuration."""
        pricing = PLAN_PRICING[plan_tier]

        if billing_cycle == BillingCycle.ANNUAL:
            base_price = pricing.annual_price / 12  # Monthly equivalent
        else:
            base_price = pricing.monthly_price

        # Add-on costs
        add_on_cost = 0
        if add_ons:
            for add_on in add_ons:
                add_on_pricing = ADD_ON_PRICING[add_on]
                add_on_cost += add_on_pricing.monthly_price

        # Usage overage estimates
        limits = PLAN_LIMITS[plan_tier]
        overage_cost = 0

        if estimated_events > limits.events_per_month and limits.events_per_month != float('inf'):
            events_over_millions = (estimated_events - limits.events_per_month) / 1_000_000
            overage_cost += events_over_millions * self.EVENT_PRICE_PER_MILLION

        if estimated_storage_gb > limits.storage_gb and limits.storage_gb != float('inf'):
            storage_over = estimated_storage_gb - limits.storage_gb
            overage_cost += storage_over * self.STORAGE_PRICE_PER_GB

        total = base_price + add_on_cost + overage_cost

        return {
            'base_price': round(base_price, 2),
            'add_on_cost': round(add_on_cost, 2),
            'estimated_overage': round(overage_cost, 2),
            'total_monthly': round(total, 2),
            'total_annual': round(total * 12 * (1 - 0.17) if billing_cycle == BillingCycle.ANNUAL else total * 12, 2),
        }

    def get_plan_comparison(self) -> List[Dict[str, Any]]:
        """Get comparison of all plans."""
        plans = []
        for tier in PlanTier:
            limits = PLAN_LIMITS[tier]
            features = PLAN_FEATURES[tier]
            pricing = PLAN_PRICING[tier]

            plans.append({
                'tier': tier.value,
                'monthly_price': pricing.monthly_price,
                'annual_price': pricing.annual_price,
                'events_per_month': limits.events_per_month if limits.events_per_month != float('inf') else 'Unlimited',
                'team_members': limits.team_members if limits.team_members != float('inf') else 'Unlimited',
                'storage_gb': limits.storage_gb if limits.storage_gb != float('inf') else 'Unlimited',
                'ai_requests': limits.ai_requests_per_month if limits.ai_requests_per_month != float('inf') else 'Unlimited',
                'verticals': features.verticals if features.verticals else ['None'],
                'real_time_drift': features.real_time_drift,
                'api_access': features.api_access,
                'sso': features.sso if features.sso else ['None'],
                'support': features.support_level,
                'sla': f"{features.sla_uptime}%" if features.sla_uptime > 0 else 'N/A',
                'soc2': features.soc2_reporting,
            })

        return plans


# Convenience functions for common operations
def get_starter_price() -> Dict[str, int]:
    """Get Starter plan pricing."""
    pricing = PLAN_PRICING[PlanTier.STARTER]
    return {'monthly': pricing.monthly_price, 'annual': pricing.annual_price}


def get_professional_price() -> Dict[str, int]:
    """Get Professional plan pricing."""
    pricing = PLAN_PRICING[PlanTier.PROFESSIONAL]
    return {'monthly': pricing.monthly_price, 'annual': pricing.annual_price}


def get_plan_limits(tier: str) -> Dict[str, Any]:
    """Get limits for a plan tier."""
    tier_enum = PlanTier(tier)
    limits = PLAN_LIMITS[tier_enum]
    return {
        'events_per_month': limits.events_per_month,
        'process_models': limits.process_models,
        'team_members': limits.team_members,
        'storage_gb': limits.storage_gb,
        'ai_requests_per_month': limits.ai_requests_per_month,
        'api_calls_per_month': limits.api_calls_per_month,
        'webhooks': limits.webhooks,
    }


__all__ = [
    'PlanTier',
    'BillingCycle',
    'AddOnType',
    'BillingEngine',
    'get_starter_price',
    'get_professional_price',
    'get_plan_limits',
]
