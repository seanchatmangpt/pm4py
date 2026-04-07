'''
PM4Py – A Process Mining Library for Python
Copyright (C) 2024 Process Intelligence Solutions GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see this software project's root or
visit <https://www.gnu.org/licenses/>.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
'''

import dspy


def get_judge_few_shot_demos():
    """Return few-shot examples for POWL quality judgment.

    These demos teach Dr. van der Aalst to provide specific, actionable feedback:

    Demo 1: CORRECT — Simple sequential workflow
        Teaches: Validate linear flow with proper termination

    Demo 2: DEADLOCK — XOR branch without terminal state
        Teaches: Detect when one XOR branch terminates but another doesn't
        Feedback: "The reject branch ends at 'Send Letter' with no terminal state"

    Demo 3: CORRECT — Nested XOR within PO
        Teaches: Validate proper nesting and XOR convergence
        Feedback: "Both branches converge to 'End', ensuring liveness"

    Demo 4: LIVENESS VIOLATION — Loop without escape
        Teaches: Detect infinite loops with no exit path
        Feedback: "The loop could execute forever without reaching completion"

    Demo 5: CORRECT — Loop with escape (retry pattern)
        Teaches: Validate proper retry/rework patterns
        Feedback: "The loop connects to 'Complete', providing an escape"

    Demo 6: ORPHANED NODE — Unreachable activity
        Teaches: Detect nodes declared but not connected to the flow
        Feedback: "Node 'D' is unreachable from start and cannot reach terminal state"

    Demo 7: SEMANTIC MISMATCH — PO used for mutually exclusive choice
        Teaches: Distinguish PO (all execute) from XOR (one executes)
        Feedback: "Context says 'either A OR B' — this is XOR, not PO"

    Demo 8: CORRECT — Parallel/concurrent activities in PO
        Teaches: Validate proper use of PO for concurrency
        Feedback: "No ordering between A and B — they can execute in parallel"

    Demo 9: DEADLOCK RISK — Nested XOR without outgoing edge
        Teaches: Detect hidden deadlocks in nested structures
        Feedback: "The XOR operator has no outgoing edge, creating a deadlock"

    Demo 10: CORRECT — Complex nested operators
        Teaches: Validate soundness in complex, multi-level nesting
        Feedback: "All execution paths reach 'End', no orphaned nodes"

    Each demo shows a POWL string, context, reasoning, and verdict.
    """
    demos = [
        # Demo 1: Correct simple sequential workflow
        dspy.Example(
            powl_string="PO=( nodes={ 'Submit Request', 'Review Request', 'Approve Request', 'Process Request' }, order={ 'Submit Request'-->'Review Request', 'Review Request'-->'Approve Request', 'Approve Request'-->'Process Request' } )",
            context_description="A simple approval workflow where requests are submitted, reviewed, approved, and processed in sequence.",
            reasoning="SYNTACTIC VALID: All visible transitions are single-quoted, PO syntax is correct. STRUCTURALLY SOUND: Linear sequential flow with no branches. Every node has exactly one successor except the last ('Process Request') which is terminal. No deadlocks possible in a linear chain. Liveness: Every execution path reaches the terminal state. MODELING QUALITY: Appropriate abstraction level for the described process. Activity names are meaningful and consistent.",
            verdict=True,
        ).with_inputs("powl_string", "context_description"),

        # Demo 2: Deadlock in XOR branch — one branch terminates, other doesn't
        dspy.Example(
            powl_string="X( PO=( nodes={ 'Approve', 'Disburse Funds', 'Complete' }, order={ 'Approve'-->'Disburse Funds', 'Disburse Funds'-->'Complete' } ), PO=( nodes={ 'Reject', 'Send Letter' }, order={ 'Reject'-->'Send Letter' } ) )",
            context_description="A loan approval process where approved loans are funded and completed, while rejected loans trigger a rejection letter.",
            reasoning="SYNTACTIC VALID: Syntax is correct. STRUCTURALLY UNSOUND: DEADLOCK DETECTED. The reject branch (right side of XOR) ends at 'Send Letter' with no terminal state. 'Send Letter' has no outgoing edge, creating a dead end. The approve branch (left side) properly terminates at 'Complete'. This violates the liveness property — not every execution path can reach a terminal state. The reject branch needs to connect to a terminal activity (e.g., 'Close Case').",
            verdict=False,
        ).with_inputs("powl_string", "context_description"),

        # Demo 3: Correct nested XOR within PO
        dspy.Example(
            powl_string="PO=( nodes={ 'Start', 'Process Data', X( 'Save', 'Discard' ), 'End' }, order={ 'Start'-->'Process Data', 'Process Data'-->X( 'Save', 'Discard' ), X( 'Save', 'Discard' )-->'End' } )",
            context_description="A data processing workflow where processed data can be either saved or discarded, then the workflow ends.",
            reasoning="SYNTACTIC VALID: XOR is properly nested within the PO node set. STRUCTURALLY SOUND: The XOR operator represents an exclusive choice between 'Save' and 'Discard'. Both branches of the XOR converge to the same successor ('End'), ensuring both paths reach a terminal state. No deadlocks: the XOR guarantees exactly one branch executes, and both lead to 'End'. Liveness: Every execution path reaches 'End'. MODELING QUALITY: Correct use of XOR for mutually exclusive alternatives.",
            verdict=True,
        ).with_inputs("powl_string", "context_description"),

        # Demo 4: Loop without escape — potential infinite loop
        dspy.Example(
            powl_string="PO=( nodes={ 'Receive Task', *( 'Process Task', 'Review Task' ) }, order={ 'Receive Task'-->*( 'Process Task', 'Review Task' ) } )",
            context_description="A task processing system where tasks are received, processed, reviewed, and can be sent back for reprocessing.",
            reasoning="SYNTACTIC VALID: Loop syntax *( 'do_part', 'redo_part' ) is correct. STRUCTURALLY QUESTIONABLE: LIVENESS VIOLATION. The loop operator *( 'Process Task', 'Review Task' ) allows 'Review Task' to transition back to 'Process Task' indefinitely. While loops are intentional in some processes (e.g., retry logic), this loop has no escape condition or terminal state. The process could loop forever without reaching completion. A proper loop should have an exit: either (a) the redo part should eventually lead to a terminal activity, or (b) the loop should be nested within a larger structure that provides an exit path.",
            verdict=False,
        ).with_inputs("powl_string", "context_description"),

        # Demo 5: Correct loop with escape — proper retry pattern
        dspy.Example(
            powl_string="PO=( nodes={ 'Receive Task', *( 'Process Task', 'Retry Task' ), 'Complete' }, order={ 'Receive Task'-->*( 'Process Task', 'Retry Task' ), *( 'Process Task', 'Retry Task' )-->'Complete' } )",
            context_description="A task processing system with retry capability. Tasks are processed, and if they fail, they can be retried before completion.",
            reasoning="SYNTACTIC VALID: Loop syntax is correct. STRUCTURALLY SOUND: The loop *( 'Process Task', 'Retry Task' ) models a retry pattern where 'Retry Task' can transition back to 'Process Task'. Crucially, the loop itself connects to 'Complete', providing an escape. The process can exit the loop by completing 'Process Task' without retrying, or by retrying some number of times and then completing. Liveness is satisfied because 'Complete' is reachable from the loop. This is a proper retry/rework pattern.",
            verdict=True,
        ).with_inputs("powl_string", "context_description"),

        # Demo 6: Orphaned node — unreachable activity
        dspy.Example(
            powl_string="PO=( nodes={ 'A', 'B', 'C', 'D' }, order={ 'A'-->'B', 'B'-->'C' } )",
            context_description="A process with four activities where A leads to B, B leads to C.",
            reasoning="SYNTACTIC VALID: Syntax is correct. STRUCTURALLY UNSOUND: ORPHANED NODE DETECTED. Node 'D' is declared in the node set but has no incoming or outgoing edges. It is unreachable from the start node 'A' and cannot reach any terminal state. This violates the proper completion property — every activity should be reachable from the start and should contribute to the process flow. If 'D' is not needed, it should be removed. If 'D' is part of the process, it needs proper connections.",
            verdict=False,
        ).with_inputs("powl_string", "context_description"),

        # Demo 7: Incorrect use of PO for mutually exclusive choices
        dspy.Example(
            powl_string="PO=( nodes={ 'Check Condition', 'Action A', 'Action B' }, order={ 'Check Condition'-->'Action A', 'Check Condition'-->'Action B' } )",
            context_description="A conditional process where after checking a condition, either Action A OR Action B is executed (not both).",
            reasoning="SYNTACTIC VALID: Syntax is correct. STRUCTURALLY QUESTIONABLE: SEMANTIC MISMATCH. In a Partial Order (PO), if a node has multiple outgoing edges (like 'Check Condition' → 'Action A' and 'Check Condition' → 'Action B'), BOTH successors must eventually complete. The PO semantics require all nodes in the order relation to execute. However, the context says 'either Action A OR Action B is executed (not both)' — this describes an EXCLUSIVE choice, not concurrent execution. The correct operator is X( 'Action A', 'Action B' ) for mutually exclusive alternatives. Using PO here would require both A and B to complete, which contradicts the process description.",
            verdict=False,
        ).with_inputs("powl_string", "context_description"),

        # Demo 8: Correct use of parallel PO
        dspy.Example(
            powl_string="PO=( nodes={ 'Start', 'Task A', 'Task B', 'Finalize' }, order={ 'Start'-->'Task A', 'Start'-->'Task B', 'Task A'-->'Finalize', 'Task B'-->'Finalize' } )",
            context_description="A parallel process where Task A and Task B execute concurrently after Start, and Finalize waits for both to complete.",
            reasoning="SYNTACTIC VALID: Syntax is correct. STRUCTURALLY SOUND: This is a proper use of Partial Order for concurrency. 'Start' has edges to both 'Task A' and 'Task B' with no ordering constraint between them — they can execute in parallel. Both 'Task A' and 'Task B' must complete before 'Finalize' (synchronization point). Liveness: All paths reach 'Finalize'. No deadlocks: The parallel structure correctly models concurrent execution with a join. MODELING QUALITY: Correct abstraction for parallel/concurrent activities.",
            verdict=True,
        ).with_inputs("powl_string", "context_description"),

        # Demo 9: Nested operators with hidden deadlock
        dspy.Example(
            powl_string="X( PO=( nodes={ 'Path A1', 'Path A2' }, order={ 'Path A1'-->'Path A2' } ), 'Path B' )",
            context_description="A process choosing between a two-step path (A1 then A2) and a single-step path (B).",
            reasoning="SYNTACTIC VALID: Syntax is correct. STRUCTURALLY QUESTIONABLE: DEADLOCK RISK. The left branch of the XOR is a PO with 'Path A1' → 'Path A2'. This PO terminates at 'Path A2'. The right branch is a single activity 'Path B'. The XOR operator itself has no outgoing edge, so neither branch leads to a terminal state. After executing either Path A2 or Path B, the process cannot continue. This creates a deadlock. The XOR should connect to a successor activity, or the activities within the XOR branches should themselves lead to a common terminal state.",
            verdict=False,
        ).with_inputs("powl_string", "context_description"),

        # Demo 10: Complex but sound — multiple nested operators
        dspy.Example(
            powl_string="PO=( nodes={ 'Begin', *( 'Step 1', 'Retry 1' ), X( PO=( nodes={ 'Path A', 'A1', 'A2' }, order={ 'Path A'-->'A1', 'A1'-->'A2' } ), PO=( nodes={ 'Path B', 'B1' }, order={ 'Path B'-->'B1' } ) ), 'End' }, order={ 'Begin'-->*( 'Step 1', 'Retry 1' ), *( 'Step 1', 'Retry 1' )-->X( PO=( nodes={ 'Path A', 'A1', 'A2' }, order={ 'Path A'-->'A1', 'A1'-->'A2' } ), PO=( nodes={ 'Path B', 'B1' }, order={ 'Path B'-->'B1' } ) ), X( PO=( nodes={ 'Path A', 'A1', 'A2' }, order={ 'Path A'-->'A1', 'A1'-->'A2' } ), PO=( nodes={ 'Path B', 'B1' }, order={ 'Path B'-->'B1' } ) )-->'End' } )",
            context_description="A complex workflow with retry logic (loop), followed by a choice between two paths (XOR), where one path has multiple steps and the other has a single step, converging to a common end.",
            reasoning="SYNTACTIC VALID: All operators correctly nested. Loop *( 'Step 1', 'Retry 1' ) can retry Step 1. XOR chooses between Path A (3 steps) and Path B (2 steps). STRUCTURALLY SOUND: (1) Loop has escape: 'Step 1' can complete and exit the loop without retrying. (2) XOR both branches converge to 'End': after 'A2' or 'B1', both lead to 'End' via the XOR edge. (3) No dead ends: all terminal activities ('A2', 'B1', 'End') are properly connected. (4) No orphaned nodes. Liveness: Every execution path reaches 'End'. MODELING QUALITY: Appropriate complexity for the described process. The nesting correctly captures the process structure.",
            verdict=True,
        ).with_inputs("powl_string", "context_description"),

        # Demo 11: Correct POWL with constructive feedback (using real analysis)
        dspy.Example(
            powl_string="PO=( nodes={ 'Start', 'Process Data', X( 'Approve', 'Reject' ), 'End' }, order={ 'Start'-->'Process Data', 'Process Data'-->X( 'Approve', 'Reject' ), X( 'Approve', 'Reject' )-->'End' } )",
            context_description="A simple approval process: start, process data, approve or reject, then end.",
            reasoning="SYNTACTIC VALID: Syntax is correct. STRUCTURAL SOUND: Linear flow with a single XOR decision. Both 'Approve' and 'Reject' branches converge to 'End', ensuring all execution paths reach a terminal state. No deadlocks, no orphaned nodes. Liveness satisfied. MODELING QUALITY: Appropriate abstraction. However, the model could be enhanced by adding detail to what happens after approval (e.g., 'Notify User') vs rejection (e.g., 'Log Rejection'). Current structure is sound but minimal.",
            verdict=True,
        ).with_inputs("powl_string", "context_description"),

        # Demo 12: Incorrect POWL with analysis-based feedback (orphaned node detected)
        dspy.Example(
            powl_string="X( 'Start Task', PO=( nodes={ 'Task A', 'Task B', 'Task C' }, order={ 'Task A'-->'Task B' } ), 'Complete' )",
            context_description="A process that starts a task, does A and B in some order, then completes. Task C is also available but not connected.",
            reasoning="SYNTACTIC VALID: Syntax is correct. STRUCTURALLY UNSOUND: ORPHANED NODE DETECTED by real analysis. 'Task C' is declared in the PO node set but has no incoming or outgoing edges in the order relation. It is unreachable from 'Start Task' and cannot reach 'Complete'. Additionally, the PO structure has 'Task A' → 'Task B' but no edges from the PO to 'Complete', creating a dead end. The model needs: (1) Remove 'Task C' if not used, or connect it properly. (2) Add edge from PO (or its final node) to 'Complete'. (3) Ensure both XOR branches lead to terminal state.",
            verdict=False,
        ).with_inputs("powl_string", "context_description"),
    ]

    return demos
