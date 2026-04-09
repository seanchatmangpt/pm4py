"""
Test PM4Py POWL extensions.

Verifies that the POWL extensions (GuardOperator, GuardCondition, ChoiceRegionWithGuards,
CancellationScope, ExtendedPOWL) work correctly with PM4Py's POWL implementation.
"""

import pytest

from pm4py.objects.powl.obj import Transition, SilentTransition, StrictPartialOrder, Sequence, OperatorPOWL
from pm4py.objects.process_tree.obj import Operator

from pm4py.objects.powl.extensions import (
    GuardOperator,
    GuardCondition,
    ChoiceRegionWithGuards,
    CancellationScope,
    ExtendedPOWL,
    add_guard_to_choice,
    add_cancellation_scope,
)


def test_guard_condition():
    """Test GuardCondition evaluation."""
    guard = GuardCondition(
        variable="amount",
        operator=GuardOperator.GREATER_THAN,
        value=1000
    )

    # Test evaluation
    assert guard.evaluate({"amount": 1500})
    assert not guard.evaluate({"amount": 500})

    # Test serialization
    data = guard.to_dict()
    restored = GuardCondition.from_dict(data)
    assert restored.variable == "amount"
    assert restored.operator == GuardOperator.GREATER_THAN
    assert restored.value == 1000


def test_choice_region_with_guards():
    """Test ChoiceRegionWithGuards."""
    # Create a simple XOR choice
    a = Transition(label="A")
    b = Transition(label="B")
    xor = OperatorPOWL(Operator.XOR, [a, b])

    region = ChoiceRegionWithGuards(
        id="choice_1",
        powl_node=xor,
        activities={"A", "B"},
        choice_type="exclusive"
    )

    # Add guards
    guard_a = GuardCondition("type", GuardOperator.EQUALS, "premium")
    guard_b = GuardCondition("type", GuardOperator.EQUALS, "standard")
    region.set_guard("A", guard_a)
    region.set_guard("B", guard_b)

    # Test guard evaluation
    assert region.evaluate_guards({"type": "premium"}) == ["A"]
    assert region.evaluate_guards({"type": "standard"}) == ["B"]


def test_cancellation_scope():
    """Test CancellationScope."""
    scope = CancellationScope(
        id="cancel_1",
        cancellable_activities={"A", "B"},
        trigger_activity="C",
        cancellation_type="terminate"
    )

    # Test serialization
    data = scope.to_dict()
    restored = CancellationScope.from_dict(data)
    assert restored.id == "cancel_1"
    assert restored.trigger_activity == "C"
    assert restored.cancellation_type == "terminate"


def test_extended_powl_with_guards():
    """Test ExtendedPOWL with guard conditions."""
    # Create a simple process: A -> (B | C) -> D
    a = Transition(label="A")
    b = Transition(label="B")
    c = Transition(label="C")
    d = Transition(label="D")

    # Create XOR choice
    xor = OperatorPOWL(Operator.XOR, [b, c])

    # Create sequence: A -> xor -> D
    seq = StrictPartialOrder([a, xor, d])
    seq.add_edge(a, xor)
    seq.add_edge(xor, d)

    # Add guards to the choice
    extended = add_guard_to_choice(
        powl_model=seq,
        choice_id="choice_1",
        activity="B",
        variable="priority",
        operator=GuardOperator.EQUALS,
        value="high",
        description="High priority customers"
    )

    assert "choice_1" in extended.get_choice_regions()
    assert extended.get_choice_regions()["choice_1"].get_guard("B") is not None


def test_extended_powl_with_cancellation():
    """Test ExtendedPOWL with cancellation scopes."""
    # Create a simple process: A -> B -> C
    a = Transition(label="A")
    b = Transition(label="B")
    c = Transition(label="C")

    seq = Sequence([a, b, c])

    # Add cancellation scope
    extended = add_cancellation_scope(
        powl_model=seq,
        scope_id="cancel_1",
        cancellable_activities={"B", "C"},
        trigger_activity="A",
        cancellation_type="terminate"
    )

    assert "cancel_1" in extended.get_cancellation_scopes()
    assert extended.get_cancellation_scopes()["cancel_1"].trigger_activity == "A"


def test_extended_powl_get_activities():
    """Test ExtendedPOWL.get_activities()."""
    # Create a simple process: A -> (B | C) -> D
    a = Transition(label="A")
    b = Transition(label="B")
    c = Transition(label="C")
    d = Transition(label="D")

    xor = OperatorPOWL(Operator.XOR, [b, c])
    seq = Sequence([a, xor, d])

    extended = ExtendedPOWL(powl_model=seq)

    activities = extended.get_activities()
    assert activities == {"A", "B", "C", "D"}


def test_extended_powl_validate_semantics():
    """Test ExtendedPOWL semantic validation."""
    a = Transition(label="A")
    b = Transition(label="B")
    seq = Sequence([a, b])

    # Create invalid choice region (references non-existent activity)
    xor = OperatorPOWL(Operator.XOR, [a, b])
    region = ChoiceRegionWithGuards(
        id="invalid_choice",
        powl_node=xor,
        activities={"C"},  # C doesn't exist
        choice_type="exclusive"
    )

    extended = ExtendedPOWL(
        powl_model=seq,
        choice_regions={"invalid_choice": region}
    )

    errors = extended.validate_semantics()
    assert len(errors) > 0
    assert "non-existent activity" in errors[0]


def test_extended_powl_simplify():
    """Test ExtendedPOWL.simplify()."""
    # Create a process with silent transitions that can be simplified
    a = Transition(label="A")
    tau = SilentTransition()
    b = Transition(label="B")

    seq = Sequence([a, tau, b])

    extended = ExtendedPOWL(powl_model=seq)
    simplified = extended.simplify()

    # The simplified model should be equivalent
    assert isinstance(simplified, ExtendedPOWL)
    assert simplified.powl_model is not None


def test_extended_powl_copy():
    """Test ExtendedPOWL.copy()."""
    a = Transition(label="A")
    b = Transition(label="B")
    seq = Sequence([a, b])

    xor = OperatorPOWL(Operator.XOR, [a, b])
    region = ChoiceRegionWithGuards(
        id="choice_1",
        powl_node=xor,
        activities={"A"},
        choice_type="exclusive"
    )

    scope = CancellationScope(
        id="cancel_1",
        cancellable_activities={"A"},
        trigger_activity="B"
    )

    extended = ExtendedPOWL(
        powl_model=seq,
        choice_regions={"choice_1": region},
        cancellation_scopes={"cancel_1": scope},
        metadata={"key": "value"}
    )

    copied = extended.copy()

    # Check that the copy is equivalent but not the same object
    assert copied is not extended
    assert copied.powl_model is not extended.powl_model
    assert len(copied.get_choice_regions()) == 1
    assert len(copied.get_cancellation_scopes()) == 1
    assert copied.metadata == {"key": "value"}


def test_add_guard_to_choice_convenience():
    """Test add_guard_to_choice convenience function."""
    a = Transition(label="A")
    b = Transition(label="B")
    xor = OperatorPOWL(Operator.XOR, [a, b])

    extended = add_guard_to_choice(
        powl_model=xor,
        choice_id="priority_choice",
        activity="A",
        variable="priority",
        operator=GuardOperator.EQUALS,
        value="high"
    )

    assert "priority_choice" in extended.get_choice_regions()
    guard = extended.get_choice_regions()["priority_choice"].get_guard("A")
    assert guard is not None
    assert guard.variable == "priority"


def test_add_cancellation_scope_convenience():
    """Test add_cancellation_scope convenience function."""
    a = Transition(label="A")
    b = Transition(label="B")
    seq = Sequence([a, b])

    extended = add_cancellation_scope(
        powl_model=seq,
        scope_id="emergency_cancel",
        cancellable_activities={"B"},
        trigger_activity="A",
        cancellation_type="escalate"
    )

    assert "emergency_cancel" in extended.get_cancellation_scopes()
    scope = extended.get_cancellation_scopes()["emergency_cancel"]
    assert scope.cancellation_type == "escalate"


def test_guard_operators():
    """Test all GuardOperator types."""
    # Test EQUALS
    assert GuardCondition("x", GuardOperator.EQUALS, 5).evaluate({"x": 5})
    assert not GuardCondition("x", GuardOperator.EQUALS, 5).evaluate({"x": 3})

    # Test NOT_EQUALS
    assert not GuardCondition("x", GuardOperator.NOT_EQUALS, 5).evaluate({"x": 5})
    assert GuardCondition("x", GuardOperator.NOT_EQUALS, 5).evaluate({"x": 3})

    # Test GREATER_THAN
    assert GuardCondition("x", GuardOperator.GREATER_THAN, 5).evaluate({"x": 10})
    assert not GuardCondition("x", GuardOperator.GREATER_THAN, 5).evaluate({"x": 3})

    # Test LESS_THAN
    assert GuardCondition("x", GuardOperator.LESS_THAN, 5).evaluate({"x": 3})
    assert not GuardCondition("x", GuardOperator.LESS_THAN, 5).evaluate({"x": 10})

    # Test IN
    assert GuardCondition("x", GuardOperator.IN, [1, 2, 3]).evaluate({"x": 2})
    assert not GuardCondition("x", GuardOperator.IN, [1, 2, 3]).evaluate({"x": 5})

    # Test NOT_IN
    assert not GuardCondition("x", GuardOperator.NOT_IN, [1, 2, 3]).evaluate({"x": 2})
    assert GuardCondition("x", GuardOperator.NOT_IN, [1, 2, 3]).evaluate({"x": 5})
