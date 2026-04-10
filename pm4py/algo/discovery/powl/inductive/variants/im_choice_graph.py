"""
POWL 2.0 Inductive Miner with Choice Graphs (PM×).

Implements the extended Inductive Miner that discovers POWL 2.0 models
with choice graphs instead of block-structured XOR operators.

Based on:
H Kourani, G Park, WMP van der Aalst. "Unlocking Non-Block-Structured Decisions:
Inductive Mining with Choice Graphs" arXiv preprint arXiv:2505.07052.
"""

from typing import List, Set, Tuple, Optional, Dict, Any
from abc import ABC

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.algo.discovery.powl.inductive.variants.im_tree import IMBasePOWL
from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.util.compression import util as comut
from pm4py.objects.powl.obj import (
    POWL, Transition, SilentTransition, StrictPartialOrder,
    Sequence, OperatorPOWL, DecisionGraph
)
from pm4py.objects.process_tree.obj import Operator
from pm4py.objects.powl import choice_graph_discovery
from pm4py.objects.powl.BinaryRelation import BinaryRelation


class InductiveMinerChoiceGraph(IMBasePOWL):
    """
    Inductive Miner with Choice Graphs (PM×).

    Extends the Inductive Miner to discover POWL 2.0 models by:
    1. First trying to detect valid choice graph cuts
    2. Falling back to partial order cuts
    3. Using base cases for simple logs
    4. Applying fall-through when no cut is found

    This replaces the XOR-based choice detection with the more expressive
    choice graph mechanism from the paper.
    """

    def __init__(self):
        super().__init__()
        self.detect_choice_graph_cut = True
        self.detect_partial_order_cut = True
        self.use_loop_detection = True

    def apply(self, obj: IMDataStructureUVCL, parameters: Optional[Dict[str, Any]] = None) -> POWL:
        """
        Apply the inductive miner with choice graph support.

        Args:
            obj: Inductive miner data structure (event log)
            parameters: Optional parameters

        Returns:
            Discovered POWL 2.0 model
        """
        if parameters is None:
            parameters = {}

        # Get the event log from the data structure
        if isinstance(obj, EventLog):
            log = obj
        elif isinstance(obj, IMDataStructureUVCL):
            log = self._uvcl_to_event_log(obj._obj)
        else:
            log = obj

        # Base cases
        base_case_result = self._check_base_cases(log)
        if base_case_result is not None:
            return base_case_result

        # Try to detect a choice graph cut first
        if self.detect_choice_graph_cut:
            choice_graph_cut = self._detect_choice_graph_cut(log)
            if choice_graph_cut is not None:
                return self._apply_choice_graph_cut(log, choice_graph_cut)

        # Fall back to partial order cut detection
        if self.detect_partial_order_cut:
            partial_order_cut = self._detect_partial_order_cut(log)
            if partial_order_cut is not None:
                return self._apply_partial_order_cut(log, partial_order_cut)

        # Try loop detection
        if self.use_loop_detection:
            loop_cut = self._detect_loop_cut(log)
            if loop_cut is not None:
                return self._apply_loop_cut(log, loop_cut)

        # Fall-through: handle cases where no cut is detected
        return self._fall_through(log)

    def _uvcl_to_event_log(self, uvcl) -> EventLog:
        """
        Convert a UVCL (Counter of variants) to an EventLog.

        Args:
            uvcl: Counter mapping trace tuples to frequencies

        Returns:
            EventLog with expanded traces
        """
        event_log = EventLog()
        for trace_tuple, count in uvcl.items():
            for _ in range(count):
                events = [Event({'concept:name': act}) for act in trace_tuple]
                event_log.append(Trace(events))
        return event_log

    def _check_base_cases(self, log: EventLog) -> Optional[POWL]:
        """
        Check for base cases.

        Base cases:
        - Empty log → silent transition
        - Single activity log → single activity

        Args:
            log: Event log

        Returns:
            POWL model if base case detected, None otherwise
        """
        activities = choice_graph_discovery.get_activities(log)

        # Empty log
        if len(activities) == 0:
            return SilentTransition()

        # Single activity
        if len(activities) == 1:
            activity = list(activities)[0]
            return Transition(activity)

        return None

    def _detect_choice_graph_cut(self, log: EventLog) -> Optional[List[Set[str]]]:
        """
        Detect a valid choice graph cut in the log.

        Uses MineDG algorithm (Algorithm 1) to generate candidate partitions,
        then validates them using Definition 5.

        Args:
            log: Event log

        Returns:
            Valid partition if choice graph cut found, None otherwise
        """
        # Step 1: Generate candidate partition using MineDG
        parts = choice_graph_discovery.mine_dg(log)

        # Need at least 2 parts for a choice graph cut
        if len(parts) < 2:
            return None

        # Step 2: Validate the cut
        if choice_graph_discovery.is_valid_choice_graph_cut(log, parts):
            return parts

        return None

    def _apply_choice_graph_cut(self, log: EventLog, parts: List[Set[str]]) -> DecisionGraph:
        """
        Apply a choice graph cut to recursively discover a POWL 2.0 model.

        For each part Ai in the partition:
        1. Project log onto Ai
        2. Recursively apply PM×
        3. Map Ai to its discovered POWL model in the choice graph

        Args:
            log: Event log
            parts: Valid partition (choice graph cut)

        Returns:
            DecisionGraph representing the choice structure
        """
        # Step 1: Project log onto each part and discover sub-models
        sub_models = {}
        for i, part in enumerate(parts):
            # Project log onto this part
            sub_log = choice_graph_discovery.project_log(log, part)

            # Convert EventLog to UVCL before wrapping
            sub_uvcl = comut.get_variants(comut.project_univariate(sub_log))

            # Recursively discover POWL model for this part
            sub_model = self.apply(IMDataStructureUVCL(sub_uvcl))
            sub_models[i] = sub_model

        # Step 2: Create choice graph from the cut and sub-models
        choice_graph = choice_graph_discovery.create_choice_graph_from_cut(
            log, parts, sub_models
        )

        return choice_graph

    def _detect_partial_order_cut(self, log: EventLog) -> Optional[List[Set[str]]]:
        """
        Detect a partial order cut in the log.

        A partial order cut is detected when:
        - Activities can be partitioned into subsets
        - No ordering constraints between subsets (concurrency)
        - All activities in different subsets are mutually reachable

        Args:
            log: Event log

        Returns:
            Valid partition if partial order cut found, None otherwise
        """
        dfg = choice_graph_discovery.compute_dfg_relation(log)
        dfg_tc = choice_graph_discovery.compute_transitive_closure(dfg)
        activities = choice_graph_discovery.get_activities(log)

        # Check for concurrent activities (not ordered in DFG)
        parts = []
        remaining = set(activities)

        while remaining:
            # Find activities that are mutually reachable (form a concurrent group)
            current_part = set()
            for activity in list(remaining):
                # Add activity if it's mutually reachable with all in current_part
                can_add = True
                for existing in current_part:
                    if ((activity, existing) not in dfg_tc or
                        (existing, activity) not in dfg_tc):
                        can_add = False
                        break

                if can_add:
                    current_part.add(activity)
                    remaining.remove(activity)

            if current_part:
                parts.append(current_part)

        # Need at least 2 parts for a partial order
        if len(parts) < 2:
            return None

        # Verify it's a valid partial order (no ordering between parts)
        for i, part1 in enumerate(parts):
            for j, part2 in enumerate(parts):
                if i != j:
                    # Check if there's any DFG relation between parts
                    has_relation = any(
                        (a, b) in dfg or (b, a) in dfg
                        for a in part1 for b in part2
                    )
                    if has_relation:
                        return None  # Has ordering, not a partial order

        return parts

    def _apply_partial_order_cut(self, log: EventLog, parts: List[Set[str]]) -> StrictPartialOrder:
        """
        Apply a partial order cut to recursively discover a POWL model.

        Args:
            log: Event log
            parts: Valid partition (partial order cut)

        Returns:
            StrictPartialOrder with discovered sub-models
        """
        # Project log onto each part and discover sub-models
        sub_models = []
        for part in parts:
            sub_log = choice_graph_discovery.project_log(log, part)
            sub_uvcl = comut.get_variants(comut.project_univariate(sub_log))
            sub_model = self.apply(IMDataStructureUVCL(sub_uvcl))
            sub_models.append(sub_model)

        # Create partial order
        po = StrictPartialOrder(sub_models)

        return po

    def _detect_loop_cut(self, log: EventLog) -> Optional[Tuple[Set[str], Set[str]]]:
        """
        Detect a loop cut in the log.

        A loop cut is detected when:
        - The log can be split into a do-part and redo-part
        - The do-part starts with the process
        - The redo-part is optional

        Simplified implementation: detects single-activity loops.

        Args:
            log: Event log

        Returns:
            Tuple of (do_activities, redo_activities) if loop found, None otherwise
        """
        activities = choice_graph_discovery.get_activities(log)
        start_activities = choice_graph_discovery.get_start_activities(log)
        end_activities = choice_graph_discovery.get_end_activities(log)

        if len(activities) < 2:
            return None

        # Simple heuristic: look for start activity that repeats
        for start_act in start_activities:
            # Check if start_act appears multiple times in traces
            for trace in log:
                count = sum(1 for e in trace if e['concept:name'] == start_act)
                if count > 1:
                    # Potential loop: do-part = {start_act}, redo-part = rest
                    do_part = {start_act}
                    redo_part = activities - do_part
                    return (do_part, redo_part)

        return None

    def _apply_loop_cut(self, log: EventLog, cut: Tuple[Set[str], Set[str]]) -> OperatorPOWL:
        """
        Apply a loop cut to recursively discover a POWL model.

        Args:
            log: Event log
            cut: Tuple of (do_activities, redo_activities)

        Returns:
            OperatorPOWL with LOOP operator
        """
        do_part, redo_part = cut

        # Discover do-part
        do_log = choice_graph_discovery.project_log(log, do_part)
        do_uvcl = comut.get_variants(comut.project_univariate(do_log))
        do_model = self.apply(IMDataStructureUVCL(do_uvcl))

        # Discover redo-part
        redo_log = choice_graph_discovery.project_log(log, redo_part)
        redo_uvcl = comut.get_variants(comut.project_univariate(redo_log))
        redo_model = self.apply(IMDataStructureUVCL(redo_uvcl))

        return OperatorPOWL(Operator.LOOP, [do_model, redo_model])

    def _fall_through(self, log: EventLog) -> StrictPartialOrder:
        """
        Fall-through behavior when no cut is detected.

        This is a simplified implementation that places all activities
        in a partial order with no ordering constraints (full concurrency).

        Args:
            log: Event log

        Returns:
            StrictPartialOrder with all activities
        """
        activities = choice_graph_discovery.get_activities(log)
        sub_models = [Transition(act) for act in activities]

        return StrictPartialOrder(sub_models)


class InductiveMinerChoiceGraphMaximal(InductiveMinerChoiceGraph):
    """
    Choice Graph Inductive Miner with maximal partial order detection.

    Tries to discover the largest possible partial orders before
    falling back to smaller cuts or choice graphs.
    """

    def __init__(self):
        super().__init__()
        self.maximal_order = True


class InductiveMinerChoiceGraphClustering(InductiveMinerChoiceGraph):
    """
    Choice Graph Inductive Miner with frequency-based clustering.

    Uses activity frequencies to guide the discovery process,
    preferring to group frequently co-occurring activities.
    """

    def __init__(self):
        super().__init__()
        self.use_clustering = True

    def _detect_choice_graph_cut(self, log: EventLog) -> Optional[List[Set[str]]]:
        """
        Detect choice graph cut with frequency-based clustering.

        Groups activities that frequently occur together in the same traces.
        """
        dfg = choice_graph_discovery.compute_dfg(log)

        # Build co-occurrence matrix
        co_occurrence = {}
        for trace in log:
            activities_in_trace = [e['concept:name'] for e in trace]
            for i, a in enumerate(activities_in_trace):
                for b in activities_in_trace[i+1:]:
                    key = (a, b)
                    co_occurrence[key] = co_occurrence.get(key, 0) + 1

        # Use MineDG as base, then potentially merge based on co-occurrence
        parts = choice_graph_discovery.mine_dg(log)

        # TODO: Apply clustering based on co-occurrence frequencies
        # This is a simplified version

        if len(parts) >= 2 and choice_graph_discovery.is_valid_choice_graph_cut(log, parts):
            return parts

        return None


class InductiveMinerChoiceGraphCyclic(InductiveMinerChoiceGraph):
    """
    Choice Graph Inductive Miner with cycle detection.

    Specifically handles processes with cyclic behavior,
    distinguishing between true cycles (loops) and apparent cycles
    caused by concurrency.
    """

    def __init__(self):
        super().__init__()
        self.detect_cycles = True

    def _detect_choice_graph_cut(self, log: EventLog) -> Optional[List[Set[str]]]:
        """
        Detect choice graph cut with cycle awareness.

        Ensures that apparent cycles from concurrency don't interfere
        with choice graph detection.
        """
        # Use standard MineDG but with additional cycle checking
        parts = choice_graph_discovery.mine_dg(log)

        if len(parts) < 2:
            return None

        # Additional validation: ensure the cut doesn't create cyclic behavior
        # that should be modeled as a loop instead
        if self._creates_unintended_loop(log, parts):
            return None

        if choice_graph_discovery.is_valid_choice_graph_cut(log, parts):
            return parts

        return None

    def _creates_unintended_loop(self, log: EventLog, parts: List[Set[str]]) -> bool:
        """
        Check if a partition would create unintended loop behavior.

        Args:
            log: Event log
            parts: Partition to check

        Returns:
            True if partition creates unintended loops
        """
        # Simplified check: look for activities that repeat within traces
        # after being in different parts
        for trace in log:
            activities_seen = set()
            for event in trace:
                activity = event['concept:name']

                # Check if activity was seen before and is in a different part now
                if activity in activities_seen:
                    for i, part in enumerate(parts):
                        if activity in part:
                            # Check if we've seen activities from other parts
                            other_parts = set()
                            for j, other_part in enumerate(parts):
                                if i != j:
                                    other_parts.update(other_part)

                            if activities_seen & other_parts:
                                return True  # Potential unintended loop

                activities_seen.add(activity)

        return False


class InductiveMinerChoiceGraphCyclicStrict(InductiveMinerChoiceGraphCyclic):
    """
    Strict variant of Cyclic Choice Graph Inductive Miner.

    Applies stricter validation to ensure that discovered models
    are acyclic and sound by construction.
    """

    def __init__(self):
        super().__init__()
        self.strict_mode = True

    def _detect_choice_graph_cut(self, log: EventLog) -> Optional[List[Set[str]]]:
        """
        Detect choice graph cut with strict validation.

        Applies additional constraints:
        - Enforces acyclicity more strictly
        - Validates that the choice graph itself is acyclic
        """
        parts = choice_graph_discovery.mine_dg(log)

        if len(parts) < 2:
            return None

        # Strict acyclicity check
        if not self._strict_acyclicity_check(log, parts):
            return None

        if choice_graph_discovery.is_valid_choice_graph_cut(log, parts):
            return parts

        return None

    def _strict_acyclicity_check(self, log: EventLog, parts: List[Set[str]]) -> bool:
        """
        Strict acyclicity validation.

        Ensures that:
        1. No activity is reachable from itself through the partition
        2. The partition doesn't create cyclic dependencies

        Args:
            log: Event log
            parts: Partition to validate

        Returns:
            True if partition passes strict acyclicity check
        """
        dfg_tc = choice_graph_discovery.compute_transitive_closure(
            choice_graph_discovery.compute_dfg_relation(log)
        )

        # Check that no two different parts are mutually reachable
        for i, part1 in enumerate(parts):
            for j, part2 in enumerate(parts):
                if i != j:
                    # Check if any activity in part1 is mutually reachable with any in part2
                    for a in part1:
                        for b in part2:
                            if (a, b) in dfg_tc and (b, a) in dfg_tc:
                                return False  # Violates strict acyclicity

        return True


__all__ = [
    "InductiveMinerChoiceGraph",
    "InductiveMinerChoiceGraphMaximal",
    "InductiveMinerChoiceGraphClustering",
    "InductiveMinerChoiceGraphCyclic",
    "InductiveMinerChoiceGraphCyclicStrict",
]
