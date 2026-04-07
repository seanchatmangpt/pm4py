'''
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions GmbH

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


class NaturalLanguageToPOWL(dspy.Module):
    """Generate a POWL model from a natural language process description.

    This module takes a free-text description of a business process and
    produces a valid POWL model string. Unlike the event-log-driven agent,
    this works from human descriptions, interviews, SOPs, etc.

    Available tools:
    - validate_powl(powl_string): Check if the POWL string parses correctly
    - finish(powl_model): Return the final POWL model
    """

    def __init__(self, max_steps=6, demos=None):
        self.max_steps = max_steps
        instructions = (
            "You are a process modeler. Given a natural language description "
            "of a business process, generate a POWL (Partially Ordered Workflow Language) model.\n\n"
            "POWL syntax (STRICT — no other syntax allowed):\n"
            "- Visible transition: 'label' (single-quoted string)\n"
            "- Silent transition: tau\n"
            "- XOR choice: X( 'A', 'B' )\n"
            "- LOOP: *( 'do_part', 'redo_part' )\n"
            "- Partial Order: PO=( nodes={ 'A', 'B', 'C' }, order={ 'A'-->'B', 'A'-->'C' } )\n"
            "- Nesting: operators can contain other operators or transitions\n"
            "- NO arrow (->) notation. NO sequence (seq) notation. Only X(), *(), PO=().\n"
            "- Activity names in nodes={} MUST be single-quoted: 'Activity Name'.\n\n"
            "CRITICAL — Choosing between X(), *(), and PO=():\n"
            "- X() = EXCLUSIVE choice: exactly ONE branch executes (if/else, either/or).\n"
            "  Use when the description says 'if X then A otherwise B' or 'either A or B'.\n"
            "  In a PO=(), if a node has multiple successors, ALL successors MUST execute.\n"
            "  So if only one should execute, use X() NOT multiple outgoing edges in PO.\n"
            "- *() = LOOP: the redo part can repeat. Use for retry/rework/repeat patterns.\n"
            "- PO=() = PARTIAL ORDER: ALL activities in the node set execute. The order "
            "  field specifies precedence constraints (A must complete before B starts).\n"
            "  If two activities have no ordering constraint, they can run concurrently.\n"
            "  IMPORTANT: In a PO, every node with outgoing edges means ALL successors "
            "  must eventually complete. If you need mutual exclusion, use X().\n\n"
            "STRUCTURAL SOUNDNESS (mandatory):\n"
            "- Every execution path must reach a terminal state (no dead ends).\n"
            "- No deadlocks: if two activities are in an XOR, both branches must "
            "  eventually lead to completion.\n"
            "- In a PO, if activity A has edges to both B and C, then both B and C "
            "  must complete before the process can proceed past A.\n\n"
            "GUIDELINES:\n"
            "1. Extract every distinct activity mentioned in the description.\n"
            "2. Infer control flow from temporal words (then, after, before, when), "
            "conditional words (if, otherwise, alternatively, or), and loop words (repeat, "
            "redo, retry, loop, again).\n"
            "3. Activity names should be concise verb phrases matching the description.\n"
            "4. Nest X() inside PO nodes when a step involves a choice.\n"
            "5. Every branch of every X() must eventually lead to a terminal activity.\n\n"
            "MANDATORY workflow:\n"
            "1. Generate a POWL model from the description.\n"
            "2. Call validate_powl(powl_string=...) — must return is_valid=true.\n"
            "3. If invalid, fix the syntax and re-validate.\n"
            "4. Call finish(powl_model=...) after validation passes.\n"
        )
        signature = dspy.Signature(
            'process_description, trajectory, functions -> next_selected_fn, args: dict[str, Any]',
            instructions=instructions,
        )
        self.react = dspy.ChainOfThought(signature)
        if demos:
            self.react.predict.demos = demos

    def forward(self, process_description, functions):
        from pm4py.algo.dspy.powl.generation import fn_metadata, wrap_function_with_timeout, validate_powl

        tools = {
            fn_name: fn_metadata(fn)
            for fn_name, fn in functions.items()
        }

        trajectory = []
        last_output = None
        last_valid_powl = None

        for _ in range(self.max_steps):
            pred = self.react(
                process_description=process_description,
                trajectory=trajectory,
                functions=tools,
            )
            selected_fn = getattr(pred, "next_selected_fn", None)
            if not selected_fn:
                break
            selected_fn = selected_fn.strip('"').strip("'")
            if selected_fn not in functions:
                trajectory.append(dict(
                    reasoning=getattr(pred, "reasoning", ""),
                    selected_fn=selected_fn,
                    args={},
                    return_value=None,
                    errors=f"Unknown function: {selected_fn}",
                ))
                continue

            args = getattr(pred, "args", {}) or {}
            fn_output = wrap_function_with_timeout(functions[selected_fn])(**args)
            trajectory.append(dict(
                reasoning=getattr(pred, "reasoning", ""),
                selected_fn=selected_fn,
                args=args,
                **fn_output,
            ))
            last_output = fn_output

            # Track the last validated POWL as fallback
            if selected_fn == "validate_powl" and fn_output.get("is_valid"):
                powl_arg = args.get("powl_string", "")
                if powl_arg:
                    last_valid_powl = powl_arg

            if selected_fn == "finish":
                break

        answer = last_output.get("return_value", "") if last_output else ""
        if isinstance(answer, dict):
            answer = answer.get("powl_model", str(answer))

        # Fallback: if finish wasn't called, use last validated POWL from trajectory
        if not answer and last_valid_powl:
            answer = last_valid_powl

        return dspy.Prediction(answer=answer, trajectory=trajectory)


def generate_powl_from_text(
    process_description: str,
    model: str = "groq/openai/gpt-oss-20b",
    api_key=None,
    api_base=None,
    max_refinements: int = 2,
    use_demos: bool = True,
) -> dict:
    """Generate a POWL model from a natural language description.

    Generates a POWL, validates it syntactically, then optionally runs
    the Dr. van der Aalst judge for structural soundness. If the judge
    rejects it, re-generates with the judge's feedback.

    Parameters
    ----------
    process_description : str
        Natural language description of a business process.
    model : str
        LLM model identifier (litellm format).
    api_key : str, optional
        API key. If None, reads from provider env vars.
    api_base : str, optional
        Custom API base URL.
    max_refinements : int
        Max judge-and-refine iterations (0 = skip judging).
    use_demos : bool
        Whether to use built-in few-shot examples.

    Returns
    -------
    dict
        With 'powl' (str), 'verdict' (bool), 'reasoning' (str),
        'refinements' (int).
    """
    from pm4py.algo.dspy.powl.optimize import configure_lm
    from pm4py.algo.dspy.powl.generation import validate_powl, finish
    from pm4py.algo.dspy.powl.judge import judge_powl
    from pm4py.algo.dspy.powl.powl_analysis import analyze_powl

    configure_lm(model=model, api_key=api_key, api_base=api_base)

    demos = None
    if use_demos:
        from pm4py.algo.dspy.powl.nl_demos import get_nl_few_shot_demos
        demos = get_nl_few_shot_demos()

    agent = NaturalLanguageToPOWL(demos=demos)
    functions = {
        "validate_powl": validate_powl,
        "finish": finish,
        "analyze_powl": analyze_powl  # Allow agent to proactively analyze its POWL
    }

    current_description = process_description
    refinements = 0

    for attempt in range(max_refinements + 1):
        pred = agent(process_description=current_description, functions=functions)
        powl_result = pred.answer

        # Always validate syntax first
        v = validate_powl(powl_result)
        if not v.get("is_valid"):
            if attempt < max_refinements:
                # Format syntax errors to match the demo pattern (see Demo 1 in nl_demos.py)
                errors = v.get("errors", "")
                current_description = (
                    process_description + "\n\n"
                    f"PREVIOUS ATTEMPT FAILED SYNTAX VALIDATION.\n"
                    f"Parse error: {errors}\n"
                    "REMEMBER these syntax rules:\n"
                    "- Visible transitions: 'label' (single-quoted)\n"
                    "- XOR choice: X( 'A', 'B' )\n"
                    "- LOOP: *( 'do_part', 'redo_part' )\n"
                    "- Partial Order: PO=( nodes={...}, order={...} )\n"
                    "- NO arrow (->) notation, NO seq notation\n"
                    "- Operators cannot be edge endpoints in PO order\n"
                    "Fix the syntax and try again."
                )
                refinements += 1
                continue
            return {
                "powl": powl_result,
                "verdict": False,
                "reasoning": f"Syntax error: {v['errors']}",
                "refinements": refinements,
            }

        # ALWAYS run judge once for feedback (autofail once pattern)
        # First run: always get feedback even if max_refinements=0
        is_first_run = (attempt == 0)
        should_judge = is_first_run or (max_refinements > 0)

        if should_judge:
            judge_result = judge_powl(
                powl_string=powl_result,
                context_description=process_description,
                use_real_analysis=True,
            )

            # Judge approved
            if judge_result["verdict"]:
                # For correct POWLs, provide constructive feedback
                feedback = _get_constructive_feedback(powl_result, judge_result)

                result = {
                    "powl": powl_result,
                    "verdict": True,
                    "reasoning": judge_result["reasoning"],
                    "feedback": feedback,
                    "analysis": judge_result.get("analysis"),
                    "refinements": refinements,
                }

                # If this is the first run and max_refinements=0, return with feedback
                # If we have more attempts and the judge approved, return success
                if not max_refinements or is_first_run:
                    return result

            # Judge rejected — refine (only if we have more attempts)
            if attempt < max_refinements:
                reasoning = judge_result.get("reasoning", "")
                current_description = (
                    process_description + "\n\n"
                    f"PREVIOUS ATTEMPT REJECTED by process model quality review.\n"
                    f"Issues: {reasoning}\n"
                    "CRITICAL — You must fix these structural issues:\n"
                    "1. Every execution path MUST reach a terminal state (no dead ends)\n"
                    "2. Every node with outgoing edges must connect to valid successors\n"
                    "3. XOR branches must ALL lead to completion (no orphans)\n"
                    "4. Loops must have escape conditions (no infinite loops)\n"
                    "Generate an improved POWL addressing these specific issues."
                )
                refinements += 1
                continue

            # No more attempts, return with judge's rejection
            return {
                "powl": powl_result,
                "verdict": False,
                "reasoning": judge_result["reasoning"],
                "analysis": judge_result.get("analysis"),
                "refinements": refinements,
            }

        # No judging requested and not first run (shouldn't happen with autofail once)
        return {
            "powl": powl_result,
            "verdict": None,
            "reasoning": "",
            "refinements": refinements,
        }


def _get_constructive_feedback(powl_string: str, judge_result: dict) -> str:
    """Generate constructive feedback even for correct POWLs.

    Parameters
    ----------
    powl_string : str
        The POWL model string.
    judge_result : dict
        The judge's result including analysis.

    Returns
    -------
    str
        Constructive feedback suggestions.
    """
    analysis = judge_result.get("analysis", {})
    if not analysis:
        return "Model is structurally sound."

    suggestions = []

    # Check metrics for improvement suggestions
    metrics = analysis.get("metrics", {})

    # Suggest simplification if deeply nested
    if metrics.get("nesting_depth", 0) > 4:
        suggestions.append("Consider flattening deeply nested structures for better readability")

    # Suggest parallel extraction if sequential-heavy
    if metrics.get("sequential_ratio", 0) > 0.8:
        suggestions.append("Consider extracting concurrent activities to partial orders")

    # Suggest activity naming improvements
    if metrics.get("has_generic_names", False):
        suggestions.append("Use more descriptive activity names (avoid 'A', 'B', 'Task', etc.)")

    # Check structure for suggestions
    structure = analysis.get("structure", {})

    # Check if conversion failed
    conversion = analysis.get("conversion", {})
    if not conversion.get("petri_net_success"):
        suggestions.append("Petri net conversion failed — model may have non-block-structured elements")
    if not conversion.get("bpmn_success"):
        suggestions.append("BPMN conversion failed — some structures may not map cleanly")

    # Check for issues that don't cause rejection
    issues = analysis.get("issues", [])
    non_critical_issues = [i for i in issues if "orphan" not in i.lower() and "deadlock" not in i.lower()]
    if non_critical_issues:
        suggestions.append(f"Minor issues: {', '.join(non_critical_issues[:2])}")

    if not suggestions:
        return "Model is well-structured and sound."

    return "Suggestions for improvement: " + "; ".join(suggestions)
