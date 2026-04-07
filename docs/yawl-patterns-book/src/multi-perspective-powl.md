# Multi-Perspective Patterns in POWL v2

> **Therefore**: Represent organizational, temporal, and data perspectives through naming conventions, structural patterns, and POWL operators—without extending the language.

---

## Introduction

POWL v2 was designed primarily for **control flow** modeling. However, real-world processes require multiple perspectives:

1. **Organizational** (who does what): Roles, resources, departments
2. **Temporal** (when things happen): Durations, deadlines, timeouts
3. **Data** (what information flows): Data objects, conditions, decisions

This guide shows how to represent all three perspectives in **current POWL v2** through:
- **Naming conventions** for activities
- **Structural patterns** using existing operators
- **Composition patterns** that combine perspectives

---

## Philosophical Foundation

> *"A good pattern language naturally generates multi-perspective solutions."* — Christopher Alexander

POWL v2's expressiveness allows us to encode multiple perspectives without language extension:

| Perspective | POWL v2 Mechanism |
|-------------|-------------------|
| **Organizational** | Role-prefixed activities (`Manager.approve()`) |
| **Temporal** | LOOP for delays, XOR for timeouts (`Timer.timeout()`) |
| **Data** | Condition-annotated activities (`If.approved_then()`) |

---

## Organizational Perspective

### Problem: Who Performs This Activity?

Model roles, resources, and organizational units in process models.

### Solution: Role-Prefixed Activity Names

**Convention**: `{Role}.{Action}({Object})`

#### Examples

```python
# Simple role-based routing
model = parse_powl_model_string("""
X(
  Clerk.submit_application(),
  Manager.review(),
  Director.approve(),
  Committee.notify()
)
""")
```

#### Organizational Patterns

**1. Role-Based Sequence**

```python
# Handoff between roles
model = parse_powl_model_string("""
SEQ(
  Customer.submit(),
  Clerk.validate(),
  Manager.approve(),
  Shipper.ship()
)
""")
```

**2. Role-Based Parallelism**

```python
# Multiple roles working in parallel
model = parse_powl_model_string("""
PARALLEL(
  Designer.create_mockups(),
  Developer.write_code(),
  Analyst.collect_requirements()
)
""")
```

**3. Role-Based Choice**

```python
# Route to appropriate role based on customer tier
model = parse_powl_model_string("""
X(
  PlatinumAgent.handle(),
  GoldAgent.handle(),
  StandardAgent.handle()
)
""")
```

**4. Role Hierarchy**

```python
# Escalation through roles
model = parse_powl_model_string("""
X(
  FirstTier.support(),
  *(SecondTier.retry(), ThirdTier.escalate())
)
""")
```

#### Organizational Quality Attributes

| Attribute | How to Model |
|-----------|--------------|
| **Responsibility** | Role prefix identifies who is responsible |
| **Accountability** | Named roles can be traced back to organization |
| **Separation of duties** | XOR choices between different roles |
| **Delegation** | Sequences that hand off between roles |

---

## Temporal Perspective

### Problem: When Does This Happen?

Model time constraints, durations, deadlines, and timeouts.

### Solution: Time-Annotated Activities and Operators

**Conventions**:
- `{Timer}.{Action}()`: Temporal milestones
- `*({Wait}.{Activity}(), {Resume}.{Activity}())`: Wait loops
- `X({Timer}.timeout(), {Process}.continue())`: Timeout alternatives

#### Examples

**1. Sequential Time Constraints**

```python
# Activities with implicit duration
model = parse_powl_model_string("""
SEQ(
  Order.place(),
  Ship.within_24h(),
  Deliver.within_5_days()
)
""")
```

**2. Timeout with Alternative**

```python
# If A doesn't complete in time, switch to B
model = parse_powl_model_string("""
X(
  Process.complete_within_deadline(),
  Timer.timeout_then_escalate()
)
""")
```

**3. Retry Loop with Delay**

```python
# Retry with delay between attempts
model = parse_powl_model_string("""
*(
  Process.attempt(),
  Wait.for_retry_delay(),
  X(
    Process.on_success(),
    Process.on_failure()
  )
)
""")
```

**4. Deadline-Driven Choice**

```python
# Different actions based on time
model = parse_powl_model_string("""
X(
  Process.if_before_deadline(),
  Escalate.if_after_deadline(),
  Cancel.if_too_late()
)
""")
```

**5. Periodic Review**

```python
# Regular review cycles
model = parse_powl_model_string("""
*(
  Perform.daily_work(),
  Review.at_end_of_day(),
  X(
    Continue.next_day(),
    Escalate.on_issues()
  )
)
""")
```

#### Temporal Patterns

| Pattern | POWL v2 Representation |
|---------|----------------------|
| **Sequential duration** | `SEQ(A.with_time(), B.with_time())` |
| **Timeout** | `X(Process.finish(), Timer.timeout())` |
| **Retry with delay** | `*(Process.try(), Wait.delay())` |
| **Deadline** | `X(Before.deadline(), After.deadline())` |
| **Periodic** | `*(Work.do(), Wait.until_next())` |

---

## Data Perspective

### Problem: What Data Determines This Choice?

Model data-driven decisions, data objects, and information flow.

### Solution: Condition-Annotated Activities

**Conventions**:
- `If.{condition}_{then_action}()`: Data-driven choices
- `{Process}.{data_object}()`: Data objects in activity names
- `Check.{condition}()`: Data validation activities

#### Examples

**1. Simple Data-Driven Choice**

```python
# Choose based on data value
model = parse_powl_model_string("""
X(
  If.amount_under_10k_then_auto_approve(),
  If.amount_10k_to_50k_then_review(),
  If.amount_over_50k_then_committee_review()
)
""")
```

**2. Data Validation**

```python
# Validate data, handle errors
model = parse_powl_model_string("""
X(
  Data.validate_all_fields(),
  X(
    Process.on_valid_data(),
    Data.request_correction()
)
)
""")
```

**3. Data-Driven Routing**

```python
# Route based on customer data
model = parse_powl_model_string("""
X(
  Route.if_customer_is_platinum(),
  Route.if_customer_is_gold(),
  Route.if_customer_is_standard()
)
""")
```

**4. Data Transformation**

```python
# Transform data through sequence
model = parse_powl_model_string("""
SEQ(
  Data.collect_from_user(),
  Data.validate_format(),
  Data.enrich_from_database(),
  Data.transform_for_processing(),
  Process.use_transformed_data()
)
""")
```

**5. Data Availability Check**

```python
# Wait for data to become available
model = parse_powl_model_string("""
*(
  Check.if_data_available(),
  Wait.for_data_arrival(),
  X(
    Process.when_data_ready(),
    Escalate.if_data_timeout()
  )
)
""")
```

#### Data Patterns

| Pattern | POWL v2 Representation |
|---------|----------------------|
| **Data-driven choice** | `X(If.condition_A(), If.condition_B())` |
| **Data validation** | `X(Validate.if_valid(), Handle.if_invalid())` |
| **Data transformation** | `SEQ(Transform.A_to_B(), Transform.B_to_C())` |
| **Data availability** | `*(Check.data(), Wait.for_data())` |
| **Data routing** | `X(Route.if_data_A(), Route.if_data_B())` |

---

## Combined Multi-Perspective Patterns

### Real-World Examples

**1. Loan Approval (All Three Perspectives)**

```python
model = parse_powl_model_string("""
SEQ(
  # Organizational: Clerk receives, Data: loan data
  Clerk.submit_loan_application(),

  # Temporal: Validate within time window
  X(
    AutoSystem.validate_within_24h(),
    Escalate.to_manager_if_timeout()
  ),

  # Organizational + Data: Manager approves based on amount
  X(
    X(
      # Data: Under $10K, Org: Manager
      Manager.approve_if_under_10k(),

      # Data: $10K-$50K, Org: Finance
      Finance.review_if_10k_to_50k(),

      # Data: Over $50K, Org: Committee
      Committee.decide_if_over_50k()
    ),

    # Temporal: Deadline for decision
    X(
      Process.finalize_approval(),
      Escalate.if_deadline_missed()
    )
  ),

  # Organizational: Disbursement
  AutoSystem.disburse_funds()
)
""")
```

**2. Software Release Process**

```python
model = parse_powl_model_string("""
SEQ(
  # Organizational: Developer submits code
  Developer.submit_code(),

  # Parallel: Multiple perspectives
  PARALLEL(
    # Data: Validate code quality
    X(
      AutoSystem.tests_pass(),
      Developer.fix_bugs()
    ),

    # Data: Security review
    X(
      SecurityTeam.approve(),
      Developer.fix_security()
    ),

    # Temporal: Performance testing
    X(
      Performance.tests_complete(),
      Developer.optimize()
    )
  ),

  # Organizational: Final approval
  Manager.deploy_to_production(),

  # Temporal: Monitor for issues
  X(
    Operations.monitor_successfully(),
    X(
      Operations.rollback_on_failure(),
      Team.investigate_issues()
    )
  )
)
""")
```

**3. Customer Support Process**

```python
model = parse_powl_model_string("""
# Organizational: Customer tier routing
X(
  # Data: Platinum customers, Org: Premium support
  PlatinumAgent.handle_premium_customer(),

  # Data: Gold customers, Org: Standard support
  GoldAgent.handle_gold_customer(),

  # Data: Silver/Standard, Org: Basic support
  StandardAgent.handle_standard_customer()
)
""")
```

---

## Pattern Language for Multi-Perspective POWL

### Core Patterns

| Perspective | Pattern | POWL v2 |
|------------|---------|---------|
| **Org** | Role prefix | `Role.action()` |
| **Time** | Timeout | `X(Process.finish(), Timer.timeout())` |
| **Data** | Condition | `If.condition_then_action()` |

### Combination Patterns

| Combination | Pattern | POWL v2 |
|-------------|---------|---------|
| **Org + Data** | Role-based data routing | `X(RoleA.if_cond1(), RoleB.if_cond2())` |
| **Org + Time** | Role-based timeout | `X(RoleA.finish(), RoleB.escalate())` |
| **Data + Time** | Time-based data choice | `X(If.early_then_A(), If.late_then_B())` |
| **All Three** | Multi-perspective process | Combined conventions |

---

## Implementation Guidelines

### When Modeling Multi-Perspective Processes

1. **Start with control flow**: Map the basic process structure
2. **Add organizational layer**: Prefix activities with roles
3. **Add temporal constraints**: Encode timeouts and deadlines
4. **Add data conditions**: Annotate choices with data conditions

### Naming Convention Standards

**Organizational Prefixes**:
- Use role names: `Manager`, `Clerk`, `System`, `Customer`
- Use department names: `Finance`, `HR`, `IT`, `Legal`
- Use team names: `Tier1Support`, `Tier2Support`, `Escalation`

**Temporal Suffixes**:
- Use time constraints: `within_24h`, `before_deadline`, `after_timeout`
- Use durations: `short`, `medium`, `long`
- Use milestones: `initial`, `intermediate`, `final`

**Data Conditions**:
- Use `If.{condition}_{then_action}()`
- Use `Check.{data_property}()`
- Use `Validate.{data_constraint}()`

### Quality Checklist

When reviewing multi-perspective POWL models:

- [ ] **Organizational**: Can you identify who performs each activity?
- [ ] **Temporal**: Are time constraints explicit (deadlines, timeouts)?
- [ ] **Data**: Are data conditions visible in choices?
- [ ] **Consistency**: Do naming conventions follow standards?
- [ ] **Readability**: Can a domain expert understand the model?

---

## Tool Support

### Extracting Perspectives from POWL Models

```python
from pm4py.objects.powl.parser import parse_powl_model_string

model = parse_powl_model_string("X(Manager.approve(), Director.review())")

# Extract organizational perspective
activities = pm4py.dx.model_activities(model)
roles = set(a.split('.')[0] for a in activities if '.' in a)
print(f"Roles: {roles}")
# Output: {'Manager', 'Director'}
```

### Validating Multi-Perspective Models

```python
def validate_multi_perspective_model(model):
    """Check if model follows multi-perspective conventions."""

    activities = pm4py.dx.model_activities(model)

    # Check for role prefixes
    has_org = any('.' in a and not a.startswith('If') for a in activities)

    # Check for temporal markers
    has_temporal = any(word in a for word in ['timeout', 'deadline', 'wait']
                       for a in activities for word in words)

    # Check for data conditions
    has_data = any(a.startswith('If') or a.startswith('Check') for a in activities)

    return {
        'organizational': has_org,
        'temporal': has_temporal,
        'data': has_data
    }
```

---

## References

- van der Aalst, W.M.P. (2016). *Process Mining: Data Science in Action*
- Mannhardt, F., et al. (2016). "Balanced Multi-perspective Process Checking"
- POWL v2: Kourani & van der Aalst (2025)

---

**Next**: Explore specific patterns in each perspective category.
