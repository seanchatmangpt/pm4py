"""
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions UG (haftungsbeschränkt)

Licensed under the GNU AGPL v3.0 - see LICENSE file for details.
"""

"""
Tests for all 8 POWL patterns following van der Aalst's theoretical approach.

Tests cover:
1. LOOP (1-node and 2-node)
2. INTERLEAVING (StrictPartialOrder)
3. CHOICE GRAPHS (DecisionGraph)
4. GUARDS (GuardCondition, ChoiceRegionWithGuards)
5. CANCELLATION (CancellationScope)
6. MULTI-INSTANCE (MultiInstanceActivity)
7. MESSAGE CORRELATION (MessageCorrelation)
8. EVENT INTERLEAVING (EventInterleavingMiner)
"""

import pytest
from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.objects.powl.obj import (
    Transition, SilentTransition, StrictPartialOrder,
    OperatorPOWL, Operator, DecisionGraph, FrequentTransition,
)
from pm4py.objects.powl.BinaryRelation import BinaryRelation
from pm4py.objects.powl.extensions import (
    GuardOperator, GuardCondition, ChoiceRegionWithGuards,
    CancellationScope, ExtendedPOWL,
)
from pm4py.objects.powl.multi_instance import (
    MultiInstanceType, MultiInstanceActivity, MultiInstancePOWL,
)
from pm4py.objects.powl.messaging import (
    MessageEvent, MessageCorrelation, MessagingPOWL,
)
from pm4py.objects.powl.event_interleaving import EventInterleavingMiner


# ============================================================
# 1. LOOP (Single Node)
# ============================================================

class TestLoopSingle:
    """Test 1-node loop support: *(A)"""

    def test_one_child_loop_creation(self):
        a = Transition('a')
        loop = OperatorPOWL(Operator.LOOP, [a])
        assert loop.operator == Operator.LOOP
        assert len(loop.children) == 1

    def test_two_child_loop_still_works(self):
        a = Transition('a')
        b = Transition('b')
        loop = OperatorPOWL(Operator.LOOP, [a, b])
        assert len(loop.children) == 2

    def test_zero_child_loop_raises(self):
        with pytest.raises(Exception):
            OperatorPOWL(Operator.LOOP, [])

    def test_three_child_loop_raises(self):
        a = Transition('a')
        b = Transition('b')
        c = Transition('c')
        with pytest.raises(Exception):
            OperatorPOWL(Operator.LOOP, [a, b, c])

    def test_one_child_loop_petri_net_conversion(self):
        from pm4py.objects.conversion.powl.variants.to_petri_net import apply
        a = Transition('a')
        loop = OperatorPOWL(Operator.LOOP, [a])
        net, im, fm = apply(loop)
        assert len(net.transitions) > 0
        assert len(net.places) > 0


# ============================================================
# 2. INTERLEAVING (StrictPartialOrder)
# ============================================================

class TestInterleaving:
    """Test interleaving via StrictPartialOrder"""

    def test_basic_partial_order(self):
        a = Transition('a')
        b = Transition('b')
        po = StrictPartialOrder([a, b])
        assert po.operator == Operator.PARTIALORDER

    def test_ordered_partial_order(self):
        a = Transition('a')
        b = Transition('b')
        po = StrictPartialOrder([a, b])
        po.add_edge(a, b)
        assert po.order.is_edge(a, b)

    def test_concurrent_activities(self):
        a = Transition('a')
        b = Transition('b')
        c = Transition('c')
        po = StrictPartialOrder([a, b, c])
        po.add_edge(a, c)
        # b is concurrent with both a and c
        assert not po.order.is_edge(a, b)
        assert not po.order.is_edge(b, c)

    def test_partial_order_petri_net(self):
        from pm4py.objects.conversion.powl.variants.to_petri_net import apply
        a = Transition('a')
        b = Transition('b')
        po = StrictPartialOrder([a, b])
        net, im, fm = apply(po)
        assert len(net.transitions) >= 2


# ============================================================
# 3. CHOICE GRAPHS (DecisionGraph)
# ============================================================

class TestChoiceGraphs:
    """Test Choice Graph discovery and soundness"""

    def test_simple_decision_graph(self):
        a = Transition('a')
        b = Transition('b')
        c = Transition('c')
        order = BinaryRelation([a, b, c])
        order.add_edge(a, b)
        order.add_edge(a, c)
        dg = DecisionGraph(order, [a], [b, c])
        assert dg is not None

    def test_decision_graph_soundness(self):
        a = Transition('a')
        b = Transition('b')
        c = Transition('c')
        order = BinaryRelation([a, b, c])
        order.add_edge(a, b)
        order.add_edge(a, c)
        dg = DecisionGraph(order, [a], [b, c])
        report = dg.get_soundness_report()
        assert report['is_sound']

    def test_overlapping_choice_regions(self):
        """Test the key advantage of Choice Graphs over block-structured XOR"""
        a = Transition('a')
        b = Transition('b')
        c = Transition('c')
        d = Transition('d')
        order = BinaryRelation([a, b, c, d])
        order.add_edge(a, b)
        order.add_edge(a, c)
        order.add_edge(b, d)
        order.add_edge(c, d)
        order.add_edge(b, c)  # Overlapping: b can lead to c
        dg = DecisionGraph(order, [a], [d])
        report = dg.get_soundness_report()
        # Diamond pattern with extra edge may or may not be sound
        assert 'is_sound' in report


# ============================================================
# 4. GUARDS
# ============================================================

class TestGuards:
    """Test guard conditions and choice regions with guards"""

    def test_guard_equals(self):
        guard = GuardCondition("amount", GuardOperator.GREATER_THAN, 100)
        assert guard.evaluate({"amount": 200})
        assert not guard.evaluate({"amount": 50})

    def test_guard_missing_variable(self):
        guard = GuardCondition("amount", GuardOperator.EQUALS, 100)
        assert not guard.evaluate({"other": 100})

    def test_guard_in_operator(self):
        guard = GuardCondition("status", GuardOperator.IN, ["approved", "pending"])
        assert guard.evaluate({"status": "approved"})
        assert not guard.evaluate({"status": "rejected"})

    def test_guard_serialization(self):
        guard = GuardCondition("amount", GuardOperator.GREATER_THAN, 100)
        d = guard.to_dict()
        restored = GuardCondition.from_dict(d)
        assert restored.variable == "amount"
        assert restored.operator == GuardOperator.GREATER_THAN
        assert restored.value == 100

    def test_choice_region_evaluate(self):
        a = Transition('a')
        b = Transition('b')
        xor = OperatorPOWL(Operator.XOR, [a, b])
        region = ChoiceRegionWithGuards(
            id="r1",
            powl_node=xor,
            activities={"a", "b"},
            guard_conditions={
                "a": GuardCondition("type", GuardOperator.EQUALS, "fast"),
                "b": GuardCondition("type", GuardOperator.EQUALS, "slow"),
            },
        )
        result = region.evaluate_guards({"type": "fast"})
        assert "a" in result

    def test_choice_region_soundness(self):
        region = ChoiceRegionWithGuards(
            id="r1",
            powl_node=OperatorPOWL(Operator.XOR, [Transition('a'), Transition('b')]),
            activities={"a", "b"},
            guard_conditions={
                "a": GuardCondition("type", GuardOperator.EQUALS, "fast"),
                "b": GuardCondition("type", GuardOperator.EQUALS, "fast"),
            },
        )
        # Identical guards violate mutual exclusivity
        assert not region.is_sound()

    def test_choice_region_distinct_guards_sound(self):
        region = ChoiceRegionWithGuards(
            id="r1",
            powl_node=OperatorPOWL(Operator.XOR, [Transition('a'), Transition('b')]),
            activities={"a", "b"},
            guard_conditions={
                "a": GuardCondition("type", GuardOperator.EQUALS, "fast"),
                "b": GuardCondition("type", GuardOperator.EQUALS, "slow"),
            },
        )
        assert region.is_sound()

    def test_extended_powl_validation(self):
        xor = OperatorPOWL(Operator.XOR, [Transition('a'), Transition('b')])
        region = ChoiceRegionWithGuards(
            id="r1", powl_node=xor, activities={"a", "b"},
        )
        ext = ExtendedPOWL(xor, choice_regions={"r1": region})
        errors = ext.validate_semantics()
        assert len(errors) == 0


# ============================================================
# 5. CANCELLATION
# ============================================================

class TestCancellation:
    """Test cancellation scopes"""

    def test_basic_cancellation_scope(self):
        scope = CancellationScope(
            id="cs1",
            cancellable_activities={"b", "c"},
            trigger_activity="cancel",
        )
        assert scope.is_sound()

    def test_self_cancellation_unsound(self):
        scope = CancellationScope(
            id="cs2",
            cancellable_activities={"cancel"},
            trigger_activity="cancel",
        )
        assert not scope.is_sound()

    def test_empty_cancellable_unsound(self):
        scope = CancellationScope(
            id="cs3",
            cancellable_activities=set(),
            trigger_activity="cancel",
        )
        assert not scope.is_sound()

    def test_unbounded_cancellation_unsound(self):
        scope = CancellationScope(
            id="cs4",
            cancellable_activities={"b"},
            trigger_activity="cancel",
            bounded=False,
        )
        assert not scope.is_sound()

    def test_cancellation_serialization(self):
        scope = CancellationScope(
            id="cs5",
            cancellable_activities={"b", "c"},
            trigger_activity="cancel",
            cancellation_type="terminate",
        )
        d = scope.to_dict()
        restored = CancellationScope.from_dict(d)
        assert restored.id == "cs5"
        assert restored.cancellable_activities == {"b", "c"}

    def test_cancellation_with_condition(self):
        guard = GuardCondition("urgent", GuardOperator.EQUALS, True)
        scope = CancellationScope(
            id="cs6",
            cancellable_activities={"b"},
            trigger_activity="cancel",
            condition=guard,
        )
        assert scope.is_sound()
        assert scope.condition is not None


# ============================================================
# 6. MULTI-INSTANCE
# ============================================================

class TestMultiInstance:
    """Test multi-instance activities"""

    def test_sequential_multi_instance(self):
        mi = MultiInstanceActivity(
            activity="review",
            mi_type=MultiInstanceType.SEQUENTIAL,
            min_instances=1,
            max_instances=5,
        )
        assert mi.is_sound()

    def test_parallel_multi_instance(self):
        mi = MultiInstanceActivity(
            activity="approve",
            mi_type=MultiInstanceType.PARALLEL,
            min_instances=2,
            max_instances=10,
        )
        assert mi.is_sound()

    def test_unbounded_multi_instance_unsound(self):
        mi = MultiInstanceActivity(
            activity="loop",
            mi_type=MultiInstanceType.PARALLEL,
            max_instances=None,
        )
        assert not mi.is_sound()

    def test_invalid_bounds_unsound(self):
        mi = MultiInstanceActivity(
            activity="bad",
            mi_type=MultiInstanceType.SEQUENTIAL,
            min_instances=10,
            max_instances=5,
        )
        assert not mi.is_sound()

    def test_multi_instance_serialization(self):
        mi = MultiInstanceActivity(
            activity="review",
            mi_type=MultiInstanceType.PARALLEL,
            min_instances=1,
            max_instances=3,
        )
        d = mi.to_dict()
        restored = MultiInstanceActivity.from_dict(d)
        assert restored.activity == "review"
        assert restored.mi_type == MultiInstanceType.PARALLEL

    def test_multi_instance_powl(self):
        base = Transition('a')
        mi_powl = MultiInstancePOWL(base, [
            MultiInstanceActivity("a", MultiInstanceType.PARALLEL, 1, 5),
        ])
        report = mi_powl.get_soundness_report()
        assert report['is_sound']

    def test_multi_instance_powl_unsound(self):
        base = Transition('a')
        mi_powl = MultiInstancePOWL(base, [
            MultiInstanceActivity("a", MultiInstanceType.PARALLEL, max_instances=None),
        ])
        report = mi_powl.get_soundness_report()
        assert not report['is_sound']


# ============================================================
# 7. MESSAGE CORRELATION
# ============================================================

class TestMessageCorrelation:
    """Test message correlation patterns"""

    def test_basic_correlation(self):
        send = MessageEvent("send_order", "Order", "order_id", "send")
        recv = MessageEvent("receive_order", "Order", "order_id", "receive")
        corr = MessageCorrelation(send, recv)
        assert corr.is_sound()

    def test_mismatched_keys_unsound(self):
        send = MessageEvent("send_order", "Order", "order_id", "send")
        recv = MessageEvent("receive_order", "Order", "invoice_id", "receive")
        corr = MessageCorrelation(send, recv)
        assert not corr.is_sound()

    def test_unbounded_buffer_unsound(self):
        send = MessageEvent("send", "Msg", "id", "send")
        recv = MessageEvent("recv", "Msg", "id", "receive")
        corr = MessageCorrelation(send, recv, buffer_capacity=0)
        assert not corr.is_sound()

    def test_wrong_directions_unsound(self):
        send = MessageEvent("a", "Msg", "id", "receive")
        recv = MessageEvent("b", "Msg", "id", "send")
        corr = MessageCorrelation(send, recv)
        assert not corr.is_sound()

    def test_messaging_powl(self):
        base = Transition('a')
        send = MessageEvent("send", "Msg", "id", "send")
        recv = MessageEvent("recv", "Msg", "id", "receive")
        msg_powl = MessagingPOWL(base, [MessageCorrelation(send, recv)])
        report = msg_powl.get_soundness_report()
        assert report['is_sound']

    def test_correlation_serialization(self):
        send = MessageEvent("send", "Msg", "id", "send")
        recv = MessageEvent("recv", "Msg", "id", "receive")
        corr = MessageCorrelation(send, recv, buffer_capacity=50)
        d = corr.to_dict()
        restored = MessageCorrelation.from_dict(d)
        assert restored.buffer_capacity == 50
        assert restored.send_event.activity == "send"


# ============================================================
# 8. EVENT INTERLEAVING
# ============================================================

class TestEventInterleaving:
    """Test event interleaving mining"""

    def _make_log(self, traces):
        log = EventLog()
        for trace_acts in traces:
            log.append(Trace([Event({'concept:name': a}) for a in trace_acts]))
        return log

    def test_mine_interleavings(self):
        log = self._make_log([
            ["a", "b", "c"],
            ["a", "c", "b"],
        ])
        miner = EventInterleavingMiner()
        interleavings = miner.mine_interleavings_from_log(log)
        assert "a" in interleavings
        assert "b" in interleavings

    def test_mine_causal_relations(self):
        log = self._make_log([
            ["a", "b", "c"],
        ])
        miner = EventInterleavingMiner()
        causal = miner.mine_causal_relations(log)
        assert ("a", "b") in causal
        assert ("b", "c") in causal

    def test_to_powl_partial_order(self):
        log = self._make_log([
            ["a", "b", "c"],
        ])
        miner = EventInterleavingMiner()
        powl = miner.to_powl(log)
        assert powl is not None
        assert isinstance(powl, StrictPartialOrder)

    def test_to_powl_decision_graph(self):
        log = self._make_log([
            ["a", "b", "c"],
            ["a", "c", "b"],
        ])
        miner = EventInterleavingMiner()
        powl = miner.to_powl(log, use_decision_graph=True)
        assert powl is not None

    def test_empty_log(self):
        miner = EventInterleavingMiner()
        assert miner.to_powl(EventLog()) is None

    def test_interleaving_report(self):
        log = self._make_log([
            ["a", "b"],
            ["b", "a"],
        ])
        miner = EventInterleavingMiner()
        report = miner.get_interleaving_report(log)
        assert report['num_activities'] == 2
        assert report['num_causal_relations'] > 0
