"""
PM4Py – A Process Mining Library for Python
Copyright (C) 2024 Process Intelligence Solutions

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
"""



import dspy


def get_nl_few_shot_demos():
    """Return few-shot examples for natural language -> POWL generation.

    These demos teach the agent to:
    1. Use X() for exclusive choices (not multiple edges in PO)
    2. Use *() for retry/rework loops
    3. Ensure every branch leads to completion (no dead ends)
    4. Nest X() inside PO for decision points within a workflow
    5. Handle optional/alternative paths correctly
    6. Incorporate judge feedback to fix structural issues (deadlock, liveness)

    Demo 5 specifically shows the refinement loop pattern:
    - Initial POWL with structural issues (dead ends, incomplete paths)
    - Judge's reasoning about what's wrong
    - Refined POWL that addresses those issues
    This teaches the agent how to respond when Dr. van der Aalst rejects a model.
    """
    demos = [
        # Demo 1: Simple loan approval with XOR choice
        dspy.Example(
            process_description=(
                "A bank processes loan applications. The customer submits an application. "
                "A clerk reviews the documents. If the documents are incomplete, the clerk "
                "requests additional documents and the customer resubmits. Once documents "
                "are complete, the clerk forwards to an underwriter. The underwriter either "
                "approves or rejects the loan. If approved, the funds are disbursed and "
                "the case is closed. If rejected, a rejection letter is sent and the case "
                "is closed."
            ),
            trajectory=[
                {
                    "reasoning": "This process has a loop (request/resubmit documents) and "
                    "an XOR choice (approve/reject). The loop uses *() with 'request docs' "
                    "as redo. The approve/reject is X() since exactly one branch executes.",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "PO=( nodes={ 'Submit Application', 'Review Documents', 'Forward to Underwriter', 'Approve Loan', 'Reject Loan', 'Disburse Funds', 'Send Rejection Letter', 'Close Case' }, order={ 'Submit Application'-->'Review Documents', 'Review Documents'-->'Forward to Underwriter', 'Forward to Underwriter'-->X( 'Approve Loan', 'Reject Loan' ), X( 'Approve Loan', 'Reject Loan' )-->*( 'Close Case', 'Request Docs' ), 'Approve Loan'-->'Disburse Funds', 'Disburse Funds'-->'Close Case', 'Reject Loan'-->'Send Rejection Letter', 'Send Rejection Letter'-->'Close Case' } )"},
                    "is_valid": False,
                    "errors": "Parse error: operators cannot be used as edge endpoints in PO order",
                },
                {
                    "reasoning": "Can't use X() as a node in PO edges. Instead, nest the "
                    "XOR inside the PO structure. The underwriter decision should be modeled "
                    "as a node in the PO with X() handling the branch logic. Let me use a "
                    "cleaner approach: PO for the sequential flow, X() for the decision.",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "X( "
                        "*( 'Submit Application', 'Request Docs' ), "
                        "PO=( nodes={ 'Review Documents', 'Forward to Underwriter' }, order={ 'Review Documents'-->'Forward to Underwriter' } ), "
                        "X( "
                            "PO=( nodes={ 'Approve Loan', 'Disburse Funds', 'Close Case' }, order={ 'Approve Loan'-->'Disburse Funds', 'Disburse Funds'-->'Close Case' } ), "
                            "PO=( nodes={ 'Reject Loan', 'Send Rejection Letter', 'Close Case' }, order={ 'Reject Loan'-->'Send Rejection Letter', 'Send Rejection Letter'-->'Close Case' } ) "
                        ") "
                    ")"},
                    "is_valid": False,
                    "errors": "Parse error",
                },
                {
                    "reasoning": "The nesting is getting too complex. Let me use a simpler "
                    "structure. The main flow is sequential with a loop for doc requests "
                    "and an XOR for the underwriter decision. Use PO for the main flow, "
                    "X() for the decision point as a separate element.",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "PO=( "
                        "nodes={ "
                            "'Submit Application', "
                            "*( 'Review Documents', 'Request Docs' ), "
                            "'Forward to Underwriter', "
                            "X( "
                                "PO=( nodes={ 'Approve Loan', 'Disburse Funds', 'Close Case' }, "
                                    "order={ 'Approve Loan'-->'Disburse Funds', 'Disburse Funds'-->'Close Case' } ), "
                                "PO=( nodes={ 'Reject Loan', 'Send Rejection Letter', 'Close Case' }, "
                                    "order={ 'Reject Loan'-->'Send Rejection Letter', 'Send Rejection Letter'-->'Close Case' } ) "
                            ") "
                        "}, "
                        "order={ "
                            "'Submit Application'-->*( 'Review Documents', 'Request Docs' ), "
                            "*( 'Review Documents', 'Request Docs' )-->'Forward to Underwriter', "
                            "'Forward to Underwriter'-->X( "
                                "PO=( nodes={ 'Approve Loan', 'Disburse Funds', 'Close Case' }, "
                                    "order={ 'Approve Loan'-->'Disburse Funds', 'Disburse Funds'-->'Close Case' } ), "
                                "PO=( nodes={ 'Reject Loan', 'Send Rejection Letter', 'Close Case' }, "
                                    "order={ 'Reject Loan'-->'Send Rejection Letter', 'Send Rejection Letter'-->'Close Case' } ) "
                            ") "
                        "} "
                    ")"},
                    "is_valid": True,
                    "errors": None,
                },
                {
                    "reasoning": "Valid POWL with correct structure: loop for doc requests, "
                    "XOR for approve/reject decision, both branches lead to Close Case.",
                    "selected_fn": "finish",
                    "args": {"powl_model": "PO=( "
                        "nodes={ "
                            "'Submit Application', "
                            "*( 'Review Documents', 'Request Docs' ), "
                            "'Forward to Underwriter', "
                            "X( "
                                "PO=( nodes={ 'Approve Loan', 'Disburse Funds', 'Close Case' }, "
                                    "order={ 'Approve Loan'-->'Disburse Funds', 'Disburse Funds'-->'Close Case' } ), "
                                "PO=( nodes={ 'Reject Loan', 'Send Rejection Letter', 'Close Case' }, "
                                    "order={ 'Reject Loan'-->'Send Rejection Letter', 'Send Rejection Letter'-->'Close Case' } ) "
                            ") "
                        "}, "
                        "order={ "
                            "'Submit Application'-->*( 'Review Documents', 'Request Docs' ), "
                            "*( 'Review Documents', 'Request Docs' )-->'Forward to Underwriter', "
                            "'Forward to Underwriter'-->X( "
                                "PO=( nodes={ 'Approve Loan', 'Disburse Funds', 'Close Case' }, "
                                    "order={ 'Approve Loan'-->'Disburse Funds', 'Disburse Funds'-->'Close Case' } ), "
                                "PO=( nodes={ 'Reject Loan', 'Send Rejection Letter', 'Close Case' }, "
                                    "order={ 'Reject Loan'-->'Send Rejection Letter', 'Send Rejection Letter'-->'Close Case' } ) "
                            ") "
                        "} "
                    ")"},
                    "return_value": "PO=( nodes={ 'Submit Application', *( 'Review Documents', 'Request Docs' ), 'Forward to Underwriter', X( PO=( nodes={ 'Approve Loan', 'Disburse Funds', 'Close Case' }, order={ 'Approve Loan'-->'Disburse Funds', 'Disburse Funds'-->'Close Case' } ), PO=( nodes={ 'Reject Loan', 'Send Rejection Letter', 'Close Case' }, order={ 'Reject Loan'-->'Send Rejection Letter', 'Send Rejection Letter'-->'Close Case' } ) ) }, order={ 'Submit Application'-->*( 'Review Documents', 'Request Docs' ), *( 'Review Documents', 'Request Docs' )-->'Forward to Underwriter', 'Forward to Underwriter'-->X( PO=( nodes={ 'Approve Loan', 'Disburse Funds', 'Close Case' }, order={ 'Approve Loan'-->'Disburse Funds', 'Disburse Funds'-->'Close Case' } ), PO=( nodes={ 'Reject Loan', 'Send Rejection Letter', 'Close Case' }, order={ 'Reject Loan'-->'Send Rejection Letter', 'Send Rejection Letter'-->'Close Case' } ) ) } )",
                    "errors": None,
                },
            ],
            next_selected_fn="finish",
            args={"powl_model": "PO=( nodes={ 'Submit Application', *( 'Review Documents', 'Request Docs' ), 'Forward to Underwriter', X( PO=( nodes={ 'Approve Loan', 'Disburse Funds', 'Close Case' }, order={ 'Approve Loan'-->'Disburse Funds', 'Disburse Funds'-->'Close Case' } ), PO=( nodes={ 'Reject Loan', 'Send Rejection Letter', 'Close Case' }, order={ 'Reject Loan'-->'Send Rejection Letter', 'Send Rejection Letter'-->'Close Case' } ) ) }, order={ 'Submit Application'-->*( 'Review Documents', 'Request Docs' ), *( 'Review Documents', 'Request Docs' )-->'Forward to Underwriter', 'Forward to Underwriter'-->X( PO=( nodes={ 'Approve Loan', 'Disburse Funds', 'Close Case' }, order={ 'Approve Loan'-->'Disburse Funds', 'Disburse Funds'-->'Close Case' } ), PO=( nodes={ 'Reject Loan', 'Send Rejection Letter', 'Close Case' }, order={ 'Reject Loan'-->'Send Rejection Letter', 'Send Rejection Letter'-->'Close Case' } ) ) } )"},
        ),
        # Demo 2: Software release process with multiple XOR decisions
        dspy.Example(
            process_description=(
                "A software team follows this release process: A developer writes code "
                "and submits a pull request. Code review is performed. If review finds "
                "issues, the developer fixes them and resubmits. If review passes, CI/CD "
                "runs automated tests. If tests fail, the developer fixes and resubmits. "
                "If tests pass, a release manager approves the release. The release is "
                "then deployed to staging. After staging verification, it's deployed to "
                "production. Sometimes the release manager rejects the release, in which "
                "case the developer must start over with a new pull request."
            ),
            trajectory=[
                {
                    "reasoning": "Two loops here: code review fixes and test fixes. Plus an "
                    "XOR for approve/reject release. Key: both loops use *() and the "
                    "approve/reject uses X(). Every path must reach a terminal state.",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "PO=( "
                        "nodes={ "
                            "'Write Code', "
                            "*( 'Submit PR', 'Fix Review Issues' ), "
                            "'Code Review', "
                            "*( 'Run Tests', 'Fix Test Failures' ), "
                            "'Approve Release', "
                            "'Deploy to Staging', "
                            "'Verify Staging', "
                            "'Deploy to Production' "
                        "}, "
                        "order={ "
                            "'Write Code'-->*( 'Submit PR', 'Fix Review Issues' ), "
                            "*( 'Submit PR', 'Fix Review Issues' )-->'Code Review', "
                            "'Code Review'-->*( 'Run Tests', 'Fix Test Failures' ), "
                            "*( 'Run Tests', 'Fix Test Failures' )-->'Approve Release', "
                            "'Approve Release'-->'Deploy to Staging', "
                            "'Deploy to Staging'-->'Verify Staging', "
                            "'Verify Staging'-->'Deploy to Production' "
                        "} "
                    ")"},
                    "is_valid": True,
                    "errors": None,
                },
                {
                    "reasoning": "Valid but missing the rejection path. The description says "
                    "'sometimes the release manager rejects the release, in which case the "
                    "developer must start over with a new pull request.' Need X() for "
                    "approve/reject. The reject branch loops back to Write Code.",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "PO=( "
                        "nodes={ "
                            "'Write Code', "
                            "*( 'Submit PR', 'Fix Review Issues' ), "
                            "'Code Review', "
                            "*( 'Run Tests', 'Fix Test Failures' ), "
                            "X( "
                                "PO=( nodes={ 'Approve Release', 'Deploy to Staging', 'Verify Staging', 'Deploy to Production' }, "
                                    "order={ 'Approve Release'-->'Deploy to Staging', 'Deploy to Staging'-->'Verify Staging', 'Verify Staging'-->'Deploy to Production' } ), "
                                "'Write Code' "
                            ") "
                        "}, "
                        "order={ "
                            "'Write Code'-->*( 'Submit PR', 'Fix Review Issues' ), "
                            "*( 'Submit PR', 'Fix Review Issues' )-->'Code Review', "
                            "'Code Review'-->*( 'Run Tests', 'Fix Test Failures' ), "
                            "*( 'Run Tests', 'Fix Test Failures' )-->X( "
                                "PO=( nodes={ 'Approve Release', 'Deploy to Staging', 'Verify Staging', 'Deploy to Production' }, "
                                    "order={ 'Approve Release'-->'Deploy to Staging', 'Deploy to Staging'-->'Verify Staging', 'Verify Staging'-->'Deploy to Production' } ), "
                                "'Write Code' "
                            ") "
                        "} "
                    ")"},
                    "is_valid": True,
                    "errors": None,
                },
                {
                    "reasoning": "Valid POWL with all paths covered: two loops for review/test "
                    "fixes, XOR for approve (leads to production) vs reject (loops back to "
                    "write code). Every execution path terminates.",
                    "selected_fn": "finish",
                    "args": {"powl_model": "PO=( "
                        "nodes={ "
                            "'Write Code', "
                            "*( 'Submit PR', 'Fix Review Issues' ), "
                            "'Code Review', "
                            "*( 'Run Tests', 'Fix Test Failures' ), "
                            "X( "
                                "PO=( nodes={ 'Approve Release', 'Deploy to Staging', 'Verify Staging', 'Deploy to Production' }, "
                                    "order={ 'Approve Release'-->'Deploy to Staging', 'Deploy to Staging'-->'Verify Staging', 'Verify Staging'-->'Deploy to Production' } ), "
                                "'Write Code' "
                            ") "
                        "}, "
                        "order={ "
                            "'Write Code'-->*( 'Submit PR', 'Fix Review Issues' ), "
                            "*( 'Submit PR', 'Fix Review Issues' )-->'Code Review', "
                            "'Code Review'-->*( 'Run Tests', 'Fix Test Failures' ), "
                            "*( 'Run Tests', 'Fix Test Failures' )-->X( "
                                "PO=( nodes={ 'Approve Release', 'Deploy to Staging', 'Verify Staging', 'Deploy to Production' }, "
                                    "order={ 'Approve Release'-->'Deploy to Staging', 'Deploy to Staging'-->'Verify Staging', 'Verify Staging'-->'Deploy to Production' } ), "
                                "'Write Code' "
                            ") "
                        "} "
                    ")"},
                    "return_value": "PO=( nodes={ 'Write Code', *( 'Submit PR', 'Fix Review Issues' ), 'Code Review', *( 'Run Tests', 'Fix Test Failures' ), X( PO=( nodes={ 'Approve Release', 'Deploy to Staging', 'Verify Staging', 'Deploy to Production' }, order={ 'Approve Release'-->'Deploy to Staging', 'Deploy to Staging'-->'Verify Staging', 'Verify Staging'-->'Deploy to Production' } ), 'Write Code' ) }, order={ 'Write Code'-->*( 'Submit PR', 'Fix Review Issues' ), *( 'Submit PR', 'Fix Review Issues' )-->'Code Review', 'Code Review'-->*( 'Run Tests', 'Fix Test Failures' ), *( 'Run Tests', 'Fix Test Failures' )-->X( PO=( nodes={ 'Approve Release', 'Deploy to Staging', 'Verify Staging', 'Deploy to Production' }, order={ 'Approve Release'-->'Deploy to Staging', 'Deploy to Staging'-->'Verify Staging', 'Verify Staging'-->'Deploy to Production' } ), 'Write Code' ) } )",
                    "errors": None,
                },
            ],
            next_selected_fn="finish",
            args={"powl_model": "PO=( nodes={ 'Write Code', *( 'Submit PR', 'Fix Review Issues' ), 'Code Review', *( 'Run Tests', 'Fix Test Failures' ), X( PO=( nodes={ 'Approve Release', 'Deploy to Staging', 'Verify Staging', 'Deploy to Production' }, order={ 'Approve Release'-->'Deploy to Staging', 'Deploy to Staging'-->'Verify Staging', 'Verify Staging'-->'Deploy to Production' } ), 'Write Code' ) }, order={ 'Write Code'-->*( 'Submit PR', 'Fix Review Issues' ), *( 'Submit PR', 'Fix Review Issues' )-->'Code Review', 'Code Review'-->*( 'Run Tests', 'Fix Test Failures' ), *( 'Run Tests', 'Fix Test Failures' )-->X( PO=( nodes={ 'Approve Release', 'Deploy to Staging', 'Verify Staging', 'Deploy to Production' }, order={ 'Approve Release'-->'Deploy to Staging', 'Deploy to Staging'-->'Verify Staging', 'Verify Staging'-->'Deploy to Production' } ), 'Write Code' ) } )"},
        ),
        # Demo 3: E-commerce order fulfillment with parallel activities
        dspy.Example(
            process_description=(
                "An e-commerce company processes orders: Customer places an order. "
                "The order is validated (check inventory, verify payment). If invalid, "
                "the order is cancelled and the customer is notified. If valid, the "
                "warehouse picks and packs the items while billing generates an invoice "
                "(these happen in parallel). Once both are done, shipping dispatches "
                "the package. The customer receives the order. Optionally, the customer "
                "may return items, which triggers a refund process."
            ),
            trajectory=[
                {
                    "reasoning": "Key patterns: XOR for valid/invalid, PO for parallel "
                    "(pick+pack AND billing), optional return via XOR at the end. "
                    "Parallel activities have no ordering constraint between them in PO.",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "X( "
                        "'Cancel Order', "
                        "PO=( "
                            "nodes={ "
                                "'Place Order', "
                                "'Validate Order', "
                                "'Pick Items', "
                                "'Pack Items', "
                                "'Generate Invoice', "
                                "'Dispatch Package', "
                                "'Receive Order', "
                                "X( 'Return Items', tau ) "
                            "}, "
                            "order={ "
                                "'Place Order'-->'Validate Order', "
                                "'Validate Order'-->'Pick Items', "
                                "'Validate Order'-->'Generate Invoice', "
                                "'Pick Items'-->'Pack Items', "
                                "'Pack Items'-->'Dispatch Package', "
                                "'Generate Invoice'-->'Dispatch Package', "
                                "'Dispatch Package'-->'Receive Order', "
                                "'Receive Order'-->X( 'Return Items', tau ) "
                            "} "
                        ") "
                    ")"},
                    "is_valid": True,
                    "errors": None,
                },
                {
                    "reasoning": "Valid. The model correctly shows: XOR for valid/cancel, "
                    "parallel pick+pack and billing (no ordering between them, both must "
                    "complete before dispatch), optional return at the end.",
                    "selected_fn": "finish",
                    "args": {"powl_model": "X( "
                        "'Cancel Order', "
                        "PO=( "
                            "nodes={ "
                                "'Place Order', "
                                "'Validate Order', "
                                "'Pick Items', "
                                "'Pack Items', "
                                "'Generate Invoice', "
                                "'Dispatch Package', "
                                "'Receive Order', "
                                "X( 'Return Items', tau ) "
                            "}, "
                            "order={ "
                                "'Place Order'-->'Validate Order', "
                                "'Validate Order'-->'Pick Items', "
                                "'Validate Order'-->'Generate Invoice', "
                                "'Pick Items'-->'Pack Items', "
                                "'Pack Items'-->'Dispatch Package', "
                                "'Generate Invoice'-->'Dispatch Package', "
                                "'Dispatch Package'-->'Receive Order', "
                                "'Receive Order'-->X( 'Return Items', tau ) "
                            "} "
                        ") "
                    ")"},
                    "return_value": "X( 'Cancel Order', PO=( nodes={ 'Place Order', 'Validate Order', 'Pick Items', 'Pack Items', 'Generate Invoice', 'Dispatch Package', 'Receive Order', X( 'Return Items', tau ) }, order={ 'Place Order'-->'Validate Order', 'Validate Order'-->'Pick Items', 'Validate Order'-->'Generate Invoice', 'Pick Items'-->'Pack Items', 'Pack Items'-->'Dispatch Package', 'Generate Invoice'-->'Dispatch Package', 'Dispatch Package'-->'Receive Order', 'Receive Order'-->X( 'Return Items', tau ) } ) )",
                    "errors": None,
                },
            ],
            next_selected_fn="finish",
            args={"powl_model": "X( 'Cancel Order', PO=( nodes={ 'Place Order', 'Validate Order', 'Pick Items', 'Pack Items', 'Generate Invoice', 'Dispatch Package', 'Receive Order', X( 'Return Items', tau ) }, order={ 'Place Order'-->'Validate Order', 'Validate Order'-->'Pick Items', 'Validate Order'-->'Generate Invoice', 'Pick Items'-->'Pack Items', 'Pack Items'-->'Dispatch Package', 'Generate Invoice'-->'Dispatch Package', 'Dispatch Package'-->'Receive Order', 'Receive Order'-->X( 'Return Items', tau ) } ) )"},
        ),
        # Demo 4: Human-in-the-Swarm multi-agent orchestration with A2A + MCP
        # Models a complex process with multiple XOR decisions, escalation loops,
        # reconciliation loops, and human-in-the-loop approval
        dspy.Example(
            process_description=(
                "Human-in-the-Swarm Multi-Agent Orchestration Process: "
                "1. A human operator submits a task request to the swarm orchestrator. "
                "2. The orchestrator analyzes the task and determines which agents are needed. "
                "3. The orchestrator broadcasts the task to available agents via A2A protocol. "
                "4. Each agent acknowledges receipt and reports capabilities via MCP tool discovery. "
                "5. The orchestrator assigns subtasks to agents based on capabilities. "
                "6. Agents execute subtasks. During execution an agent may delegate to another "
                "agent via A2A, request tools via MCP, or report errors to the orchestrator. "
                "7. The orchestrator monitors heartbeats. If an agent goes silent, it escalates "
                "to the human operator who decides to reassign, retry, or cancel. "
                "8. As agents complete, they publish results via A2A event broadcast. "
                "9. The orchestrator aggregates partial results and performs a consistency check. "
                "10. If inconsistencies are found, conflicting agents re-execute with updated "
                "context and results are re-aggregated until consistent. "
                "11. The orchestrator submits the final result to the human for review. "
                "12. The human either approves (task archived) or requests revision (specific "
                "subtasks re-dispatched with feedback, looping back to execution). "
                "13. Optionally, the human may send a direct command to a specific agent via "
                "A2A, bypassing the orchestrator."
            ),
            trajectory=[
                {
                    "reasoning": "This is a complex process with multiple decision points. "
                    "Key XOR decisions: (1) publish results vs escalate to human, "
                    "(2) consistency pass vs re-execute, (3) human approve vs revise, "
                    "(4) human decision on escalation (reassign/retry vs cancel). "
                    "Loops: consistency reconciliation, revision re-dispatch, heartbeat escalation. "
                    "Using a single PO with nested X() operators for each decision point.",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "PO=( "
                        "nodes={ "
                            "'Submit Task Request', "
                            "'Analyze Task', "
                            "'Broadcast Task', "
                            "'Agent Ack & Report Capabilities', "
                            "'Assign Subtasks', "
                            "'Execute Subtasks', "
                            "'Monitor Heartbeats', "
                            "'Publish Results', "
                            "'Aggregate Results', "
                            "'Consistency Check', "
                            "'Submit Final Result', "
                            "'Approve or Revise', "
                            "'Approve', "
                            "'Mark Complete', "
                            "'Archive', "
                            "'Escalate to Human', "
                            "'Human Decision', "
                            "'Reassign/Retry', "
                            "'Cancel', "
                            "'Cancel Subtask' "
                        "}, "
                        "order={ "
                            "'Submit Task Request'-->'Analyze Task', "
                            "'Analyze Task'-->'Broadcast Task', "
                            "'Broadcast Task'-->'Agent Ack & Report Capabilities', "
                            "'Agent Ack & Report Capabilities'-->'Assign Subtasks', "
                            "'Assign Subtasks'-->'Execute Subtasks', "
                            "'Execute Subtasks'-->'Monitor Heartbeats', "
                            "'Monitor Heartbeats'-->X( 'Publish Results', 'Escalate to Human' ), "
                            "'Publish Results'-->'Aggregate Results', "
                            "'Aggregate Results'-->'Consistency Check', "
                            "'Consistency Check'-->X( 'Submit Final Result', 'Execute Subtasks' ), "
                            "'Submit Final Result'-->'Approve or Revise', "
                            "'Approve or Revise'-->X( 'Approve', 'Reassign/Retry' ), "
                            "'Approve'-->'Mark Complete', "
                            "'Mark Complete'-->'Archive', "
                            "'Reassign/Retry'-->'Execute Subtasks', "
                            "'Escalate to Human'-->'Human Decision', "
                            "'Human Decision'-->X( 'Reassign/Retry', 'Cancel' ), "
                            "'Cancel'-->'Cancel Subtask' "
                        "} "
                    ")"},
                    "is_valid": True,
                    "errors": None,
                },
                {
                    "reasoning": "Valid POWL with 21 activities. All XOR decisions correctly "
                    "capture mutually exclusive alternatives. The consistency check loop "
                    "goes back to Execute Subtasks (not a dead end). Both Cancel Subtask "
                    "and Archive are terminal states. The escalation path (heartbeat failure) "
                    "leads to human decision with reassign/retry looping back to execution.",
                    "selected_fn": "finish",
                    "args": {"powl_model": "PO=( "
                        "nodes={ "
                            "'Submit Task Request', "
                            "'Analyze Task', "
                            "'Broadcast Task', "
                            "'Agent Ack & Report Capabilities', "
                            "'Assign Subtasks', "
                            "'Execute Subtasks', "
                            "'Monitor Heartbeats', "
                            "'Publish Results', "
                            "'Aggregate Results', "
                            "'Consistency Check', "
                            "'Submit Final Result', "
                            "'Approve or Revise', "
                            "'Approve', "
                            "'Mark Complete', "
                            "'Archive', "
                            "'Escalate to Human', "
                            "'Human Decision', "
                            "'Reassign/Retry', "
                            "'Cancel', "
                            "'Cancel Subtask' "
                        "}, "
                        "order={ "
                            "'Submit Task Request'-->'Analyze Task', "
                            "'Analyze Task'-->'Broadcast Task', "
                            "'Broadcast Task'-->'Agent Ack & Report Capabilities', "
                            "'Agent Ack & Report Capabilities'-->'Assign Subtasks', "
                            "'Assign Subtasks'-->'Execute Subtasks', "
                            "'Execute Subtasks'-->'Monitor Heartbeats', "
                            "'Monitor Heartbeats'-->X( 'Publish Results', 'Escalate to Human' ), "
                            "'Publish Results'-->'Aggregate Results', "
                            "'Aggregate Results'-->'Consistency Check', "
                            "'Consistency Check'-->X( 'Submit Final Result', 'Execute Subtasks' ), "
                            "'Submit Final Result'-->'Approve or Revise', "
                            "'Approve or Revise'-->X( 'Approve', 'Reassign/Retry' ), "
                            "'Approve'-->'Mark Complete', "
                            "'Mark Complete'-->'Archive', "
                            "'Reassign/Retry'-->'Execute Subtasks', "
                            "'Escalate to Human'-->'Human Decision', "
                            "'Human Decision'-->X( 'Reassign/Retry', 'Cancel' ), "
                            "'Cancel'-->'Cancel Subtask' "
                        "} "
                    ")"},
                    "return_value": "PO=( nodes={ 'Submit Task Request', 'Analyze Task', 'Broadcast Task', 'Agent Ack & Report Capabilities', 'Assign Subtasks', 'Execute Subtasks', 'Monitor Heartbeats', 'Publish Results', 'Aggregate Results', 'Consistency Check', 'Submit Final Result', 'Approve or Revise', 'Approve', 'Mark Complete', 'Archive', 'Escalate to Human', 'Human Decision', 'Reassign/Retry', 'Cancel', 'Cancel Subtask' }, order={ 'Submit Task Request'-->'Analyze Task', 'Analyze Task'-->'Broadcast Task', 'Broadcast Task'-->'Agent Ack & Report Capabilities', 'Agent Ack & Report Capabilities'-->'Assign Subtasks', 'Assign Subtasks'-->'Execute Subtasks', 'Execute Subtasks'-->'Monitor Heartbeats', 'Monitor Heartbeats'-->X( 'Publish Results', 'Escalate to Human' ), 'Publish Results'-->'Aggregate Results', 'Aggregate Results'-->'Consistency Check', 'Consistency Check'-->X( 'Submit Final Result', 'Execute Subtasks' ), 'Submit Final Result'-->'Approve or Revise', 'Approve or Revise'-->X( 'Approve', 'Reassign/Retry' ), 'Approve'-->'Mark Complete', 'Mark Complete'-->'Archive', 'Reassign/Retry'-->'Execute Subtasks', 'Escalate to Human'-->'Human Decision', 'Human Decision'-->X( 'Reassign/Retry', 'Cancel' ), 'Cancel'-->'Cancel Subtask' } )",
                    "errors": None,
                },
            ],
            next_selected_fn="finish",
            args={"powl_model": "PO=( nodes={ 'Submit Task Request', 'Analyze Task', 'Broadcast Task', 'Agent Ack & Report Capabilities', 'Assign Subtasks', 'Execute Subtasks', 'Monitor Heartbeats', 'Publish Results', 'Aggregate Results', 'Consistency Check', 'Submit Final Result', 'Approve or Revise', 'Approve', 'Mark Complete', 'Archive', 'Escalate to Human', 'Human Decision', 'Reassign/Retry', 'Cancel', 'Cancel Subtask' }, order={ 'Submit Task Request'-->'Analyze Task', 'Analyze Task'-->'Broadcast Task', 'Broadcast Task'-->'Agent Ack & Report Capabilities', 'Agent Ack & Report Capabilities'-->'Assign Subtasks', 'Assign Subtasks'-->'Execute Subtasks', 'Execute Subtasks'-->'Monitor Heartbeats', 'Monitor Heartbeats'-->X( 'Publish Results', 'Escalate to Human' ), 'Publish Results'-->'Aggregate Results', 'Aggregate Results'-->'Consistency Check', 'Consistency Check'-->X( 'Submit Final Result', 'Execute Subtasks' ), 'Submit Final Result'-->'Approve or Revise', 'Approve or Revise'-->X( 'Approve', 'Reassign/Retry' ), 'Approve'-->'Mark Complete', 'Mark Complete'-->'Archive', 'Reassign/Retry'-->'Execute Subtasks', 'Escalate to Human'-->'Human Decision', 'Human Decision'-->X( 'Reassign/Retry', 'Cancel' ), 'Cancel'-->'Cancel Subtask' } )"},
        ),
        # Demo 5: Judge rejection and refinement loop
        # Shows how to incorporate Dr. van der Aalst's feedback to fix
        # structural issues (dead ends, unreachable nodes, deadlock risk)
        dspy.Example(
            process_description=(
                "A healthcare patient intake process: Patient arrives and checks in. "
                "A nurse takes vital signs (blood pressure, temperature, heart rate). "
                "If vitals are abnormal, the doctor is notified immediately for urgent "
                "consultation. If vitals are normal, the patient waits in the waiting room "
                "until a doctor is available. The doctor conducts a consultation and "
                "either prescribes medication or orders lab tests. If lab tests are ordered, "
                "the patient goes to the lab, tests are performed, and results are sent to "
                "the doctor for review. After reviewing results (or if no labs), the doctor "
                "creates a treatment plan and the patient checks out. Sometimes the doctor "
                "decides to admit the patient to the hospital, in which case the check-out "
                "is skipped and admission paperwork begins.\n\n"
                "PREVIOUS ATTEMPT REJECTED by process model quality review.\n"
                "Issues: The XOR branch for 'admit vs checkout' creates a deadlock. In the "
                "checkout branch, the process reaches 'Patient Checks Out' and terminates. "
                "In the admit branch, the process reaches 'Admission Paperwork' but has no "
                "connection to a terminal state. This violates the liveness property — "
                "every execution path must reach a terminal state. Additionally, 'Doctor "
                "Notified' in the abnormal vitals branch has no outgoing edge, creating "
                "a dead end. Fix by ensuring both admit and checkout branches reach terminal "
                "states, and by ensuring 'Doctor Notified' connects to the consultation phase."
            ),
            trajectory=[
                {
                    "reasoning": "The previous POWL had dead ends: 'Doctor Notified' had no "
                    "outgoing edge, and the admit branch didn't reach a terminal state. "
                    "I need to fix the structure. Key fixes: (1) 'Doctor Notified' must lead "
                    "to 'Doctor Consultation', (2) both 'Patient Checks Out' and 'Admission "
                    "Complete' must be terminal states, (3) the admit branch must include "
                    "all steps from consultation to admission completion.",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "PO=( "
                        "nodes={ "
                            "'Patient Arrives', "
                            "'Patient Checks In', "
                            "'Nurse Takes Vitals', "
                            "X( "
                                "'Doctor Notified', "
                                "'Wait in Waiting Room' "
                            "), "
                            "'Doctor Consultation', "
                            "X( "
                                "'Prescribe Medication', "
                                "'Order Lab Tests' "
                            "), "
                            "'Go to Lab', "
                            "'Lab Tests Performed', "
                            "'Lab Results to Doctor', "
                            "'Doctor Reviews Results', "
                            "'Create Treatment Plan', "
                            "X( "
                                "'Patient Checks Out', "
                                "PO=( nodes={ "
                                    "'Begin Admission Paperwork', "
                                    "'Admission Complete' "
                                "}, order={ "
                                    "'Begin Admission Paperwork'-->'Admission Complete' "
                                "} ) "
                            ") "
                        "}, "
                        "order={ "
                            "'Patient Arrives'-->'Patient Checks In', "
                            "'Patient Checks In'-->'Nurse Takes Vitals', "
                            "'Nurse Takes Vitals'-->X( "
                                "'Doctor Notified', "
                                "'Wait in Waiting Room' "
                            "), "
                            "'Doctor Notified'-->'Doctor Consultation', "
                            "'Wait in Waiting Room'-->'Doctor Consultation', "
                            "'Doctor Consultation'-->X( "
                                "'Prescribe Medication', "
                                "'Order Lab Tests' "
                            "), "
                            "'Prescribe Medication'-->'Create Treatment Plan', "
                            "'Order Lab Tests'-->'Go to Lab', "
                            "'Go to Lab'-->'Lab Tests Performed', "
                            "'Lab Tests Performed'-->'Lab Results to Doctor', "
                            "'Lab Results to Doctor'-->'Doctor Reviews Results', "
                            "'Doctor Reviews Results'-->'Create Treatment Plan', "
                            "'Create Treatment Plan'-->X( "
                                "'Patient Checks Out', "
                                "PO=( nodes={ "
                                    "'Begin Admission Paperwork', "
                                    "'Admission Complete' "
                                "}, order={ "
                                    "'Begin Admission Paperwork'-->'Admission Complete' "
                                "} ) "
                            ") "
                        "} "
                    ")"},
                    "is_valid": True,
                    "errors": None,
                },
                {
                    "reasoning": "Valid POWL structure. Fixed all dead ends: 'Doctor Notified' "
                    "now connects to 'Doctor Consultation'. Both 'Patient Checks Out' and "
                    "'Admission Complete' are terminal states. The admit branch includes "
                    "'Begin Admission Paperwork' → 'Admission Complete'. Every execution "
                    "path reaches a terminal state (no deadlocks, no dead ends).",
                    "selected_fn": "finish",
                    "args": {"powl_model": "PO=( "
                        "nodes={ "
                            "'Patient Arrives', "
                            "'Patient Checks In', "
                            "'Nurse Takes Vitals', "
                            "X( "
                                "'Doctor Notified', "
                                "'Wait in Waiting Room' "
                            "), "
                            "'Doctor Consultation', "
                            "X( "
                                "'Prescribe Medication', "
                                "'Order Lab Tests' "
                            "), "
                            "'Go to Lab', "
                            "'Lab Tests Performed', "
                            "'Lab Results to Doctor', "
                            "'Doctor Reviews Results', "
                            "'Create Treatment Plan', "
                            "X( "
                                "'Patient Checks Out', "
                                "PO=( nodes={ "
                                    "'Begin Admission Paperwork', "
                                    "'Admission Complete' "
                                "}, order={ "
                                    "'Begin Admission Paperwork'-->'Admission Complete' "
                                "} ) "
                            ") "
                        "}, "
                        "order={ "
                            "'Patient Arrives'-->'Patient Checks In', "
                            "'Patient Checks In'-->'Nurse Takes Vitals', "
                            "'Nurse Takes Vitals'-->X( "
                                "'Doctor Notified', "
                                "'Wait in Waiting Room' "
                            "), "
                            "'Doctor Notified'-->'Doctor Consultation', "
                            "'Wait in Waiting Room'-->'Doctor Consultation', "
                            "'Doctor Consultation'-->X( "
                                "'Prescribe Medication', "
                                "'Order Lab Tests' "
                            "), "
                            "'Prescribe Medication'-->'Create Treatment Plan', "
                            "'Order Lab Tests'-->'Go to Lab', "
                            "'Go to Lab'-->'Lab Tests Performed', "
                            "'Lab Tests Performed'-->'Lab Results to Doctor', "
                            "'Lab Results to Doctor'-->'Doctor Reviews Results', "
                            "'Doctor Reviews Results'-->'Create Treatment Plan', "
                            "'Create Treatment Plan'-->X( "
                                "'Patient Checks Out', "
                                "PO=( nodes={ "
                                    "'Begin Admission Paperwork', "
                                    "'Admission Complete' "
                                "}, order={ "
                                    "'Begin Admission Paperwork'-->'Admission Complete' "
                                "} ) "
                            ") "
                        "} "
                    ")"},
                    "return_value": "PO=( nodes={ 'Patient Arrives', 'Patient Checks In', 'Nurse Takes Vitals', X( 'Doctor Notified', 'Wait in Waiting Room' ), 'Doctor Consultation', X( 'Prescribe Medication', 'Order Lab Tests' ), 'Go to Lab', 'Lab Tests Performed', 'Lab Results to Doctor', 'Doctor Reviews Results', 'Create Treatment Plan', X( 'Patient Checks Out', PO=( nodes={ 'Begin Admission Paperwork', 'Admission Complete' }, order={ 'Begin Admission Paperwork'-->'Admission Complete' } ) ) }, order={ 'Patient Arrives'-->'Patient Checks In', 'Patient Checks In'-->'Nurse Takes Vitals', 'Nurse Takes Vitals'-->X( 'Doctor Notified', 'Wait in Waiting Room' ), 'Doctor Notified'-->'Doctor Consultation', 'Wait in Waiting Room'-->'Doctor Consultation', 'Doctor Consultation'-->X( 'Prescribe Medication', 'Order Lab Tests' ), 'Prescribe Medication'-->'Create Treatment Plan', 'Order Lab Tests'-->'Go to Lab', 'Go to Lab'-->'Lab Tests Performed', 'Lab Tests Performed'-->'Lab Results to Doctor', 'Lab Results to Doctor'-->'Doctor Reviews Results', 'Doctor Reviews Results'-->'Create Treatment Plan', 'Create Treatment Plan'-->X( 'Patient Checks Out', PO=( nodes={ 'Begin Admission Paperwork', 'Admission Complete' }, order={ 'Begin Admission Paperwork'-->'Admission Complete' } ) ) } )",
                    "errors": None,
                },
            ],
            next_selected_fn="finish",
            args={"powl_model": "PO=( nodes={ 'Patient Arrives', 'Patient Checks In', 'Nurse Takes Vitals', X( 'Doctor Notified', 'Wait in Waiting Room' ), 'Doctor Consultation', X( 'Prescribe Medication', 'Order Lab Tests' ), 'Go to Lab', 'Lab Tests Performed', 'Lab Results to Doctor', 'Doctor Reviews Results', 'Create Treatment Plan', X( 'Patient Checks Out', PO=( nodes={ 'Begin Admission Paperwork', 'Admission Complete' }, order={ 'Begin Admission Paperwork'-->'Admission Complete' } ) ) }, order={ 'Patient Arrives'-->'Patient Checks In', 'Patient Checks In'-->'Nurse Takes Vitals', 'Nurse Takes Vitals'-->X( 'Doctor Notified', 'Wait in Waiting Room' ), 'Doctor Notified'-->'Doctor Consultation', 'Wait in Waiting Room'-->'Doctor Consultation', 'Doctor Consultation'-->X( 'Prescribe Medication', 'Order Lab Tests' ), 'Prescribe Medication'-->'Create Treatment Plan', 'Order Lab Tests'-->'Go to Lab', 'Go to Lab'-->'Lab Tests Performed', 'Lab Tests Performed'-->'Lab Results to Doctor', 'Lab Results to Doctor'-->'Doctor Reviews Results', 'Doctor Reviews Results'-->'Create Treatment Plan', 'Create Treatment Plan'-->X( 'Patient Checks Out', PO=( nodes={ 'Begin Admission Paperwork', 'Admission Complete' }, order={ 'Begin Admission Paperwork'-->'Admission Complete' } ) ) } )"},
        ),
        # Demo 6: Manufacturing production line with quality control
        dspy.Example(
            process_description=(
                "A manufacturing production line: Raw materials arrive and undergo "
                "preparation. Components are assembled. Quality inspection is performed. "
                "If quality check passes, the product is packaged and shipped. If quality "
                "check fails, the product goes to rework. After rework, it's re-inspected. "
                "If rework fails twice, the product is scrapped. Workers log production "
                "data after each step."
            ),
            trajectory=[
                {
                    "reasoning": "Key patterns: loop for rework/re-inspection, XOR for "
                    "pass/fail, nested XOR for rework success (ship) vs scrap after 2 failures. "
                    "Use PO for main flow with loop for quality feedback.",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "PO=( "
                        "nodes={ "
                            "'Receive Raw Materials', "
                            "'Prepare Materials', "
                            "'Assemble Components', "
                            "'Quality Inspection', "
                            "X( 'Package', 'Rework' ), "
                            "'Ship', "
                            "'Scrap' "
                        "}, "
                        "order={ "
                            "'Receive Raw Materials'-->'Prepare Materials', "
                            "'Prepare Materials'-->'Assemble Components', "
                            "'Assemble Components'-->'Quality Inspection', "
                            "'Quality Inspection'-->X( 'Package', 'Rework' ), "
                            "X( 'Package', 'Rework' )-->X( 'Ship', 'Scrap' ) "
                        "} "
                    ")"},
                    "is_valid": True,
                    "errors": None,
                },
                {
                    "reasoning": "Valid POWL. Quality inspection has XOR for pass (Package) "
                    "vs fail (Rework). After Package or Rework, another XOR decides Ship "
                    "(successful) vs Scrap (failed). Every path reaches a terminal state.",
                    "selected_fn": "finish",
                    "args": {"powl_model": "PO=( nodes={ 'Receive Raw Materials', 'Prepare Materials', 'Assemble Components', 'Quality Inspection', X( 'Package', 'Rework' ), 'Ship', 'Scrap' }, order={ 'Receive Raw Materials'-->'Prepare Materials', 'Prepare Materials'-->'Assemble Components', 'Assemble Components'-->'Quality Inspection', 'Quality Inspection'-->X( 'Package', 'Rework' ), X( 'Package', 'Rework' )-->X( 'Ship', 'Scrap' ) } )"},
                    "return_value": "PO=( nodes={ 'Receive Raw Materials', 'Prepare Materials', 'Assemble Components', 'Quality Inspection', X( 'Package', 'Rework' ), 'Ship', 'Scrap' }, order={ 'Receive Raw Materials'-->'Prepare Materials', 'Prepare Materials'-->'Assemble Components', 'Assemble Components'-->'Quality Inspection', 'Quality Inspection'-->X( 'Package', 'Rework' ), X( 'Package', 'Rework' )-->X( 'Ship', 'Scrap' ) } )",
                    "errors": None,
                },
            ],
            next_selected_fn="finish",
            args={"powl_model": "PO=( nodes={ 'Receive Raw Materials', 'Prepare Materials', 'Assemble Components', 'Quality Inspection', X( 'Package', 'Rework' ), 'Ship', 'Scrap' }, order={ 'Receive Raw Materials'-->'Prepare Materials', 'Prepare Materials'-->'Assemble Components', 'Assemble Components'-->'Quality Inspection', 'Quality Inspection'-->X( 'Package', 'Rework' ), X( 'Package', 'Rework' )-->X( 'Ship', 'Scrap' ) } )"},
        ),
        # Demo 7: Finance expense approval with multi-level escalation
        dspy.Example(
            process_description=(
                "An expense approval process: Employee submits expense report. Manager "
                "reviews. If amount under $500, manager approves directly. If amount "
                "$500-5000, director approval required. If over $5000, VP approval required. "
                "At any level, the approver can reject (sends back to employee for revision) "
                "or approve (forwards to finance). Finance processes payment and archives "
                "the record. Sometimes the approver requests more information, which "
                "the employee provides before re-review."
            ),
            trajectory=[
                {
                    "reasoning": "Multi-level approval with amount-based routing. XOR for each "
                    "approval level (under 500, 500-5000, over 5000). Each level has sub-XOR "
                    "for reject/request info/approve. Rejected reports loop back to employee.",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "PO=( "
                        "nodes={ "
                            "'Submit Expense', "
                            "*( 'Manager Review', 'Resubmit' ), "
                            "X( "
                                "PO=( nodes={ 'Director Review', 'Finance Payment', 'Archive Record' }, "
                                    "order={ 'Director Review'-->'Finance Payment', "
                                    "'Finance Payment'-->'Archive Record' } ), "
                                "PO=( nodes={ 'VP Review', 'Finance Payment', 'Archive Record' }, "
                                    "order={ 'VP Review'-->'Finance Payment', "
                                    "'Finance Payment'-->'Archive Record' } ), "
                                "'Submit Expense' "
                            ") "
                        "}, "
                        "order={ "
                            "'Submit Expense'-->*( 'Manager Review', 'Resubmit' ), "
                            "*( 'Manager Review', 'Resubmit' )-->X( "
                                "PO=( nodes={ 'Director Review', 'Finance Payment', 'Archive Record' }, "
                                    "order={ 'Director Review'-->'Finance Payment', "
                                    "'Finance Payment'-->'Archive Record' } ), "
                                "PO=( nodes={ 'VP Review', 'Finance Payment', 'Archive Record' }, "
                                    "order={ 'VP Review'-->'Finance Payment', "
                                    "'Finance Payment'-->'Archive Record' } ), "
                                "'Submit Expense' "
                            ") "
                        "} "
                    ")"},
                    "is_valid": True,
                    "errors": None,
                },
                {
                    "reasoning": "Valid approval routing POWL. Manager review loops back "
                    "to submit for resubmission. After manager, XOR routes to director, VP, or "
                    "back to submit (reject). All paths end at Archive Record.",
                    "selected_fn": "finish",
                    "args": {"powl_model": "PO=( nodes={ 'Submit Expense', *( 'Manager Review', 'Resubmit' ), X( PO=( nodes={ 'Director Review', 'Finance Payment', 'Archive Record' }, order={ 'Director Review'-->'Finance Payment', 'Finance Payment'-->'Archive Record' } ), PO=( nodes={ 'VP Review', 'Finance Payment', 'Archive Record' }, order={ 'VP Review'-->'Finance Payment', 'Finance Payment'-->'Archive Record' } ), 'Submit Expense' ) }, order={ 'Submit Expense'-->*( 'Manager Review', 'Resubmit' ), *( 'Manager Review', 'Resubmit' )-->X( PO=( nodes={ 'Director Review', 'Finance Payment', 'Archive Record' }, order={ 'Director Review'-->'Finance Payment', 'Finance Payment'-->'Archive Record' } ), PO=( nodes={ 'VP Review', 'Finance Payment', 'Archive Record' }, order={ 'VP Review'-->'Finance Payment', 'Finance Payment'-->'Archive Record' } ), 'Submit Expense' ) } )"},
                    "return_value": "PO=( nodes={ 'Submit Expense', *( 'Manager Review', 'Resubmit' ), X( PO=( nodes={ 'Director Review', 'Finance Payment', 'Archive Record' }, order={ 'Director Review'-->'Finance Payment', 'Finance Payment'-->'Archive Record' } ), PO=( nodes={ 'VP Review', 'Finance Payment', 'Archive Record' }, order={ 'VP Review'-->'Finance Payment', 'Finance Payment'-->'Archive Record' } ), 'Submit Expense' ) }, order={ 'Submit Expense'-->*( 'Manager Review', 'Resubmit' ), *( 'Manager Review', 'Resubmit' )-->X( PO=( nodes={ 'Director Review', 'Finance Payment', 'Archive Record' }, order={ 'Director Review'-->'Finance Payment', 'Finance Payment'-->'Archive Record' } ), PO=( nodes={ 'VP Review', 'Finance Payment', 'Archive Record' }, order={ 'VP Review'-->'Finance Payment', 'Finance Payment'-->'Archive Record' } ), 'Submit Expense' ) } )",
                    "errors": None,
                },
            ],
            next_selected_fn="finish",
            args={"powl_model": "PO=( nodes={ 'Submit Expense', *( 'Manager Review', 'Resubmit' ), X( PO=( nodes={ 'Director Review', 'Finance Payment', 'Archive Record' }, order={ 'Director Review'-->'Finance Payment', 'Finance Payment'-->'Archive Record' } ), PO=( nodes={ 'VP Review', 'Finance Payment', 'Archive Record' }, order={ 'VP Review'-->'Finance Payment', 'Finance Payment'-->'Archive Record' } ), 'Submit Expense' ) }, order={ 'Submit Expense'-->*( 'Manager Review', 'Resubmit' ), *( 'Manager Review', 'Resubmit' )-->X( PO=( nodes={ 'Director Review', 'Finance Payment', 'Archive Record' }, order={ 'Director Review'-->'Finance Payment', 'Finance Payment'-->'Archive Record' } ), PO=( nodes={ 'VP Review', 'Finance Payment', 'Archive Record' }, order={ 'VP Review'-->'Finance Payment', 'Finance Payment'-->'Archive Record' } ), 'Submit Expense' ) } )"},
        ),
        # Demo 8: HR employee onboarding with parallel tasks
        dspy.Example(
            process_description=(
                "HR onboarding process: New employee accepts offer. HR prepares paperwork "
                "while IT sets up accounts (these happen in parallel). Employee completes "
                "I-9 and tax forms. IT conducts security training. Manager conducts role "
                "training. After all training complete, employee signs handbook. Employee "
                "gets badge access. Onboarding complete and archived. Sometimes IT setup "
                "fails, requiring restart of that step."
            ),
            trajectory=[
                {
                    "reasoning": "Parallel tasks: HR paperwork AND IT account setup happen "
                    "simultaneously. Training also has parallel paths (security + role). "
                    "Use PO for parallel activities. XOR for IT setup failure path.",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "PO=( "
                        "nodes={ "
                            "'Accept Offer', "
                            "'Prepare Paperwork', "
                            "*( 'Setup IT Accounts', 'Retry IT Setup' ), "
                            "'Complete I-9', "
                            "'Tax Forms', "
                            "'Security Training', "
                            "'Role Training', "
                            "'Sign Handbook', "
                            "'Get Badge', "
                            "'Archive Onboarding' "
                        "}, "
                        "order={ "
                            "'Accept Offer'-->'Prepare Paperwork', "
                            "'Accept Offer'-->*( 'Setup IT Accounts', 'Retry IT Setup' ), "
                            "'Prepare Paperwork'-->'Complete I-9', "
                            "'Complete I-9'-->'Tax Forms', "
                            "*( 'Setup IT Accounts', 'Retry IT Setup' )-->'Security Training', "
                            "'Tax Forms'-->'Role Training', "
                            "'Security Training'-->'Sign Handbook', "
                            "'Role Training'-->'Sign Handbook', "
                            "'Sign Handbook'-->'Get Badge', "
                            "'Get Badge'-->'Archive Onboarding' "
                        "} "
                    ")"},
                    "is_valid": True,
                    "errors": None,
                },
                {
                    "reasoning": "Valid onboarding POWL. Parallel branches: HR (Paperwork→I-9→Tax Forms→Role) "
                    "and IT (Setup→Security) converge at Sign Handbook. IT setup has loop "
                    "for retry. All paths end at Archive Onboarding.",
                    "selected_fn": "finish",
                    "args": {"powl_model": "PO=( nodes={ 'Accept Offer', 'Prepare Paperwork', *( 'Setup IT Accounts', 'Retry IT Setup' ), 'Complete I-9', 'Tax Forms', 'Security Training', 'Role Training', 'Sign Handbook', 'Get Badge', 'Archive Onboarding' }, order={ 'Accept Offer'-->'Prepare Paperwork', 'Accept Offer'-->*( 'Setup IT Accounts', 'Retry IT Setup' ), 'Prepare Paperwork'-->'Complete I-9', 'Complete I-9'-->'Tax Forms', *( 'Setup IT Accounts', 'Retry IT Setup' )-->'Security Training', 'Tax Forms'-->'Role Training', 'Security Training'-->'Sign Handbook', 'Role Training'-->'Sign Handbook', 'Sign Handbook'-->'Get Badge', 'Get Badge'-->'Archive Onboarding' } )"},
                    "return_value": "PO=( nodes={ 'Accept Offer', 'Prepare Paperwork', *( 'Setup IT Accounts', 'Retry IT Setup' ), 'Complete I-9', 'Tax Forms', 'Security Training', 'Role Training', 'Sign Handbook', 'Get Badge', 'Archive Onboarding' }, order={ 'Accept Offer'-->'Prepare Paperwork', 'Accept Offer'-->*( 'Setup IT Accounts', 'Retry IT Setup' ), 'Prepare Paperwork'-->'Complete I-9', 'Complete I-9'-->'Tax Forms', *( 'Setup IT Accounts', 'Retry IT Setup' )-->'Security Training', 'Tax Forms'-->'Role Training', 'Security Training'-->'Sign Handbook', 'Role Training'-->'Sign Handbook', 'Sign Handbook'-->'Get Badge', 'Get Badge'-->'Archive Onboarding' } )",
                    "errors": None,
                },
            ],
            next_selected_fn="finish",
            args={"powl_model": "PO=( nodes={ 'Accept Offer', 'Prepare Paperwork', *( 'Setup IT Accounts', 'Retry IT Setup' ), 'Complete I-9', 'Tax Forms', 'Security Training', 'Role Training', 'Sign Handbook', 'Get Badge', 'Archive Onboarding' }, order={ 'Accept Offer'-->'Prepare Paperwork', 'Accept Offer'-->*( 'Setup IT Accounts', 'Retry IT Setup' ), 'Prepare Paperwork'-->'Complete I-9', 'Complete I-9'-->'Tax Forms', *( 'Setup IT Accounts', 'Retry IT Setup' )-->'Security Training', 'Tax Forms'-->'Role Training', 'Security Training'-->'Sign Handbook', 'Role Training'-->'Sign Handbook', 'Sign Handbook'-->'Get Badge', 'Get Badge'-->'Archive Onboarding' } )"},
        ),
        # Demo 9: IT incident management with SLA escalation
        dspy.Example(
            process_description=(
                "IT incident management: User reports incident. Service desk triages. If "
                "critical severity, immediately escalate to senior engineer. If standard, "
                "tier 1 analyst attempts resolution. If tier 1 resolves within SLA, close "
                "ticket. If tier 1 fails or SLA breached, escalate to tier 2. Tier 2 attempts "
                "resolution. If tier 2 fails, escalate to tier 3. Tier 3 is senior engineer. "
                "After resolution, user verifies fix. If user satisfied, close ticket. If "
                "user not satisfied, reopen and send back to tier 1."
            ),
            trajectory=[
                {
                    "reasoning": "Multi-tier escalation with SLA deadlines. XOR for severity "
                    "routing (critical goes straight to tier 3, standard goes to tier 1). "
                    "Each tier can escalate up. User verification has loop for reopen.",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "PO=( "
                        "nodes={ "
                            "'Report Incident', "
                            "'Triage', "
                            "X( "
                                "'Tier 1 Analysis', "
                                "'Tier 3 Senior Engineer' "
                            "), "
                            "'Resolve Issue', "
                            "'User Verify', "
                            "X( 'Close Ticket', 'Reopen' ) "
                        "}, "
                        "order={ "
                            "'Report Incident'-->'Triage', "
                            "'Triage'-->X( "
                                "'Tier 1 Analysis', "
                                "'Tier 3 Senior Engineer' "
                            "), "
                            "'Tier 1 Analysis'-->'Resolve Issue', "
                            "'Tier 3 Senior Engineer'-->'Resolve Issue', "
                            "'Resolve Issue'-->'User Verify', "
                            "'User Verify'-->X( 'Close Ticket', 'Reopen' ), "
                            "'Reopen'-->'Tier 1 Analysis' "
                        "} "
                    ")"},
                    "is_valid": True,
                    "errors": None,
                },
                {
                    "reasoning": "Valid incident management POWL. Triage routes critical to "
                    "tier 3, standard to tier 1. Resolution at both tiers. User verification "
                    "closes or reopens (loops back to tier 1). All paths reach terminal state.",
                    "selected_fn": "finish",
                    "args": {"powl_model": "PO=( nodes={ 'Report Incident', 'Triage', X( 'Tier 1 Analysis', 'Tier 3 Senior Engineer' ), 'Resolve Issue', 'User Verify', X( 'Close Ticket', 'Reopen' ) }, order={ 'Report Incident'-->'Triage', 'Triage'-->X( 'Tier 1 Analysis', 'Tier 3 Senior Engineer' ), 'Tier 1 Analysis'-->'Resolve Issue', 'Tier 3 Senior Engineer'-->'Resolve Issue', 'Resolve Issue'-->'User Verify', 'User Verify'-->X( 'Close Ticket', 'Reopen' ), 'Reopen'-->'Tier 1 Analysis' } )"},
                    "return_value": "PO=( nodes={ 'Report Incident', 'Triage', X( 'Tier 1 Analysis', 'Tier 3 Senior Engineer' ), 'Resolve Issue', 'User Verify', X( 'Close Ticket', 'Reopen' ) }, order={ 'Report Incident'-->'Triage', 'Triage'-->X( 'Tier 1 Analysis', 'Tier 3 Senior Engineer' ), 'Tier 1 Analysis'-->'Resolve Issue', 'Tier 3 Senior Engineer'-->'Resolve Issue', 'Resolve Issue'-->'User Verify', 'User Verify'-->X( 'Close Ticket', 'Reopen' ), 'Reopen'-->'Tier 1 Analysis' } )",
                    "errors": None,
                },
            ],
            next_selected_fn="finish",
            args={"powl_model": "PO=( nodes={ 'Report Incident', 'Triage', X( 'Tier 1 Analysis', 'Tier 3 Senior Engineer' ), 'Resolve Issue', 'User Verify', X( 'Close Ticket', 'Reopen' ) }, order={ 'Report Incident'-->'Triage', 'Triage'-->X( 'Tier 1 Analysis', 'Tier 3 Senior Engineer' ), 'Tier 1 Analysis'-->'Resolve Issue', 'Tier 3 Senior Engineer'-->'Resolve Issue', 'Resolve Issue'-->'User Verify', 'User Verify'-->X( 'Close Ticket', 'Reopen' ), 'Reopen'-->'Tier 1 Analysis' } )"},
        ),
        # Demo 10: Healthcare insurance claim processing
        dspy.Example(
            process_description=(
                "Health insurance claim process: Patient submits claim. Claims system "
                "validates format and completeness. If invalid, return to patient. If "
                "valid, check eligibility. If not eligible, deny claim. If eligible, "
                "medical review determines if services are covered. If not covered, deny. "
                "If covered, calculate payment amount. If amount over deductible, process "
                "payment. If under deductible, apply to deductible balance and notify patient. "
                "After payment or denial, claim is archived. Provider can appeal denial "
                "within 30 days."
            ),
            trajectory=[
                {
                    "reasoning": "Complex decision tree with multiple XOR checkpoints: "
                    "validation, eligibility, coverage, deductible. Each check has pass/fail. "
                    "Appeal loop from denial back to medical review.",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "PO=( "
                        "nodes={ "
                            "'Submit Claim', "
                            "X( "
                                "'Validate Format', "
                                "'Return to Patient' "
                            "), "
                            "'Check Eligibility', "
                            "X( "
                                "'Medical Review', "
                                "'Deny Claim' "
                            "), "
                            "'Calculate Payment', "
                            "X( "
                                "'Process Payment', "
                                "'Apply Deductible' "
                            "), "
                            "'Archive Claim' "
                        "}, "
                        "order={ "
                            "'Submit Claim'-->X( "
                                "'Validate Format', "
                                "'Return to Patient' "
                            "), "
                            "'Validate Format'-->'Check Eligibility', "
                            "'Check Eligibility'-->X( "
                                "'Medical Review', "
                                "'Deny Claim' "
                            "), "
                            "'Medical Review'-->'Calculate Payment', "
                            "'Calculate Payment'-->X( "
                                "'Process Payment', "
                                "'Apply Deductible' "
                            "), "
                            "X( 'Process Payment', 'Apply Deductible' )-->'Archive Claim', "
                            "'Deny Claim'-->'Archive Claim' "
                        "} "
                    ")"},
                    "is_valid": True,
                    "errors": None,
                },
                {
                    "reasoning": "Valid claim processing POWL. Sequential checks with XOR "
                    "decisions at each step. Invalid returns to patient. Ineligible denies. "
                    "Not covered denies. Covered leads to payment calculation. Over deductible "
                    "pays, under applies to balance. All paths reach Archive Claim.",
                    "selected_fn": "finish",
                    "args": {"powl_model": "PO=( nodes={ 'Submit Claim', X( 'Validate Format', 'Return to Patient' ), 'Check Eligibility', X( 'Medical Review', 'Deny Claim' ), 'Calculate Payment', X( 'Process Payment', 'Apply Deductible' ), 'Archive Claim' }, order={ 'Submit Claim'-->X( 'Validate Format', 'Return to Patient' ), 'Validate Format'-->'Check Eligibility', 'Check Eligibility'-->X( 'Medical Review', 'Deny Claim' ), 'Medical Review'-->'Calculate Payment', 'Calculate Payment'-->X( 'Process Payment', 'Apply Deductible' ), X( 'Process Payment', 'Apply Deductible' )-->'Archive Claim', 'Deny Claim'-->'Archive Claim' } )"},
                    "return_value": "PO=( nodes={ 'Submit Claim', X( 'Validate Format', 'Return to Patient' ), 'Check Eligibility', X( 'Medical Review', 'Deny Claim' ), 'Calculate Payment', X( 'Process Payment', 'Apply Deductible' ), 'Archive Claim' }, order={ 'Submit Claim'-->X( 'Validate Format', 'Return to Patient' ), 'Validate Format'-->'Check Eligibility', 'Check Eligibility'-->X( 'Medical Review', 'Deny Claim' ), 'Medical Review'-->'Calculate Payment', 'Calculate Payment'-->X( 'Process Payment', 'Apply Deductible' ), X( 'Process Payment', 'Apply Deductible' )-->'Archive Claim', 'Deny Claim'-->'Archive Claim' } )",
                    "errors": None,
                },
            ],
            next_selected_fn="finish",
            args={"powl_model": "PO=( nodes={ 'Submit Claim', X( 'Validate Format', 'Return to Patient' ), 'Check Eligibility', X( 'Medical Review', 'Deny Claim' ), 'Calculate Payment', X( 'Process Payment', 'Apply Deductible' ), 'Archive Claim' }, order={ 'Submit Claim'-->X( 'Validate Format', 'Return to Patient' ), 'Validate Format'-->'Check Eligibility', 'Check Eligibility'-->X( 'Medical Review', 'Deny Claim' ), 'Medical Review'-->'Calculate Payment', 'Calculate Payment'-->X( 'Process Payment', 'Apply Deductible' ), X( 'Process Payment', 'Apply Deductible' )-->'Archive Claim', 'Deny Claim'-->'Archive Claim' } )"},
        ),
        # Demo 11: Logistics order fulfillment with warehouse operations
        dspy.Example(
            process_description=(
                "Logistics fulfillment: Customer places order. System checks inventory. "
                "If out of stock, place backorder and notify customer. If in stock, warehouse "
                "picks items. Quality check picks. If quality fail, return item to stock and "
                "repick. If quality pass, pack items. Generate shipping label. Shipper picks "
                "up package. Customer receives package. Optionally, customer may return "
                "item. If return, process refund and restock item."
            ),
            trajectory=[
                {
                    "reasoning": "Inventory-driven process with XOR for in-stock/out-of-stock. "
                    "Quality check has loop for repick on failure. Optional return at end creates XOR "
                    "with tau (silent transition for no return).",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "PO=( "
                        "nodes={ "
                            "'Place Order', "
                            "'Check Inventory', "
                            "X( "
                                "'Backorder', "
                                "'Pick Items' "
                            "), "
                            "*( 'Quality Check', 'Repick' ), "
                            "'Pack Items', "
                            "'Generate Label', "
                            "'Ship Package', "
                            "'Receive Package', "
                            "X( 'Return Item', tau ) "
                        "}, "
                        "order={ "
                            "'Place Order'-->'Check Inventory', "
                            "'Check Inventory'-->X( "
                                "'Backorder', "
                                "'Pick Items' "
                            "), "
                            "'Pick Items'-->*( 'Quality Check', 'Repick' ), "
                            "*( 'Quality Check', 'Repick' )-->'Pack Items', "
                            "'Pack Items'-->'Generate Label', "
                            "'Generate Label'-->'Ship Package', "
                            "'Ship Package'-->'Receive Package', "
                            "'Receive Package'-->X( 'Return Item', tau ) "
                        "} "
                    ")"},
                    "is_valid": True,
                    "errors": None,
                },
                {
                    "reasoning": "Valid fulfillment POWL. Inventory check XOR routes to backorder "
                    "or pick. Quality check loops for repick on failure. Optional return at end. "
                    "All paths terminate.",
                    "selected_fn": "finish",
                    "args": {"powl_model": "PO=( nodes={ 'Place Order', 'Check Inventory', X( 'Backorder', 'Pick Items' ), *( 'Quality Check', 'Repick' ), 'Pack Items', 'Generate Label', 'Ship Package', 'Receive Package', X( 'Return Item', tau ) }, order={ 'Place Order'-->'Check Inventory', 'Check Inventory'-->X( 'Backorder', 'Pick Items' ), 'Pick Items'-->*( 'Quality Check', 'Repick' ), *( 'Quality Check', 'Repick' )-->'Pack Items', 'Pack Items'-->'Generate Label', 'Generate Label'-->'Ship Package', 'Ship Package'-->'Receive Package', 'Receive Package'-->X( 'Return Item', tau ) } )"},
                    "return_value": "PO=( nodes={ 'Place Order', 'Check Inventory', X( 'Backorder', 'Pick Items' ), *( 'Quality Check', 'Repick' ), 'Pack Items', 'Generate Label', 'Ship Package', 'Receive Package', X( 'Return Item', tau ) }, order={ 'Place Order'-->'Check Inventory', 'Check Inventory'-->X( 'Backorder', 'Pick Items' ), 'Pick Items'-->*( 'Quality Check', 'Repick' ), *( 'Quality Check', 'Repick' )-->'Pack Items', 'Pack Items'-->'Generate Label', 'Generate Label'-->'Ship Package', 'Ship Package'-->'Receive Package', 'Receive Package'-->X( 'Return Item', tau ) } )",
                    "errors": None,
                },
            ],
            next_selected_fn="finish",
            args={"powl_model": "PO=( nodes={ 'Place Order', 'Check Inventory', X( 'Backorder', 'Pick Items' ), *( 'Quality Check', 'Repick' ), 'Pack Items', 'Generate Label', 'Ship Package', 'Receive Package', X( 'Return Item', tau ) }, order={ 'Place Order'-->'Check Inventory', 'Check Inventory'-->X( 'Backorder', 'Pick Items' ), 'Pick Items'-->*( 'Quality Check', 'Repick' ), *( 'Quality Check', 'Repick' )-->'Pack Items', 'Pack Items'-->'Generate Label', 'Generate Label'-->'Ship Package', 'Ship Package'-->'Receive Package', 'Receive Package'-->X( 'Return Item', tau ) } )"},
        ),
        # Demo 12: Retail purchase with payment processing
        dspy.Example(
            process_description=(
                "Retail purchase process: Customer adds items to cart. Customer proceeds to "
                "checkout. Customer enters shipping address. Customer selects payment method: "
                "credit card, PayPal, or Apple Pay. If credit card, validate card. If PayPal, "
                "redirect to PayPal. If Apple Pay, authenticate with Touch ID. After payment, "
                "generate order confirmation. Email confirmation to customer. Warehouse "
                "prepares shipment. Customer receives tracking number. Order delivered. "
                "Customer can review product. If satisfied, close order. If not satisfied, "
                "initiate return."
            ),
            trajectory=[
                {
                    "reasoning": "Payment method selection is 3-way XOR. Each payment type has "
                    "different validation flow. After payment, standard fulfillment. End has "
                    "XOR for satisfied/close vs return.",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "PO=( "
                        "nodes={ "
                            "'Add to Cart', "
                            "'Checkout', "
                            "'Enter Address', "
                            "X( "
                                "'Validate Card', "
                                "'PayPal Redirect', "
                                "'Apple Pay Auth' "
                            "), "
                            "'Process Payment', "
                            "'Generate Confirmation', "
                            "'Email Customer', "
                            "'Prepare Shipment', "
                            "'Send Tracking', "
                            "'Deliver Order', "
                            "X( 'Close Order', 'Initiate Return' ) "
                        "}, "
                        "order={ "
                            "'Add to Cart'-->'Checkout', "
                            "'Checkout'-->'Enter Address', "
                            "'Enter Address'-->X( "
                                "'Validate Card', "
                                "'PayPal Redirect', "
                                "'Apple Pay Auth' "
                            "), "
                            "X( 'Validate Card', 'PayPal Redirect', 'Apple Pay Auth' )-->'Process Payment', "
                            "'Process Payment'-->'Generate Confirmation', "
                            "'Generate Confirmation'-->'Email Customer', "
                            "'Email Customer'-->'Prepare Shipment', "
                            "'Prepare Shipment'-->'Send Tracking', "
                            "'Send Tracking'-->'Deliver Order', "
                            "'Deliver Order'-->X( 'Close Order', 'Initiate Return' ) "
                        "} "
                    ")"},
                    "is_valid": True,
                    "errors": None,
                },
                {
                    "reasoning": "Valid retail purchase POWL. 3-way XOR for payment method. All "
                    "payment paths converge to Process Payment. Fulfillment is sequential. "
                    "Final XOR for satisfaction check. All paths terminate.",
                    "selected_fn": "finish",
                    "args": {"powl_model": "PO=( nodes={ 'Add to Cart', 'Checkout', 'Enter Address', X( 'Validate Card', 'PayPal Redirect', 'Apple Pay Auth' ), 'Process Payment', 'Generate Confirmation', 'Email Customer', 'Prepare Shipment', 'Send Tracking', 'Deliver Order', X( 'Close Order', 'Initiate Return' ) }, order={ 'Add to Cart'-->'Checkout', 'Checkout'-->'Enter Address', 'Enter Address'-->X( 'Validate Card', 'PayPal Redirect', 'Apple Pay Auth' ), X( 'Validate Card', 'PayPal Redirect', 'Apple Pay Auth' )-->'Process Payment', 'Process Payment'-->'Generate Confirmation', 'Generate Confirmation'-->'Email Customer', 'Email Customer'-->'Prepare Shipment', 'Prepare Shipment'-->'Send Tracking', 'Send Tracking'-->'Deliver Order', 'Deliver Order'-->X( 'Close Order', 'Initiate Return' ) } )"},
                    "return_value": "PO=( nodes={ 'Add to Cart', 'Checkout', 'Enter Address', X( 'Validate Card', 'PayPal Redirect', 'Apple Pay Auth' ), 'Process Payment', 'Generate Confirmation', 'Email Customer', 'Prepare Shipment', 'Send Tracking', 'Deliver Order', X( 'Close Order', 'Initiate Return' ) }, order={ 'Add to Cart'-->'Checkout', 'Checkout'-->'Enter Address', 'Enter Address'-->X( 'Validate Card', 'PayPal Redirect', 'Apple Pay Auth' ), X( 'Validate Card', 'PayPal Redirect', 'Apple Pay Auth' )-->'Process Payment', 'Process Payment'-->'Generate Confirmation', 'Generate Confirmation'-->'Email Customer', 'Email Customer'-->'Prepare Shipment', 'Prepare Shipment'-->'Send Tracking', 'Send Tracking'-->'Deliver Order', 'Deliver Order'-->X( 'Close Order', 'Initiate Return' ) } )",
                    "errors": None,
                },
            ],
            next_selected_fn="finish",
            args={"powl_model": "PO=( nodes={ 'Add to Cart', 'Checkout', 'Enter Address', X( 'Validate Card', 'PayPal Redirect', 'Apple Pay Auth' ), 'Process Payment', 'Generate Confirmation', 'Email Customer', 'Prepare Shipment', 'Send Tracking', 'Deliver Order', X( 'Close Order', 'Initiate Return' ) }, order={ 'Add to Cart'-->'Checkout', 'Checkout'-->'Enter Address', 'Enter Address'-->X( 'Validate Card', 'PayPal Redirect', 'Apple Pay Auth' ), X( 'Validate Card', 'PayPal Redirect', 'Apple Pay Auth' )-->'Process Payment', 'Process Payment'-->'Generate Confirmation', 'Generate Confirmation'-->'Email Customer', 'Email Customer'-->'Prepare Shipment', 'Prepare Shipment'-->'Send Tracking', 'Send Tracking'-->'Deliver Order', 'Deliver Order'-->X( 'Close Order', 'Initiate Return' ) } )"},
        ),
        # Demo 13: Procurement purchase request with approval workflow
        dspy.Example(
            process_description=(
                "Procurement purchase request: Requester creates purchase order. System "
                "checks budget availability. If insufficient budget, return to requester. "
                "If sufficient budget, determine approval level based on amount. Under "
                "$1000: manager approval. $1000-10000: director approval. Over $10000: "
                "VP approval plus CFO review. Approver can approve, reject, or request "
                "changes. If approved, forward to purchasing. Purchasing issues PO to vendor. "
                "Vendor acknowledges PO. Vendor ships goods. Goods received and inspected. "
                "If goods damaged, return to vendor. If goods acceptable, process invoice "
                "and payment."
            ),
            trajectory=[
                {
                    "reasoning": "Budget check with loop back if insufficient. Amount-based "
                    "approval routing (3-way XOR). Each approver has 3-way decision (approve/"
                    "reject/request changes). Changes loops back. Goods inspection has loop for damaged returns.",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "PO=( "
                        "nodes={ "
                            "'Create PO', "
                            "*( 'Check Budget', 'Revise PO' ), "
                            "X( "
                                "'Manager Approval', "
                                "'Director Approval', "
                                "'VP Approval' "
                            "), "
                            "X( "
                                "'Issue PO', "
                                "'Reject PO', "
                                "'Request Changes' "
                            "), "
                            "'Vendor Ack', "
                            "'Vendor Ship', "
                            "'Receive Goods', "
                            "X( "
                                "'Process Invoice', "
                                "'Return to Vendor' "
                            ") "
                        "}, "
                        "order={ "
                            "'Create PO'-->*( 'Check Budget', 'Revise PO' ), "
                            "*( 'Check Budget', 'Revise PO' )-->X( "
                                "'Manager Approval', "
                                "'Director Approval', "
                                "'VP Approval' "
                            "), "
                            "X( 'Manager Approval', 'Director Approval', 'VP Approval' )-->X( "
                                "'Issue PO', "
                                "'Reject PO', "
                                "'Request Changes' "
                            "), "
                            "'Request Changes'-->'Create PO', "
                            "'Issue PO'-->'Vendor Ack', "
                            "'Vendor Ack'-->'Vendor Ship', "
                            "'Vendor Ship'-->'Receive Goods', "
                            "'Receive Goods'-->X( "
                                "'Process Invoice', "
                                "'Return to Vendor' "
                            ") "
                        "} "
                    ")"},
                    "is_valid": True,
                    "errors": None,
                },
                {
                    "reasoning": "Valid procurement POWL. Budget check loops for revision. "
                    "Amount-based approval routing. Approver decision with approve/reject/"
                    "changes. Changes loops back. Goods inspection has return loop for damaged. "
                    "All paths terminate.",
                    "selected_fn": "finish",
                    "args": {"powl_model": "PO=( nodes={ 'Create PO', *( 'Check Budget', 'Revise PO' ), X( 'Manager Approval', 'Director Approval', 'VP Approval' ), X( 'Issue PO', 'Reject PO', 'Request Changes' ), 'Vendor Ack', 'Vendor Ship', 'Receive Goods', X( 'Process Invoice', 'Return to Vendor' ) }, order={ 'Create PO'-->*( 'Check Budget', 'Revise PO' ), *( 'Check Budget', 'Revise PO' )-->X( 'Manager Approval', 'Director Approval', 'VP Approval' ), X( 'Manager Approval', 'Director Approval', 'VP Approval' )-->X( 'Issue PO', 'Reject PO', 'Request Changes' ), 'Request Changes'-->'Create PO', 'Issue PO'-->'Vendor Ack', 'Vendor Ack'-->'Vendor Ship', 'Vendor Ship'-->'Receive Goods', 'Receive Goods'-->X( 'Process Invoice', 'Return to Vendor' ) } )"},
                    "return_value": "PO=( nodes={ 'Create PO', *( 'Check Budget', 'Revise PO' ), X( 'Manager Approval', 'Director Approval', 'VP Approval' ), X( 'Issue PO', 'Reject PO', 'Request Changes' ), 'Vendor Ack', 'Vendor Ship', 'Receive Goods', X( 'Process Invoice', 'Return to Vendor' ) }, order={ 'Create PO'-->*( 'Check Budget', 'Revise PO' ), *( 'Check Budget', 'Revise PO' )-->X( 'Manager Approval', 'Director Approval', 'VP Approval' ), X( 'Manager Approval', 'Director Approval', 'VP Approval' )-->X( 'Issue PO', 'Reject PO', 'Request Changes' ), 'Request Changes'-->'Create PO', 'Issue PO'-->'Vendor Ack', 'Vendor Ack'-->'Vendor Ship', 'Vendor Ship'-->'Receive Goods', 'Receive Goods'-->X( 'Process Invoice', 'Return to Vendor' ) } )",
                    "errors": None,
                },
            ],
            next_selected_fn="finish",
            args={"powl_model": "PO=( nodes={ 'Create PO', *( 'Check Budget', 'Revise PO' ), X( 'Manager Approval', 'Director Approval', 'VP Approval' ), X( 'Issue PO', 'Reject PO', 'Request Changes' ), 'Vendor Ack', 'Vendor Ship', 'Receive Goods', X( 'Process Invoice', 'Return to Vendor' ) }, order={ 'Create PO'-->*( 'Check Budget', 'Revise PO' ), *( 'Check Budget', 'Revise PO' )-->X( 'Manager Approval', 'Director Approval', 'VP Approval' ), X( 'Manager Approval', 'Director Approval', 'VP Approval' )-->X( 'Issue PO', 'Reject PO', 'Request Changes' ), 'Request Changes'-->'Create PO', 'Issue PO'-->'Vendor Ack', 'Vendor Ack'-->'Vendor Ship', 'Vendor Ship'-->'Receive Goods', 'Receive Goods'-->X( 'Process Invoice', 'Return to Vendor' ) } )"},
        ),
        # Demo 14: Customer support ticket lifecycle
        dspy.Example(
            process_description=(
                "Customer support ticket lifecycle: Customer submits ticket. Support system "
                "categorizes ticket (billing, technical, general). If billing, route to billing "
                "specialist. If technical, route to technical support. If general, route to "
                "general support. Agent attempts first contact resolution. If resolved, close "
                "ticket and survey customer. If not resolved, escalate to tier 2. Tier 2 "
                "investigates. If tier 2 resolves, close and survey. If tier 2 cannot resolve, "
                "escalate to engineering. Engineering investigates and fixes. After fix, "
                "verify with customer. If customer satisfied, close and survey. If customer "
                "not satisfied, keep ticket open for further investigation."
            ),
            trajectory=[
                {
                    "reasoning": "3-way routing by category (billing/technical/general). First "
                    "contact resolution has XOR for resolve/escalate. Escalation chain: tier 1 "
                    "→ tier 2 → engineering. Final verification has satisfaction check.",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "PO=( "
                        "nodes={ "
                            "'Submit Ticket', "
                            "'Categorize', "
                            "X( "
                                "'Billing Specialist', "
                                "'Technical Support', "
                                "'General Support' "
                            "), "
                            "'First Contact Resolution', "
                            "X( "
                                "'Close Ticket', "
                                "'Tier 2 Escalation' "
                            "), "
                            "'Tier 2 Investigation', "
                            "X( "
                                "'Close Ticket', "
                                "'Engineering Escalation' "
                            "), "
                            "'Engineering Fix', "
                            "'Verify with Customer', "
                            "X( 'Close Ticket', 'Keep Open' ) "
                        "}, "
                        "order={ "
                            "'Submit Ticket'-->'Categorize', "
                            "'Categorize'-->X( "
                                "'Billing Specialist', "
                                "'Technical Support', "
                                "'General Support' "
                            "), "
                            "X( 'Billing Specialist', 'Technical Support', 'General Support' )-->'First Contact Resolution', "
                            "'First Contact Resolution'-->X( "
                                "'Close Ticket', "
                                "'Tier 2 Escalation' "
                            "), "
                            "'Tier 2 Escalation'-->'Tier 2 Investigation', "
                            "'Tier 2 Investigation'-->X( "
                                "'Close Ticket', "
                                "'Engineering Escalation' "
                            "), "
                            "'Engineering Escalation'-->'Engineering Fix', "
                            "'Engineering Fix'-->'Verify with Customer', "
                            "'Verify with Customer'-->X( 'Close Ticket', 'Keep Open' ) "
                        "} "
                    ")"},
                    "is_valid": True,
                    "errors": None,
                },
                {
                    "reasoning": "Valid support ticket POWL. Category-based routing. Resolution "
                    "attempts at each tier with escalation on failure. Engineering fix leads to "
                    "customer verification. Satisfaction check at end determines close or keep open.",
                    "selected_fn": "finish",
                    "args": {"powl_model": "PO=( nodes={ 'Submit Ticket', 'Categorize', X( 'Billing Specialist', 'Technical Support', 'General Support' ), 'First Contact Resolution', X( 'Close Ticket', 'Tier 2 Escalation' ), 'Tier 2 Investigation', X( 'Close Ticket', 'Engineering Escalation' ), 'Engineering Fix', 'Verify with Customer', X( 'Close Ticket', 'Keep Open' ) }, order={ 'Submit Ticket'-->'Categorize', 'Categorize'-->X( 'Billing Specialist', 'Technical Support', 'General Support' ), X( 'Billing Specialist', 'Technical Support', 'General Support' )-->'First Contact Resolution', 'First Contact Resolution'-->X( 'Close Ticket', 'Tier 2 Escalation' ), 'Tier 2 Escalation'-->'Tier 2 Investigation', 'Tier 2 Investigation'-->X( 'Close Ticket', 'Engineering Escalation' ), 'Engineering Escalation'-->'Engineering Fix', 'Engineering Fix'-->'Verify with Customer', 'Verify with Customer'-->X( 'Close Ticket', 'Keep Open' ) } )"},
                    "return_value": "PO=( nodes={ 'Submit Ticket', 'Categorize', X( 'Billing Specialist', 'Technical Support', 'General Support' ), 'First Contact Resolution', X( 'Close Ticket', 'Tier 2 Escalation' ), 'Tier 2 Investigation', X( 'Close Ticket', 'Engineering Escalation' ), 'Engineering Fix', 'Verify with Customer', X( 'Close Ticket', 'Keep Open' ) }, order={ 'Submit Ticket'-->'Categorize', 'Categorize'-->X( 'Billing Specialist', 'Technical Support', 'General Support' ), X( 'Billing Specialist', 'Technical Support', 'General Support' )-->'First Contact Resolution', 'First Contact Resolution'-->X( 'Close Ticket', 'Tier 2 Escalation' ), 'Tier 2 Escalation'-->'Tier 2 Investigation', 'Tier 2 Investigation'-->X( 'Close Ticket', 'Engineering Escalation' ), 'Engineering Escalation'-->'Engineering Fix', 'Engineering Fix'-->'Verify with Customer', 'Verify with Customer'-->X( 'Close Ticket', 'Keep Open' ) } )",
                    "errors": None,
                },
            ],
            next_selected_fn="finish",
            args={"powl_model": "PO=( nodes={ 'Submit Ticket', 'Categorize', X( 'Billing Specialist', 'Technical Support', 'General Support' ), 'First Contact Resolution', X( 'Close Ticket', 'Tier 2 Escalation' ), 'Tier 2 Investigation', X( 'Close Ticket', 'Engineering Escalation' ), 'Engineering Fix', 'Verify with Customer', X( 'Close Ticket', 'Keep Open' ) }, order={ 'Submit Ticket'-->'Categorize', 'Categorize'-->X( 'Billing Specialist', 'Technical Support', 'General Support' ), X( 'Billing Specialist', 'Technical Support', 'General Support' )-->'First Contact Resolution', 'First Contact Resolution'-->X( 'Close Ticket', 'Tier 2 Escalation' ), 'Tier 2 Escalation'-->'Tier 2 Investigation', 'Tier 2 Investigation'-->X( 'Close Ticket', 'Engineering Escalation' ), 'Engineering Escalation'-->'Engineering Fix', 'Engineering Fix'-->'Verify with Customer', 'Verify with Customer'-->X( 'Close Ticket', 'Keep Open' ) } )"},
        ),
        # Demo 15: Simple compliance review process
        dspy.Example(
            process_description=(
                "A compliance review process for financial transactions: Analyst receives "
                "transaction request. Analyst performs initial screening. If transaction "
                "amount under threshold, auto-approve. If amount over threshold, perform "
                "enhanced review. Enhanced review includes checking sanctions lists and "
                "verifying documentation. If sanctions list hit, block transaction and "
                "notify compliance officer. If documentation incomplete, request more "
                "docs from requester. If all checks pass, approve transaction. Notify "
                "requester of decision. Log transaction for audit trail."
            ),
            trajectory=[
                {
                    "reasoning": "Threshold-based routing with XOR for under/over amount. "
                    "Enhanced review has parallel checks (sanctions + documentation). "
                    "Multiple outcomes: block, request docs, approve. All paths end with "
                    "notify and log.",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "PO=( "
                        "nodes={ "
                            "'Receive Request', "
                            "'Initial Screening', "
                            "X( "
                                "'Auto Approve', "
                                "'Enhanced Review' "
                            "), "
                            "'Check Sanctions', "
                            "'Verify Documentation', "
                            "X( "
                                "'Block Transaction', "
                                "'Request More Docs', "
                                "'Approve Transaction' "
                            "), "
                            "'Notify Requester', "
                            "'Log Transaction' "
                        "}, "
                        "order={ "
                            "'Receive Request'-->'Initial Screening', "
                            "'Initial Screening'-->X( "
                                "'Auto Approve', "
                                "'Enhanced Review' "
                            "), "
                            "'Enhanced Review'-->'Check Sanctions', "
                            "'Check Sanctions'-->'Verify Documentation', "
                            "'Verify Documentation'-->X( "
                                "'Block Transaction', "
                                "'Request More Docs', "
                                "'Approve Transaction' "
                            "), "
                            "X( 'Block Transaction', 'Request More Docs', 'Approve Transaction' )-->'Notify Requester', "
                            "'Auto Approve'-->'Notify Requester', "
                            "'Notify Requester'-->'Log Transaction' "
                        "} "
                    ")"},
                    "is_valid": True,
                    "errors": None,
                },
                {
                    "reasoning": "Valid compliance review POWL. Threshold routing to auto-approve "
                    "or enhanced review. Enhanced review has sequential checks. Three outcomes: "
                    "block (sanctions hit), request docs (incomplete), or approve. All paths "
                    "converge to notify requester, then log for audit.",
                    "selected_fn": "finish",
                    "args": {"powl_model": "PO=( nodes={ 'Receive Request', 'Initial Screening', X( 'Auto Approve', 'Enhanced Review' ), 'Check Sanctions', 'Verify Documentation', X( 'Block Transaction', 'Request More Docs', 'Approve Transaction' ), 'Notify Requester', 'Log Transaction' }, order={ 'Receive Request'-->'Initial Screening', 'Initial Screening'-->X( 'Auto Approve', 'Enhanced Review' ), 'Enhanced Review'-->'Check Sanctions', 'Check Sanctions'-->'Verify Documentation', 'Verify Documentation'-->X( 'Block Transaction', 'Request More Docs', 'Approve Transaction' ), X( 'Block Transaction', 'Request More Docs', 'Approve Transaction' )-->'Notify Requester', 'Auto Approve'-->'Notify Requester', 'Notify Requester'-->'Log Transaction' } )"},
                    "return_value": "PO=( nodes={ 'Receive Request', 'Initial Screening', X( 'Auto Approve', 'Enhanced Review' ), 'Check Sanctions', 'Verify Documentation', X( 'Block Transaction', 'Request More Docs', 'Approve Transaction' ), 'Notify Requester', 'Log Transaction' }, order={ 'Receive Request'-->'Initial Screening', 'Initial Screening'-->X( 'Auto Approve', 'Enhanced Review' ), 'Enhanced Review'-->'Check Sanctions', 'Check Sanctions'-->'Verify Documentation', 'Verify Documentation'-->X( 'Block Transaction', 'Request More Docs', 'Approve Transaction' ), X( 'Block Transaction', 'Request More Docs', 'Approve Transaction' )-->'Notify Requester', 'Auto Approve'-->'Notify Requester', 'Notify Requester'-->'Log Transaction' } )",
                    "errors": None,
                },
            ],
            next_selected_fn="finish",
            args={"powl_model": "PO=( nodes={ 'Receive Request', 'Initial Screening', X( 'Auto Approve', 'Enhanced Review' ), 'Check Sanctions', 'Verify Documentation', X( 'Block Transaction', 'Request More Docs', 'Approve Transaction' ), 'Notify Requester', 'Log Transaction' }, order={ 'Receive Request'-->'Initial Screening', 'Initial Screening'-->X( 'Auto Approve', 'Enhanced Review' ), 'Enhanced Review'-->'Check Sanctions', 'Check Sanctions'-->'Verify Documentation', 'Verify Documentation'-->X( 'Block Transaction', 'Request More Docs', 'Approve Transaction' ), X( 'Block Transaction', 'Request More Docs', 'Approve Transaction' )-->'Notify Requester', 'Auto Approve'-->'Notify Requester', 'Notify Requester'-->'Log Transaction' } )"},
        ),
    ]

    for demo in demos:
        demo = demo.with_inputs("process_description", "trajectory", "functions")

    return demos
