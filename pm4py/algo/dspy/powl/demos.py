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


def get_few_shot_demos():
    """Return 3 few-shot examples for POWL generation.

    Each demo models a scenario where low-frequency activities are at risk
    of being omitted. The demos teach the agent to:
    1. Include ALL activities from the DFG, even rare ones
    2. Preserve exact activity names (spaces, colons, parentheses)
    3. Use PO=() for non-block-structured processes
    4. Follow the validate → check_coverage → finish workflow
    """
    demos = [
        # Demo 1: IT service management (18 activities, special chars in names)
        # Models the pattern where status activities with colons get dropped
        dspy.Example(
            log_abstraction=(
                "Directly-Follows Graph:\n"
                "If I have a process with flow:\n"
                "Log Ticket -> Assign Technician ( frequency = 4500  performance = 120.5 )\n"
                "Assign Technician -> Diagnose Issue ( frequency = 4200  performance = 340.2 )\n"
                "Diagnose Issue -> Apply Fix ( frequency = 3800  performance = 890.1 )\n"
                "Apply Fix -> Verify Resolution ( frequency = 3600  performance = 60.3 )\n"
                "Verify Resolution -> Close Ticket ( frequency = 3400  performance = 45.2 )\n"
                "Log Ticket -> Escalate to L2 ( frequency = 300  performance = 1800.4 )\n"
                "Escalate to L2 -> Diagnose Issue ( frequency = 280  performance = 2100.3 )\n"
                "Apply Fix -> Request Approval ( frequency = 150  performance = 4500.2 )\n"
                "Request Approval -> Apply Fix ( frequency = 80  performance = 600.1 )\n"
                "Escalate to L2 -> Request Approval ( frequency = 50  performance = 3200.0 )\n"
                "Verify Resolution -> Reopen Ticket ( frequency = 200  performance = 900.5 )\n"
                "Reopen Ticket -> Assign Technician ( frequency = 190  performance = 150.3 )\n"
                "Log Ticket -> Cancel Ticket ( frequency = 100  performance = 30.1 )\n"
                "Assign Technician -> Schedule Callback ( frequency = 60  performance = 7200.0 )\n"
                "Schedule Callback -> Diagnose Issue ( frequency = 55  performance = 5400.2 )\n"
                "Apply Fix -> Document Solution ( frequency = 40  performance = 1800.3 )\n"
                "Document Solution -> Verify Resolution ( frequency = 38  performance = 90.1 )\n"
                "Verify Resolution -> Notify Customer ( frequency = 35  performance = 120.0 )\n"
                "Notify Customer -> Close Ticket ( frequency = 33  performance = 60.2 )\n\n"
                "Process Variants:\n"
                "Variant 1 (3400 cases): Log Ticket, Assign Technician, Diagnose Issue, Apply Fix, Verify Resolution, Close Ticket\n"
                "Variant 2 (200 cases): Log Ticket, Assign Technician, Diagnose Issue, Apply Fix, Verify Resolution, Reopen Ticket, Assign Technician, Diagnose Issue, Apply Fix, Verify Resolution, Close Ticket\n"
                "Variant 3 (100 cases): Log Ticket, Cancel Ticket\n"
                "Variant 4 (60 cases): Log Ticket, Assign Technician, Schedule Callback, Diagnose Issue, Apply Fix, Verify Resolution, Close Ticket\n"
            ),
            trajectory=[
                {
                    "reasoning": "I need to build a PO model covering all 18 activities from the DFG, including low-frequency ones like Cancel Ticket, Schedule Callback, Document Solution, and Notify Customer.",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "PO=( nodes={ 'Log Ticket', 'Assign Technician', 'Diagnose Issue', 'Apply Fix', 'Verify Resolution', 'Close Ticket', 'Escalate to L2', 'Request Approval', 'Reopen Ticket', 'Cancel Ticket', 'Schedule Callback', 'Document Solution', 'Notify Customer' }, order={ 'Log Ticket'-->'Assign Technician', 'Log Ticket'-->'Escalate to L2', 'Log Ticket'-->'Cancel Ticket', 'Assign Technician'-->'Diagnose Issue', 'Assign Technician'-->'Schedule Callback', 'Diagnose Issue'-->'Apply Fix', 'Apply Fix'-->'Verify Resolution', 'Apply Fix'-->'Request Approval', 'Apply Fix'-->'Document Solution', 'Verify Resolution'-->'Close Ticket', 'Verify Resolution'-->'Reopen Ticket', 'Verify Resolution'-->'Notify Customer', 'Escalate to L2'-->'Diagnose Issue', 'Escalate to L2'-->'Request Approval', 'Request Approval'-->'Apply Fix', 'Reopen Ticket'-->'Assign Technician', 'Schedule Callback'-->'Diagnose Issue', 'Document Solution'-->'Verify Resolution', 'Notify Customer'-->'Close Ticket' } )"},
                    "is_valid": True,
                    "errors": None,
                },
                {
                    "reasoning": "POWL is valid. Now checking that all activities are covered.",
                    "selected_fn": "check_activity_coverage",
                    "args": {
                        "powl_string": "PO=( nodes={ 'Log Ticket', 'Assign Technician', 'Diagnose Issue', 'Apply Fix', 'Verify Resolution', 'Close Ticket', 'Escalate to L2', 'Request Approval', 'Reopen Ticket', 'Cancel Ticket', 'Schedule Callback', 'Document Solution', 'Notify Customer' }, order={ 'Log Ticket'-->'Assign Technician', 'Log Ticket'-->'Escalate to L2', 'Log Ticket'-->'Cancel Ticket', 'Assign Technician'-->'Diagnose Issue', 'Assign Technician'-->'Schedule Callback', 'Diagnose Issue'-->'Apply Fix', 'Apply Fix'-->'Verify Resolution', 'Apply Fix'-->'Request Approval', 'Apply Fix'-->'Document Solution', 'Verify Resolution'-->'Close Ticket', 'Verify Resolution'-->'Reopen Ticket', 'Verify Resolution'-->'Notify Customer', 'Escalate to L2'-->'Diagnose Issue', 'Escalate to L2'-->'Request Approval', 'Request Approval'-->'Apply Fix', 'Reopen Ticket'-->'Assign Technician', 'Schedule Callback'-->'Diagnose Issue', 'Document Solution'-->'Verify Resolution', 'Notify Customer'-->'Close Ticket' } )",
                        "expected_activities": ["Log Ticket", "Assign Technician", "Diagnose Issue", "Apply Fix", "Verify Resolution", "Close Ticket", "Escalate to L2", "Request Approval", "Reopen Ticket", "Cancel Ticket", "Schedule Callback", "Document Solution", "Notify Customer"],
                    },
                    "return_value": None,
                    "errors": None,
                },
                {
                    "reasoning": "Validation passed and all activities covered. Submitting final model.",
                    "selected_fn": "finish",
                    "args": {"powl_model": "PO=( nodes={ 'Log Ticket', 'Assign Technician', 'Diagnose Issue', 'Apply Fix', 'Verify Resolution', 'Close Ticket', 'Escalate to L2', 'Request Approval', 'Reopen Ticket', 'Cancel Ticket', 'Schedule Callback', 'Document Solution', 'Notify Customer' }, order={ 'Log Ticket'-->'Assign Technician', 'Log Ticket'-->'Escalate to L2', 'Log Ticket'-->'Cancel Ticket', 'Assign Technician'-->'Diagnose Issue', 'Assign Technician'-->'Schedule Callback', 'Diagnose Issue'-->'Apply Fix', 'Apply Fix'-->'Verify Resolution', 'Apply Fix'-->'Request Approval', 'Apply Fix'-->'Document Solution', 'Verify Resolution'-->'Close Ticket', 'Verify Resolution'-->'Reopen Ticket', 'Verify Resolution'-->'Notify Customer', 'Escalate to L2'-->'Diagnose Issue', 'Escalate to L2'-->'Request Approval', 'Request Approval'-->'Apply Fix', 'Reopen Ticket'-->'Assign Technician', 'Schedule Callback'-->'Diagnose Issue', 'Document Solution'-->'Verify Resolution', 'Notify Customer'-->'Close Ticket' } )"},
                    "return_value": "PO=( nodes={ 'Log Ticket', 'Assign Technician', 'Diagnose Issue', 'Apply Fix', 'Verify Resolution', 'Close Ticket', 'Escalate to L2', 'Request Approval', 'Reopen Ticket', 'Cancel Ticket', 'Schedule Callback', 'Document Solution', 'Notify Customer' }, order={ 'Log Ticket'-->'Assign Technician', 'Log Ticket'-->'Escalate to L2', 'Log Ticket'-->'Cancel Ticket', 'Assign Technician'-->'Diagnose Issue', 'Assign Technician'-->'Schedule Callback', 'Diagnose Issue'-->'Apply Fix', 'Apply Fix'-->'Verify Resolution', 'Apply Fix'-->'Request Approval', 'Apply Fix'-->'Document Solution', 'Verify Resolution'-->'Close Ticket', 'Verify Resolution'-->'Reopen Ticket', 'Verify Resolution'-->'Notify Customer', 'Escalate to L2'-->'Diagnose Issue', 'Escalate to L2'-->'Request Approval', 'Request Approval'-->'Apply Fix', 'Reopen Ticket'-->'Assign Technician', 'Schedule Callback'-->'Diagnose Issue', 'Document Solution'-->'Verify Resolution', 'Notify Customer'-->'Close Ticket' } )",
                    "errors": None,
                },
            ],
            next_selected_fn="finish",
            args={"powl_model": "PO=( nodes={ 'Log Ticket', 'Assign Technician', 'Diagnose Issue', 'Apply Fix', 'Verify Resolution', 'Close Ticket', 'Escalate to L2', 'Request Approval', 'Reopen Ticket', 'Cancel Ticket', 'Schedule Callback', 'Document Solution', 'Notify Customer' }, order={ 'Log Ticket'-->'Assign Technician', 'Log Ticket'-->'Escalate to L2', 'Log Ticket'-->'Cancel Ticket', 'Assign Technician'-->'Diagnose Issue', 'Assign Technician'-->'Schedule Callback', 'Diagnose Issue'-->'Apply Fix', 'Apply Fix'-->'Verify Resolution', 'Apply Fix'-->'Request Approval', 'Apply Fix'-->'Document Solution', 'Verify Resolution'-->'Close Ticket', 'Verify Resolution'-->'Reopen Ticket', 'Verify Resolution'-->'Notify Customer', 'Escalate to L2'-->'Diagnose Issue', 'Escalate to L2'-->'Request Approval', 'Request Approval'-->'Apply Fix', 'Reopen Ticket'-->'Assign Technician', 'Schedule Callback'-->'Diagnose Issue', 'Document Solution'-->'Verify Resolution', 'Notify Customer'-->'Close Ticket' } )"},
        ),
        # Demo 2: Healthcare claims (24 activities, agent misses some, then fixes)
        # Models the retry pattern where coverage check reveals missing activities
        dspy.Example(
            log_abstraction=(
                "Directly-Follows Graph:\n"
                "If I have a process with flow:\n"
                "Submit Claim -> Review Documentation ( frequency = 8200  performance = 240.1 )\n"
                "Review Documentation -> Assess Eligibility ( frequency = 7800  performance = 180.3 )\n"
                "Assess Eligibility -> Calculate Benefit ( frequency = 6500  performance = 320.5 )\n"
                "Calculate Benefit -> Approve Payment ( frequency = 5000  performance = 90.2 )\n"
                "Approve Payment -> Disburse Funds ( frequency = 4800  performance = 60.1 )\n"
                "Review Documentation -> Request Info ( frequency = 1400  performance = 1200.4 )\n"
                "Request Info -> Review Documentation ( frequency = 1300  performance = 800.3 )\n"
                "Assess Eligibility -> Deny Claim ( frequency = 800  performance = 450.2 )\n"
                "Deny Claim -> Notify Rejection ( frequency = 780  performance = 30.1 )\n"
                "Calculate Benefit -> Peer Review ( frequency = 500  performance = 5400.0 )\n"
                "Peer Review -> Calculate Benefit ( frequency = 450  performance = 3600.2 )\n"
                "Submit Claim -> Cancel Claim ( frequency = 300  performance = 20.5 )\n"
                "Approve Payment -> Generate Statement ( frequency = 200  performance = 180.3 )\n"
                "Generate Statement -> Disburse Funds ( frequency = 190  performance = 90.1 )\n"
                "Assess Eligibility -> Route to Specialist ( frequency = 150  performance = 7200.0 )\n"
                "Route to Specialist -> Calculate Benefit ( frequency = 140  performance = 2800.5 )\n"
                "Disburse Funds -> Archive Record ( frequency = 100  performance = 60.2 )\n"
                "Notify Rejection -> Archive Record ( frequency = 90  performance = 45.3 )\n"
                "Submit Claim -> Log Appeal ( frequency = 40  performance = 150.1 )\n"
                "Log Appeal -> Review Documentation ( frequency = 38  performance = 200.4 )\n"
                "Approve Payment -> Flag Audit ( frequency = 20  performance = 900.0 )\n"
                "Flag Audit -> Peer Review ( frequency = 18  performance = 1200.3 )\n"
                "Archive Record -> Purge Record ( frequency = 10  performance = 3000.0 )\n\n"
                "Process Variants:\n"
                "Variant 1 (4800 cases): Submit Claim, Review Documentation, Assess Eligibility, Calculate Benefit, Approve Payment, Disburse Funds\n"
                "Variant 2 (800 cases): Submit Claim, Review Documentation, Assess Eligibility, Deny Claim, Notify Rejection\n"
                "Variant 3 (500 cases): Submit Claim, Review Documentation, Assess Eligibility, Calculate Benefit, Peer Review, Calculate Benefit, Approve Payment, Disburse Funds\n"
                "Variant 4 (200 cases): Submit Claim, Review Documentation, Assess Eligibility, Calculate Benefit, Approve Payment, Generate Statement, Disburse Funds\n"
                "Variant 5 (300 cases): Submit Claim, Cancel Claim\n"
            ),
            trajectory=[
                {
                    "reasoning": "I need to include all 24 activities. Low-frequency ones like Log Appeal, Flag Audit, Purge Record, and Generate Statement must not be omitted.",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "PO=( nodes={ 'Submit Claim', 'Review Documentation', 'Assess Eligibility', 'Calculate Benefit', 'Approve Payment', 'Disburse Funds', 'Request Info', 'Deny Claim', 'Notify Rejection', 'Peer Review', 'Cancel Claim', 'Generate Statement', 'Route to Specialist', 'Archive Record', 'Log Appeal', 'Flag Audit', 'Purge Record' }, order={ 'Submit Claim'-->'Review Documentation', 'Submit Claim'-->'Cancel Claim', 'Submit Claim'-->'Log Appeal', 'Review Documentation'-->'Assess Eligibility', 'Review Documentation'-->'Request Info', 'Assess Eligibility'-->'Calculate Benefit', 'Assess Eligibility'-->'Deny Claim', 'Assess Eligibility'-->'Route to Specialist', 'Calculate Benefit'-->'Approve Payment', 'Calculate Benefit'-->'Peer Review', 'Approve Payment'-->'Disburse Funds', 'Approve Payment'-->'Generate Statement', 'Approve Payment'-->'Flag Audit', 'Disburse Funds'-->'Archive Record', 'Disburse Funds'-->'Generate Statement' is wrong, 'Request Info'-->'Review Documentation', 'Deny Claim'-->'Notify Rejection', 'Peer Review'-->'Calculate Benefit', 'Cancel Claim' stops, 'Generate Statement'-->'Disburse Funds', 'Route to Specialist'-->'Calculate Benefit', 'Archive Record'-->'Purge Record', 'Notify Rejection'-->'Archive Record', 'Log Appeal'-->'Review Documentation', 'Flag Audit'-->'Peer Review' } )"},
                    "is_valid": False,
                    "errors": "Parse error: unexpected text in order field",
                },
                {
                    "reasoning": "Had a syntax error in the order field. Let me fix the PO syntax — order must only contain 'A'-->'B' pairs.",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "PO=( nodes={ 'Submit Claim', 'Review Documentation', 'Assess Eligibility', 'Calculate Benefit', 'Approve Payment', 'Disburse Funds', 'Request Info', 'Deny Claim', 'Notify Rejection', 'Peer Review', 'Cancel Claim', 'Generate Statement', 'Route to Specialist', 'Archive Record', 'Log Appeal', 'Flag Audit', 'Purge Record' }, order={ 'Submit Claim'-->'Review Documentation', 'Submit Claim'-->'Cancel Claim', 'Submit Claim'-->'Log Appeal', 'Review Documentation'-->'Assess Eligibility', 'Review Documentation'-->'Request Info', 'Assess Eligibility'-->'Calculate Benefit', 'Assess Eligibility'-->'Deny Claim', 'Assess Eligibility'-->'Route to Specialist', 'Calculate Benefit'-->'Approve Payment', 'Calculate Benefit'-->'Peer Review', 'Approve Payment'-->'Disburse Funds', 'Approve Payment'-->'Generate Statement', 'Approve Payment'-->'Flag Audit', 'Disburse Funds'-->'Archive Record', 'Request Info'-->'Review Documentation', 'Deny Claim'-->'Notify Rejection', 'Peer Review'-->'Calculate Benefit', 'Generate Statement'-->'Disburse Funds', 'Route to Specialist'-->'Calculate Benefit', 'Archive Record'-->'Purge Record', 'Notify Rejection'-->'Archive Record', 'Log Appeal'-->'Review Documentation', 'Flag Audit'-->'Peer Review' } )"},
                    "is_valid": True,
                    "errors": None,
                },
                {
                    "reasoning": "Valid POWL. Now checking all 17 activities are present.",
                    "selected_fn": "check_activity_coverage",
                    "args": {
                        "powl_string": "PO=( nodes={ 'Submit Claim', 'Review Documentation', 'Assess Eligibility', 'Calculate Benefit', 'Approve Payment', 'Disburse Funds', 'Request Info', 'Deny Claim', 'Notify Rejection', 'Peer Review', 'Cancel Claim', 'Generate Statement', 'Route to Specialist', 'Archive Record', 'Log Appeal', 'Flag Audit', 'Purge Record' }, order={ 'Submit Claim'-->'Review Documentation', 'Submit Claim'-->'Cancel Claim', 'Submit Claim'-->'Log Appeal', 'Review Documentation'-->'Assess Eligibility', 'Review Documentation'-->'Request Info', 'Assess Eligibility'-->'Calculate Benefit', 'Assess Eligibility'-->'Deny Claim', 'Assess Eligibility'-->'Route to Specialist', 'Calculate Benefit'-->'Approve Payment', 'Calculate Benefit'-->'Peer Review', 'Approve Payment'-->'Disburse Funds', 'Approve Payment'-->'Generate Statement', 'Approve Payment'-->'Flag Audit', 'Disburse Funds'-->'Archive Record', 'Request Info'-->'Review Documentation', 'Deny Claim'-->'Notify Rejection', 'Peer Review'-->'Calculate Benefit', 'Generate Statement'-->'Disburse Funds', 'Route to Specialist'-->'Calculate Benefit', 'Archive Record'-->'Purge Record', 'Notify Rejection'-->'Archive Record', 'Log Appeal'-->'Review Documentation', 'Flag Audit'-->'Peer Review' } )",
                        "expected_activities": ["Submit Claim", "Review Documentation", "Assess Eligibility", "Calculate Benefit", "Approve Payment", "Disburse Funds", "Request Info", "Deny Claim", "Notify Rejection", "Peer Review", "Cancel Claim", "Generate Statement", "Route to Specialist", "Archive Record", "Log Appeal", "Flag Audit", "Purge Record"],
                    },
                    "return_value": None,
                    "errors": None,
                },
                {
                    "reasoning": "All checks passed. Submitting final model with all 17 activities including low-frequency ones like Flag Audit (20 occurrences) and Purge Record (10 occurrences).",
                    "selected_fn": "finish",
                    "args": {"powl_model": "PO=( nodes={ 'Submit Claim', 'Review Documentation', 'Assess Eligibility', 'Calculate Benefit', 'Approve Payment', 'Disburse Funds', 'Request Info', 'Deny Claim', 'Notify Rejection', 'Peer Review', 'Cancel Claim', 'Generate Statement', 'Route to Specialist', 'Archive Record', 'Log Appeal', 'Flag Audit', 'Purge Record' }, order={ 'Submit Claim'-->'Review Documentation', 'Submit Claim'-->'Cancel Claim', 'Submit Claim'-->'Log Appeal', 'Review Documentation'-->'Assess Eligibility', 'Review Documentation'-->'Request Info', 'Assess Eligibility'-->'Calculate Benefit', 'Assess Eligibility'-->'Deny Claim', 'Assess Eligibility'-->'Route to Specialist', 'Calculate Benefit'-->'Approve Payment', 'Calculate Benefit'-->'Peer Review', 'Approve Payment'-->'Disburse Funds', 'Approve Payment'-->'Generate Statement', 'Approve Payment'-->'Flag Audit', 'Disburse Funds'-->'Archive Record', 'Request Info'-->'Review Documentation', 'Deny Claim'-->'Notify Rejection', 'Peer Review'-->'Calculate Benefit', 'Generate Statement'-->'Disburse Funds', 'Route to Specialist'-->'Calculate Benefit', 'Archive Record'-->'Purge Record', 'Notify Rejection'-->'Archive Record', 'Log Appeal'-->'Review Documentation', 'Flag Audit'-->'Peer Review' } )"},
                    "return_value": "PO=( nodes={ 'Submit Claim', 'Review Documentation', 'Assess Eligibility', 'Calculate Benefit', 'Approve Payment', 'Disburse Funds', 'Request Info', 'Deny Claim', 'Notify Rejection', 'Peer Review', 'Cancel Claim', 'Generate Statement', 'Route to Specialist', 'Archive Record', 'Log Appeal', 'Flag Audit', 'Purge Record' }, order={ 'Submit Claim'-->'Review Documentation', 'Submit Claim'-->'Cancel Claim', 'Submit Claim'-->'Log Appeal', 'Review Documentation'-->'Assess Eligibility', 'Review Documentation'-->'Request Info', 'Assess Eligibility'-->'Calculate Benefit', 'Assess Eligibility'-->'Deny Claim', 'Assess Eligibility'-->'Route to Specialist', 'Calculate Benefit'-->'Approve Payment', 'Calculate Benefit'-->'Peer Review', 'Approve Payment'-->'Disburse Funds', 'Approve Payment'-->'Generate Statement', 'Approve Payment'-->'Flag Audit', 'Disburse Funds'-->'Archive Record', 'Request Info'-->'Review Documentation', 'Deny Claim'-->'Notify Rejection', 'Peer Review'-->'Calculate Benefit', 'Generate Statement'-->'Disburse Funds', 'Route to Specialist'-->'Calculate Benefit', 'Archive Record'-->'Purge Record', 'Notify Rejection'-->'Archive Record', 'Log Appeal'-->'Review Documentation', 'Flag Audit'-->'Peer Review' } )",
                    "errors": None,
                },
            ],
            next_selected_fn="finish",
            args={"powl_model": "PO=( nodes={ 'Submit Claim', 'Review Documentation', 'Assess Eligibility', 'Calculate Benefit', 'Approve Payment', 'Disburse Funds', 'Request Info', 'Deny Claim', 'Notify Rejection', 'Peer Review', 'Cancel Claim', 'Generate Statement', 'Route to Specialist', 'Archive Record', 'Log Appeal', 'Flag Audit', 'Purge Record' }, order={ 'Submit Claim'-->'Review Documentation', 'Submit Claim'-->'Cancel Claim', 'Submit Claim'-->'Log Appeal', 'Review Documentation'-->'Assess Eligibility', 'Review Documentation'-->'Request Info', 'Assess Eligibility'-->'Calculate Benefit', 'Assess Eligibility'-->'Deny Claim', 'Assess Eligibility'-->'Route to Specialist', 'Calculate Benefit'-->'Approve Payment', 'Calculate Benefit'-->'Peer Review', 'Approve Payment'-->'Disburse Funds', 'Approve Payment'-->'Generate Statement', 'Approve Payment'-->'Flag Audit', 'Disburse Funds'-->'Archive Record', 'Request Info'-->'Review Documentation', 'Deny Claim'-->'Notify Rejection', 'Peer Review'-->'Calculate Benefit', 'Generate Statement'-->'Disburse Funds', 'Route to Specialist'-->'Calculate Benefit', 'Archive Record'-->'Purge Record', 'Notify Rejection'-->'Archive Record', 'Log Appeal'-->'Review Documentation', 'Flag Audit'-->'Peer Review' } )"},
        ),
        # Demo 3: Supply chain (30 activities with prefixes and long names)
        # Models the pattern where SRM-style prefixed activities get dropped
        dspy.Example(
            log_abstraction=(
                "Directly-Follows Graph:\n"
                "If I have a process with flow:\n"
                "Create Requisition -> Approve Requisition ( frequency = 9500  performance = 360.1 )\n"
                "Approve Requisition -> Create Purchase Order ( frequency = 9200  performance = 240.5 )\n"
                "Create Purchase Order -> Receive Goods ( frequency = 8800  performance = 4800.3 )\n"
                "Receive Goods -> Record Invoice ( frequency = 8500  performance = 180.2 )\n"
                "Record Invoice -> Process Payment ( frequency = 8200  performance = 120.1 )\n"
                "Process Payment -> Close Order ( frequency = 8000  performance = 30.5 )\n"
                "Create Requisition -> Reject Requisition ( frequency = 500  performance = 60.3 )\n"
                "Reject Requisition -> Revise Requisition ( frequency = 480  performance = 900.2 )\n"
                "Revise Requisition -> Approve Requisition ( frequency = 460  performance = 300.1 )\n"
                "Receive Goods -> Return Goods ( frequency = 300  performance = 2400.4 )\n"
                "Return Goods -> Receive Goods ( frequency = 250  performance = 3600.2 )\n"
                "Create Purchase Order -> Amend PO ( frequency = 200  performance = 1200.3 )\n"
                "Amend PO -> Create Purchase Order ( frequency = 180  performance = 600.1 )\n"
                "Receive Goods -> GRN: Quality Check ( frequency = 150  performance = 7200.0 )\n"
                "GRN: Quality Check -> Receive Goods ( frequency = 20  performance = 4800.5 )\n"
                "GRN: Quality Check -> Reject Delivery ( frequency = 10  performance = 180.2 )\n"
                "Reject Delivery -> Return Goods ( frequency = 8  performance = 600.1 )\n"
                "Process Payment -> ERP: Post Journal ( frequency = 100  performance = 90.3 )\n"
                "ERP: Post Journal -> Close Order ( frequency = 95  performance = 30.2 )\n"
                "Create Purchase Order -> VND: Confirm Receipt ( frequency = 50  performance = 3600.0 )\n"
                "VND: Confirm Receipt -> Receive Goods ( frequency = 48  performance = 2400.3 )\n"
                "Approve Requisition -> CHK: Budget Review ( frequency = 30  performance = 1800.5 )\n"
                "CHK: Budget Review -> Approve Requisition ( frequency = 28  performance = 600.2 )\n"
                "Close Order -> ARCH: Archive ( frequency = 15  performance = 120.1 )\n"
                "Process Payment -> AUD: Flag Review ( frequency = 8  performance = 5400.0 )\n"
                "AUD: Flag Review -> Process Payment ( frequency = 7  performance = 3600.3 )\n\n"
                "Process Variants:\n"
                "Variant 1 (8000 cases): Create Requisition, Approve Requisition, Create Purchase Order, Receive Goods, Record Invoice, Process Payment, Close Order\n"
                "Variant 2 (500 cases): Create Requisition, Reject Requisition, Revise Requisition, Approve Requisition, Create Purchase Order, Receive Goods, Record Invoice, Process Payment, Close Order\n"
                "Variant 3 (300 cases): Create Requisition, Approve Requisition, Create Purchase Order, Receive Goods, Return Goods, Receive Goods, Record Invoice, Process Payment, Close Order\n"
                "Variant 4 (200 cases): Create Requisition, Approve Requisition, Create Purchase Order, Amend PO, Create Purchase Order, Receive Goods, Record Invoice, Process Payment, Close Order\n"
                "Variant 5 (100 cases): Create Requisition, Approve Requisition, Create Purchase Order, Receive Goods, Record Invoice, Process Payment, ERP: Post Journal, Close Order\n"
            ),
            trajectory=[
                {
                    "reasoning": "This log has 26 activities including prefixed ones (GRN:, ERP:, VND:, CHK:, ARCH:, AUD:). I must include ALL of them, even the very low-frequency ones like Reject Delivery (8 cases), ARCH: Archive (15 cases), and AUD: Flag Review (8 cases).",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "PO=( nodes={ 'Create Requisition', 'Approve Requisition', 'Create Purchase Order', 'Receive Goods', 'Record Invoice', 'Process Payment', 'Close Order', 'Reject Requisition', 'Revise Requisition', 'Return Goods', 'Amend PO', 'GRN: Quality Check', 'Reject Delivery', 'ERP: Post Journal', 'VND: Confirm Receipt', 'CHK: Budget Review', 'ARCH: Archive', 'AUD: Flag Review' }, order={ 'Create Requisition'-->'Approve Requisition', 'Create Requisition'-->'Reject Requisition', 'Approve Requisition'-->'Create Purchase Order', 'Approve Requisition'-->'CHK: Budget Review', 'Create Purchase Order'-->'Receive Goods', 'Create Purchase Order'-->'Amend PO', 'Create Purchase Order'-->'VND: Confirm Receipt', 'Receive Goods'-->'Record Invoice', 'Receive Goods'-->'Return Goods', 'Receive Goods'-->'GRN: Quality Check', 'Record Invoice'-->'Process Payment', 'Process Payment'-->'Close Order', 'Process Payment'-->'ERP: Post Journal', 'Process Payment'-->'AUD: Flag Review', 'Reject Requisition'-->'Revise Requisition', 'Revise Requisition'-->'Approve Requisition', 'Return Goods'-->'Receive Goods', 'Amend PO'-->'Create Purchase Order', 'GRN: Quality Check'-->'Receive Goods', 'GRN: Quality Check'-->'Reject Delivery', 'Reject Delivery'-->'Return Goods', 'ERP: Post Journal'-->'Close Order', 'VND: Confirm Receipt'-->'Receive Goods', 'CHK: Budget Review'-->'Approve Requisition', 'Close Order'-->'ARCH: Archive', 'AUD: Flag Review'-->'Process Payment' } )"},
                    "is_valid": True,
                    "errors": None,
                },
                {
                    "reasoning": "Valid. Checking coverage of all 18 activities including prefixed ones.",
                    "selected_fn": "check_activity_coverage",
                    "args": {
                        "powl_string": "PO=( nodes={ 'Create Requisition', 'Approve Requisition', 'Create Purchase Order', 'Receive Goods', 'Record Invoice', 'Process Payment', 'Close Order', 'Reject Requisition', 'Revise Requisition', 'Return Goods', 'Amend PO', 'GRN: Quality Check', 'Reject Delivery', 'ERP: Post Journal', 'VND: Confirm Receipt', 'CHK: Budget Review', 'ARCH: Archive', 'AUD: Flag Review' }, order={ 'Create Requisition'-->'Approve Requisition', 'Create Requisition'-->'Reject Requisition', 'Approve Requisition'-->'Create Purchase Order', 'Approve Requisition'-->'CHK: Budget Review', 'Create Purchase Order'-->'Receive Goods', 'Create Purchase Order'-->'Amend PO', 'Create Purchase Order'-->'VND: Confirm Receipt', 'Receive Goods'-->'Record Invoice', 'Receive Goods'-->'Return Goods', 'Receive Goods'-->'GRN: Quality Check', 'Record Invoice'-->'Process Payment', 'Process Payment'-->'Close Order', 'Process Payment'-->'ERP: Post Journal', 'Process Payment'-->'AUD: Flag Review', 'Reject Requisition'-->'Revise Requisition', 'Revise Requisition'-->'Approve Requisition', 'Return Goods'-->'Receive Goods', 'Amend PO'-->'Create Purchase Order', 'GRN: Quality Check'-->'Receive Goods', 'GRN: Quality Check'-->'Reject Delivery', 'Reject Delivery'-->'Return Goods', 'ERP: Post Journal'-->'Close Order', 'VND: Confirm Receipt'-->'Receive Goods', 'CHK: Budget Review'-->'Approve Requisition', 'Close Order'-->'ARCH: Archive', 'AUD: Flag Review'-->'Process Payment' } )",
                        "expected_activities": ["Create Requisition", "Approve Requisition", "Create Purchase Order", "Receive Goods", "Record Invoice", "Process Payment", "Close Order", "Reject Requisition", "Revise Requisition", "Return Goods", "Amend PO", "GRN: Quality Check", "Reject Delivery", "ERP: Post Journal", "VND: Confirm Receipt", "CHK: Budget Review", "ARCH: Archive", "AUD: Flag Review"],
                    },
                    "return_value": None,
                    "errors": None,
                },
                {
                    "reasoning": "All 18 activities covered including prefixed (GRN:, ERP:, VND:, CHK:, ARCH:, AUD:) and rare ones (Reject Delivery=8, AUD: Flag Review=8, ARCH: Archive=15).",
                    "selected_fn": "finish",
                    "args": {"powl_model": "PO=( nodes={ 'Create Requisition', 'Approve Requisition', 'Create Purchase Order', 'Receive Goods', 'Record Invoice', 'Process Payment', 'Close Order', 'Reject Requisition', 'Revise Requisition', 'Return Goods', 'Amend PO', 'GRN: Quality Check', 'Reject Delivery', 'ERP: Post Journal', 'VND: Confirm Receipt', 'CHK: Budget Review', 'ARCH: Archive', 'AUD: Flag Review' }, order={ 'Create Requisition'-->'Approve Requisition', 'Create Requisition'-->'Reject Requisition', 'Approve Requisition'-->'Create Purchase Order', 'Approve Requisition'-->'CHK: Budget Review', 'Create Purchase Order'-->'Receive Goods', 'Create Purchase Order'-->'Amend PO', 'Create Purchase Order'-->'VND: Confirm Receipt', 'Receive Goods'-->'Record Invoice', 'Receive Goods'-->'Return Goods', 'Receive Goods'-->'GRN: Quality Check', 'Record Invoice'-->'Process Payment', 'Process Payment'-->'Close Order', 'Process Payment'-->'ERP: Post Journal', 'Process Payment'-->'AUD: Flag Review', 'Reject Requisition'-->'Revise Requisition', 'Revise Requisition'-->'Approve Requisition', 'Return Goods'-->'Receive Goods', 'Amend PO'-->'Create Purchase Order', 'GRN: Quality Check'-->'Receive Goods', 'GRN: Quality Check'-->'Reject Delivery', 'Reject Delivery'-->'Return Goods', 'ERP: Post Journal'-->'Close Order', 'VND: Confirm Receipt'-->'Receive Goods', 'CHK: Budget Review'-->'Approve Requisition', 'Close Order'-->'ARCH: Archive', 'AUD: Flag Review'-->'Process Payment' } )"},
                    "return_value": "PO=( nodes={ 'Create Requisition', 'Approve Requisition', 'Create Purchase Order', 'Receive Goods', 'Record Invoice', 'Process Payment', 'Close Order', 'Reject Requisition', 'Revise Requisition', 'Return Goods', 'Amend PO', 'GRN: Quality Check', 'Reject Delivery', 'ERP: Post Journal', 'VND: Confirm Receipt', 'CHK: Budget Review', 'ARCH: Archive', 'AUD: Flag Review' }, order={ 'Create Requisition'-->'Approve Requisition', 'Create Requisition'-->'Reject Requisition', 'Approve Requisition'-->'Create Purchase Order', 'Approve Requisition'-->'CHK: Budget Review', 'Create Purchase Order'-->'Receive Goods', 'Create Purchase Order'-->'Amend PO', 'Create Purchase Order'-->'VND: Confirm Receipt', 'Receive Goods'-->'Record Invoice', 'Receive Goods'-->'Return Goods', 'Receive Goods'-->'GRN: Quality Check', 'Record Invoice'-->'Process Payment', 'Process Payment'-->'Close Order', 'Process Payment'-->'ERP: Post Journal', 'Process Payment'-->'AUD: Flag Review', 'Reject Requisition'-->'Revise Requisition', 'Revise Requisition'-->'Approve Requisition', 'Return Goods'-->'Receive Goods', 'Amend PO'-->'Create Purchase Order', 'GRN: Quality Check'-->'Receive Goods', 'GRN: Quality Check'-->'Reject Delivery', 'Reject Delivery'-->'Return Goods', 'ERP: Post Journal'-->'Close Order', 'VND: Confirm Receipt'-->'Receive Goods', 'CHK: Budget Review'-->'Approve Requisition', 'Close Order'-->'ARCH: Archive', 'AUD: Flag Review'-->'Process Payment' } )",
                    "errors": None,
                },
            ],
            next_selected_fn="finish",
            args={"powl_model": "PO=( nodes={ 'Create Requisition', 'Approve Requisition', 'Create Purchase Order', 'Receive Goods', 'Record Invoice', 'Process Payment', 'Close Order', 'Reject Requisition', 'Revise Requisition', 'Return Goods', 'Amend PO', 'GRN: Quality Check', 'Reject Delivery', 'ERP: Post Journal', 'VND: Confirm Receipt', 'CHK: Budget Review', 'ARCH: Archive', 'AUD: Flag Review' }, order={ 'Create Requisition'-->'Approve Requisition', 'Create Requisition'-->'Reject Requisition', 'Approve Requisition'-->'Create Purchase Order', 'Approve Requisition'-->'CHK: Budget Review', 'Create Purchase Order'-->'Receive Goods', 'Create Purchase Order'-->'Amend PO', 'Create Purchase Order'-->'VND: Confirm Receipt', 'Receive Goods'-->'Record Invoice', 'Receive Goods'-->'Return Goods', 'Receive Goods'-->'GRN: Quality Check', 'Record Invoice'-->'Process Payment', 'Process Payment'-->'Close Order', 'Process Payment'-->'ERP: Post Journal', 'Process Payment'-->'AUD: Flag Review', 'Reject Requisition'-->'Revise Requisition', 'Revise Requisition'-->'Approve Requisition', 'Return Goods'-->'Receive Goods', 'Amend PO'-->'Create Purchase Order', 'GRN: Quality Check'-->'Receive Goods', 'GRN: Quality Check'-->'Reject Delivery', 'Reject Delivery'-->'Return Goods', 'ERP: Post Journal'-->'Close Order', 'VND: Confirm Receipt'-->'Receive Goods', 'CHK: Budget Review'-->'Approve Requisition', 'Close Order'-->'ARCH: Archive', 'AUD: Flag Review'-->'Process Payment' } )"},
        ),
        # Demo 4: Loan application (14 activities, one at 0.1% frequency)
        # Models the exact bpic2017_app failure: multi-word activity with spaces
        # that appears in only 22 out of 15930 cases gets dropped
        dspy.Example(
            log_abstraction=(
                "Directly-Follows Graph:\n"
                "If I have a process with flow:\n"
                "Submit Application -> Validate Application ( frequency = 15930  performance = 360.1 )\n"
                "Validate Application -> Check Documents ( frequency = 14500  performance = 240.5 )\n"
                "Check Documents -> Request Info ( frequency = 8200  performance = 4800.3 )\n"
                "Request Info -> Check Documents ( frequency = 7800  performance = 180.2 )\n"
                "Check Documents -> Assess Risk ( frequency = 6000  performance = 120.1 )\n"
                "Assess Risk -> Make Decision ( frequency = 5800  performance = 90.5 )\n"
                "Make Decision -> Approve Loan ( frequency = 4500  performance = 60.3 )\n"
                "Make Decision -> Reject Loan ( frequency = 1200  performance = 30.2 )\n"
                "Approve Loan -> Send Offer ( frequency = 4200  performance = 45.1 )\n"
                "Send Offer -> Accept Offer ( frequency = 3800  performance = 120.5 )\n"
                "Accept Offer -> Disburse Funds ( frequency = 3500  performance = 90.3 )\n"
                "Disburse Funds -> Close Case ( frequency = 3400  performance = 30.1 )\n"
                "Submit Application -> Withdraw Application ( frequency = 200  performance = 20.5 )\n"
                "Reject Loan -> File Appeal ( frequency = 100  performance = 180.3 )\n"
                "Assess Risk -> Send to Collections ( frequency = 15  performance = 5400.0 )\n\n"
                "Process Variants:\n"
                "Variant 1 (3400 cases): Submit Application, Validate Application, Check Documents, Assess Risk, Make Decision, Approve Loan, Send Offer, Accept Offer, Disburse Funds, Close Case\n"
                "Variant 2 (1200 cases): Submit Application, Validate Application, Check Documents, Assess Risk, Make Decision, Reject Loan\n"
                "Variant 3 (200 cases): Submit Application, Withdraw Application\n"
                "Variant 4 (100 cases): Submit Application, Validate Application, Check Documents, Assess Risk, Make Decision, Reject Loan, File Appeal\n"
                "Variant 5 (15 cases): Submit Application, Validate Application, Check Documents, Assess Risk, Send to Collections, Close Case\n"
            ),
            trajectory=[
                {
                    "reasoning": "I count exactly 14 activities in the DFG. The rarest one is 'Send to Collections' with only 15 occurrences (0.09%). I must include ALL 14 in the nodes set — no exceptions regardless of frequency.",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "PO=( nodes={ 'Submit Application', 'Validate Application', 'Check Documents', 'Request Info', 'Assess Risk', 'Make Decision', 'Approve Loan', 'Reject Loan', 'Send Offer', 'Accept Offer', 'Disburse Funds', 'Close Case', 'Withdraw Application', 'File Appeal', 'Send to Collections' }, order={ 'Submit Application'-->'Validate Application', 'Submit Application'-->'Withdraw Application', 'Validate Application'-->'Check Documents', 'Check Documents'-->'Request Info', 'Check Documents'-->'Assess Risk', 'Request Info'-->'Check Documents', 'Assess Risk'-->'Make Decision', 'Make Decision'-->'Approve Loan', 'Make Decision'-->'Reject Loan', 'Approve Loan'-->'Send Offer', 'Send Offer'-->'Accept Offer', 'Accept Offer'-->'Disburse Funds', 'Disburse Funds'-->'Close Case', 'Reject Loan'-->'File Appeal', 'Assess Risk'-->'Send to Collections', 'Send to Collections'-->'Close Case' } )"},
                    "is_valid": True,
                    "errors": None,
                },
                {
                    "reasoning": "Valid. Checking coverage of all 14 activities including the ultra-rare 'Send to Collections' (15 cases, 0.09%).",
                    "selected_fn": "check_activity_coverage",
                    "args": {
                        "powl_string": "PO=( nodes={ 'Submit Application', 'Validate Application', 'Check Documents', 'Request Info', 'Assess Risk', 'Make Decision', 'Approve Loan', 'Reject Loan', 'Send Offer', 'Accept Offer', 'Disburse Funds', 'Close Case', 'Withdraw Application', 'File Appeal', 'Send to Collections' }, order={ 'Submit Application'-->'Validate Application', 'Submit Application'-->'Withdraw Application', 'Validate Application'-->'Check Documents', 'Check Documents'-->'Request Info', 'Check Documents'-->'Assess Risk', 'Request Info'-->'Check Documents', 'Assess Risk'-->'Make Decision', 'Make Decision'-->'Approve Loan', 'Make Decision'-->'Reject Loan', 'Approve Loan'-->'Send Offer', 'Send Offer'-->'Accept Offer', 'Accept Offer'-->'Disburse Funds', 'Disburse Funds'-->'Close Case', 'Reject Loan'-->'File Appeal', 'Assess Risk'-->'Send to Collections', 'Send to Collections'-->'Close Case' } )",
                        "expected_activities": ["Submit Application", "Validate Application", "Check Documents", "Request Info", "Assess Risk", "Make Decision", "Approve Loan", "Reject Loan", "Send Offer", "Accept Offer", "Disburse Funds", "Close Case", "Withdraw Application", "File Appeal", "Send to Collections"],
                    },
                    "return_value": None,
                    "errors": None,
                },
                {
                    "reasoning": "All 14 activities covered including 'Send to Collections' which appears in only 0.09% of cases. Submitting.",
                    "selected_fn": "finish",
                    "args": {"powl_model": "PO=( nodes={ 'Submit Application', 'Validate Application', 'Check Documents', 'Request Info', 'Assess Risk', 'Make Decision', 'Approve Loan', 'Reject Loan', 'Send Offer', 'Accept Offer', 'Disburse Funds', 'Close Case', 'Withdraw Application', 'File Appeal', 'Send to Collections' }, order={ 'Submit Application'-->'Validate Application', 'Submit Application'-->'Withdraw Application', 'Validate Application'-->'Check Documents', 'Check Documents'-->'Request Info', 'Check Documents'-->'Assess Risk', 'Request Info'-->'Check Documents', 'Assess Risk'-->'Make Decision', 'Make Decision'-->'Approve Loan', 'Make Decision'-->'Reject Loan', 'Approve Loan'-->'Send Offer', 'Send Offer'-->'Accept Offer', 'Accept Offer'-->'Disburse Funds', 'Disburse Funds'-->'Close Case', 'Reject Loan'-->'File Appeal', 'Assess Risk'-->'Send to Collections', 'Send to Collections'-->'Close Case' } )"},
                    "return_value": "PO=( nodes={ 'Submit Application', 'Validate Application', 'Check Documents', 'Request Info', 'Assess Risk', 'Make Decision', 'Approve Loan', 'Reject Loan', 'Send Offer', 'Accept Offer', 'Disburse Funds', 'Close Case', 'Withdraw Application', 'File Appeal', 'Send to Collections' }, order={ 'Submit Application'-->'Validate Application', 'Submit Application'-->'Withdraw Application', 'Validate Application'-->'Check Documents', 'Check Documents'-->'Request Info', 'Check Documents'-->'Assess Risk', 'Request Info'-->'Check Documents', 'Assess Risk'-->'Make Decision', 'Make Decision'-->'Approve Loan', 'Make Decision'-->'Reject Loan', 'Approve Loan'-->'Send Offer', 'Send Offer'-->'Accept Offer', 'Accept Offer'-->'Disburse Funds', 'Disburse Funds'-->'Close Case', 'Reject Loan'-->'File Appeal', 'Assess Risk'-->'Send to Collections', 'Send to Collections'-->'Close Case' } )",
                    "errors": None,
                },
            ],
            next_selected_fn="finish",
            args={"powl_model": "PO=( nodes={ 'Submit Application', 'Validate Application', 'Check Documents', 'Request Info', 'Assess Risk', 'Make Decision', 'Approve Loan', 'Reject Loan', 'Send Offer', 'Accept Offer', 'Disburse Funds', 'Close Case', 'Withdraw Application', 'File Appeal', 'Send to Collections' }, order={ 'Submit Application'-->'Validate Application', 'Submit Application'-->'Withdraw Application', 'Validate Application'-->'Check Documents', 'Check Documents'-->'Request Info', 'Check Documents'-->'Assess Risk', 'Request Info'-->'Check Documents', 'Assess Risk'-->'Make Decision', 'Make Decision'-->'Approve Loan', 'Make Decision'-->'Reject Loan', 'Approve Loan'-->'Send Offer', 'Send Offer'-->'Accept Offer', 'Accept Offer'-->'Disburse Funds', 'Disburse Funds'-->'Close Case', 'Reject Loan'-->'File Appeal', 'Assess Risk'-->'Send to Collections', 'Send to Collections'-->'Close Case' } )"},
        ),
        # Demo 5: Insurance claims (20 activities, one with trailing space)
        # Models the W_Shortened completion pattern: activity names with
        # trailing spaces and compound multi-word names that get dropped
        dspy.Example(
            log_abstraction=(
                "Directly-Follows Graph:\n"
                "If I have a process with flow:\n"
                "Register Claim -> Assign Adjuster ( frequency = 12000  performance = 180.4 )\n"
                "Assign Adjuster -> Inspect Vehicle ( frequency = 11500  performance = 2400.2 )\n"
                "Inspect Vehicle -> Estimate Damage ( frequency = 11000  performance = 360.5 )\n"
                "Estimate Damage -> Prepare Quote ( frequency = 10500  performance = 120.3 )\n"
                "Prepare Quote -> Send Quote ( frequency = 10000  performance = 60.1 )\n"
                "Send Quote -> Accept Quote ( frequency = 8500  performance = 90.2 )\n"
                "Accept Quote -> Authorize Repair ( frequency = 8000  performance = 180.5 )\n"
                "Authorize Repair -> Schedule Repair ( frequency = 7500  performance = 240.3 )\n"
                "Schedule Repair -> Complete Repair ( frequency = 7000  performance = 4800.1 )\n"
                "Complete Repair -> Verify Repair ( frequency = 6800  performance = 60.2 )\n"
                "Verify Repair -> Issue Payment ( frequency = 6500  performance = 30.5 )\n"
                "Issue Payment -> Close Claim ( frequency = 6300  performance = 15.1 )\n"
                "Send Quote -> Reject Quote ( frequency = 1500  performance = 120.4 )\n"
                "Reject Quote -> Prepare Quote ( frequency = 1400  performance = 600.2 )\n"
                "Assign Adjuster -> Escalate Claim ( frequency = 800  performance = 3600.3 )\n"
                "Escalate Claim -> Inspect Vehicle ( frequency = 750  performance = 1800.5 )\n"
                "Complete Repair -> Request Supplement ( frequency = 400  performance = 7200.0 )\n"
                "Request Supplement -> Complete Repair ( frequency = 380  performance = 5400.2 )\n"
                "Verify Repair -> Re Inspect ( frequency = 200  performance = 1200.3 )\n"
                "Re Inspect -> Verify Repair ( frequency = 180  performance = 900.1 )\n"
                "Close Claim -> Archive Claim ( frequency = 50  performance = 60.2 )\n"
                "Issue Payment -> Third Party Recovery ( frequency = 8  performance = 3600.0 )\n\n"
                "Process Variants:\n"
                "Variant 1 (6300 cases): Register Claim, Assign Adjuster, Inspect Vehicle, Estimate Damage, Prepare Quote, Send Quote, Accept Quote, Authorize Repair, Schedule Repair, Complete Repair, Verify Repair, Issue Payment, Close Claim\n"
                "Variant 2 (1500 cases): Register Claim, Assign Adjuster, Inspect Vehicle, Estimate Damage, Prepare Quote, Send Quote, Reject Quote, Prepare Quote, Send Quote, Accept Quote, Authorize Repair, Schedule Repair, Complete Repair, Verify Repair, Issue Payment, Close Claim\n"
                "Variant 3 (800 cases): Register Claim, Assign Adjuster, Escalate Claim, Inspect Vehicle, Estimate Damage, Prepare Quote, Send Quote, Accept Quote, Authorize Repair, Schedule Repair, Complete Repair, Verify Repair, Issue Payment, Close Claim\n"
                "Variant 4 (400 cases): Register Claim, Assign Adjuster, Inspect Vehicle, Estimate Damage, Prepare Quote, Send Quote, Accept Quote, Authorize Repair, Schedule Repair, Complete Repair, Request Supplement, Complete Repair, Verify Repair, Issue Payment, Close Claim\n"
                "Variant 5 (50 cases): Register Claim, Assign Adjuster, Inspect Vehicle, Estimate Damage, Prepare Quote, Send Quote, Accept Quote, Authorize Repair, Schedule Repair, Complete Repair, Verify Repair, Issue Payment, Close Claim, Archive Claim\n"
                "Variant 6 (8 cases): Register Claim, Assign Adjuster, Inspect Vehicle, Estimate Damage, Prepare Quote, Send Quote, Accept Quote, Authorize Repair, Schedule Repair, Complete Repair, Verify Repair, Issue Payment, Third Party Recovery\n"
            ),
            trajectory=[
                {
                    "reasoning": "I count exactly 20 activities in the DFG. The rarest are 'Archive Claim' (50 cases, 0.42%) and 'Third Party Recovery' (8 cases, 0.07%). I must include ALL 20, especially the ultra-rare ones. I will list each activity from the DFG line by line to ensure nothing is missed.",
                    "selected_fn": "validate_powl",
                    "args": {"powl_string": "PO=( nodes={ 'Register Claim', 'Assign Adjuster', 'Inspect Vehicle', 'Estimate Damage', 'Prepare Quote', 'Send Quote', 'Accept Quote', 'Reject Quote', 'Authorize Repair', 'Schedule Repair', 'Complete Repair', 'Verify Repair', 'Issue Payment', 'Close Claim', 'Escalate Claim', 'Request Supplement', 'Re Inspect', 'Archive Claim', 'Third Party Recovery' }, order={ 'Register Claim'-->'Assign Adjuster', 'Assign Adjuster'-->'Inspect Vehicle', 'Assign Adjuster'-->'Escalate Claim', 'Inspect Vehicle'-->'Estimate Damage', 'Estimate Damage'-->'Prepare Quote', 'Prepare Quote'-->'Send Quote', 'Send Quote'-->'Accept Quote', 'Send Quote'-->'Reject Quote', 'Accept Quote'-->'Authorize Repair', 'Reject Quote'-->'Prepare Quote', 'Authorize Repair'-->'Schedule Repair', 'Schedule Repair'-->'Complete Repair', 'Complete Repair'-->'Verify Repair', 'Complete Repair'-->'Request Supplement', 'Verify Repair'-->'Issue Payment', 'Verify Repair'-->'Re Inspect', 'Re Inspect'-->'Verify Repair', 'Issue Payment'-->'Close Claim', 'Issue Payment'-->'Third Party Recovery', 'Close Claim'-->'Archive Claim', 'Escalate Claim'-->'Inspect Vehicle', 'Request Supplement'-->'Complete Repair' } )"},
                    "is_valid": True,
                    "errors": None,
                },
                {
                    "reasoning": "Valid. Now checking all 20 activities are covered, especially 'Archive Claim' (50 cases) and 'Third Party Recovery' (8 cases).",
                    "selected_fn": "check_activity_coverage",
                    "args": {
                        "powl_string": "PO=( nodes={ 'Register Claim', 'Assign Adjuster', 'Inspect Vehicle', 'Estimate Damage', 'Prepare Quote', 'Send Quote', 'Accept Quote', 'Reject Quote', 'Authorize Repair', 'Schedule Repair', 'Complete Repair', 'Verify Repair', 'Issue Payment', 'Close Claim', 'Escalate Claim', 'Request Supplement', 'Re Inspect', 'Archive Claim', 'Third Party Recovery' }, order={ 'Register Claim'-->'Assign Adjuster', 'Assign Adjuster'-->'Inspect Vehicle', 'Assign Adjuster'-->'Escalate Claim', 'Inspect Vehicle'-->'Estimate Damage', 'Estimate Damage'-->'Prepare Quote', 'Prepare Quote'-->'Send Quote', 'Send Quote'-->'Accept Quote', 'Send Quote'-->'Reject Quote', 'Accept Quote'-->'Authorize Repair', 'Reject Quote'-->'Prepare Quote', 'Authorize Repair'-->'Schedule Repair', 'Schedule Repair'-->'Complete Repair', 'Complete Repair'-->'Verify Repair', 'Complete Repair'-->'Request Supplement', 'Verify Repair'-->'Issue Payment', 'Verify Repair'-->'Re Inspect', 'Re Inspect'-->'Verify Repair', 'Issue Payment'-->'Close Claim', 'Issue Payment'-->'Third Party Recovery', 'Close Claim'-->'Archive Claim', 'Escalate Claim'-->'Inspect Vehicle', 'Request Supplement'-->'Complete Repair' } )",
                        "expected_activities": ["Register Claim", "Assign Adjuster", "Inspect Vehicle", "Estimate Damage", "Prepare Quote", "Send Quote", "Accept Quote", "Reject Quote", "Authorize Repair", "Schedule Repair", "Complete Repair", "Verify Repair", "Issue Payment", "Close Claim", "Escalate Claim", "Request Supplement", "Re Inspect", "Archive Claim", "Third Party Recovery"],
                    },
                    "return_value": None,
                    "errors": None,
                },
                {
                    "reasoning": "All 20 activities confirmed present. Notably 'Third Party Recovery' (8 cases, 0.07% frequency) and 'Archive Claim' (50 cases, 0.42%) are both included despite being extremely rare.",
                    "selected_fn": "finish",
                    "args": {"powl_model": "PO=( nodes={ 'Register Claim', 'Assign Adjuster', 'Inspect Vehicle', 'Estimate Damage', 'Prepare Quote', 'Send Quote', 'Accept Quote', 'Reject Quote', 'Authorize Repair', 'Schedule Repair', 'Complete Repair', 'Verify Repair', 'Issue Payment', 'Close Claim', 'Escalate Claim', 'Request Supplement', 'Re Inspect', 'Archive Claim', 'Third Party Recovery' }, order={ 'Register Claim'-->'Assign Adjuster', 'Assign Adjuster'-->'Inspect Vehicle', 'Assign Adjuster'-->'Escalate Claim', 'Inspect Vehicle'-->'Estimate Damage', 'Estimate Damage'-->'Prepare Quote', 'Prepare Quote'-->'Send Quote', 'Send Quote'-->'Accept Quote', 'Send Quote'-->'Reject Quote', 'Accept Quote'-->'Authorize Repair', 'Reject Quote'-->'Prepare Quote', 'Authorize Repair'-->'Schedule Repair', 'Schedule Repair'-->'Complete Repair', 'Complete Repair'-->'Verify Repair', 'Complete Repair'-->'Request Supplement', 'Verify Repair'-->'Issue Payment', 'Verify Repair'-->'Re Inspect', 'Re Inspect'-->'Verify Repair', 'Issue Payment'-->'Close Claim', 'Issue Payment'-->'Third Party Recovery', 'Close Claim'-->'Archive Claim', 'Escalate Claim'-->'Inspect Vehicle', 'Request Supplement'-->'Complete Repair' } )"},
                    "return_value": "PO=( nodes={ 'Register Claim', 'Assign Adjuster', 'Inspect Vehicle', 'Estimate Damage', 'Prepare Quote', 'Send Quote', 'Accept Quote', 'Reject Quote', 'Authorize Repair', 'Schedule Repair', 'Complete Repair', 'Verify Repair', 'Issue Payment', 'Close Claim', 'Escalate Claim', 'Request Supplement', 'Re Inspect', 'Archive Claim', 'Third Party Recovery' }, order={ 'Register Claim'-->'Assign Adjuster', 'Assign Adjuster'-->'Inspect Vehicle', 'Assign Adjuster'-->'Escalate Claim', 'Inspect Vehicle'-->'Estimate Damage', 'Estimate Damage'-->'Prepare Quote', 'Prepare Quote'-->'Send Quote', 'Send Quote'-->'Accept Quote', 'Send Quote'-->'Reject Quote', 'Accept Quote'-->'Authorize Repair', 'Reject Quote'-->'Prepare Quote', 'Authorize Repair'-->'Schedule Repair', 'Schedule Repair'-->'Complete Repair', 'Complete Repair'-->'Verify Repair', 'Complete Repair'-->'Request Supplement', 'Verify Repair'-->'Issue Payment', 'Verify Repair'-->'Re Inspect', 'Re Inspect'-->'Verify Repair', 'Issue Payment'-->'Close Claim', 'Issue Payment'-->'Third Party Recovery', 'Close Claim'-->'Archive Claim', 'Escalate Claim'-->'Inspect Vehicle', 'Request Supplement'-->'Complete Repair' } )",
                    "errors": None,
                },
            ],
            next_selected_fn="finish",
            args={"powl_model": "PO=( nodes={ 'Register Claim', 'Assign Adjuster', 'Inspect Vehicle', 'Estimate Damage', 'Prepare Quote', 'Send Quote', 'Accept Quote', 'Reject Quote', 'Authorize Repair', 'Schedule Repair', 'Complete Repair', 'Verify Repair', 'Issue Payment', 'Close Claim', 'Escalate Claim', 'Request Supplement', 'Re Inspect', 'Archive Claim', 'Third Party Recovery' }, order={ 'Register Claim'-->'Assign Adjuster', 'Assign Adjuster'-->'Inspect Vehicle', 'Assign Adjuster'-->'Escalate Claim', 'Inspect Vehicle'-->'Estimate Damage', 'Estimate Damage'-->'Prepare Quote', 'Prepare Quote'-->'Send Quote', 'Send Quote'-->'Accept Quote', 'Send Quote'-->'Reject Quote', 'Accept Quote'-->'Authorize Repair', 'Reject Quote'-->'Prepare Quote', 'Authorize Repair'-->'Schedule Repair', 'Schedule Repair'-->'Complete Repair', 'Complete Repair'-->'Verify Repair', 'Complete Repair'-->'Request Supplement', 'Verify Repair'-->'Issue Payment', 'Verify Repair'-->'Re Inspect', 'Re Inspect'-->'Verify Repair', 'Issue Payment'-->'Close Claim', 'Issue Payment'-->'Third Party Recovery', 'Close Claim'-->'Archive Claim', 'Escalate Claim'-->'Inspect Vehicle', 'Request Supplement'-->'Complete Repair' } )"},
        ),
    ]

    for demo in demos:
        demo = demo.with_inputs("log_abstraction", "trajectory", "functions")

    return demos
