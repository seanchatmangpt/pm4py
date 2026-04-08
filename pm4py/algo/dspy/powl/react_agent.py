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



import json
import dspy


class POWLAgent(dspy.Module):
    """ReAct-style agent that generates POWL models from event log abstractions.

    The agent receives a textual abstraction of an event log (DFG + variants)
    and iteratively builds a POWL model by calling validation tools.

    Available tools:
    - validate_powl(powl_string): Check if the POWL string parses correctly
    - check_activity_coverage(powl_string, expected_activities): Check label coverage
    - check_fitness(powl_string, log_obj): Replay fitness (if log provided)
    - finish(powl_model): Return the final POWL model

    The trajectory tracks each reasoning step, tool call, and result.
    """

    def __init__(self, max_steps=10, expected_activities=None, demos=None):
        self.max_steps = max_steps
        self.expected_activities = expected_activities
        instructions = (
            "You are a process discovery agent. Given an event log abstraction, "
            "generate a POWL (Partially Ordered Workflow Language) model.\n\n"
            "POWL syntax (STRICT — no other syntax allowed):\n"
            "- Visible transition: 'label' (single-quoted string)\n"
            "- Silent transition: tau\n"
            "- XOR choice: X( 'A', 'B' )\n"
            "- LOOP: *( 'do_part', 'redo_part' )\n"
            "- Partial Order: PO=( nodes={ 'A', 'B', 'C' }, order={ 'A'-->'B', 'A'-->'C' } )\n"
            "- Nesting: operators can contain other operators or transitions\n"
            "- NO arrow (->) notation. NO sequence (seq) notation. Only X(), *(), PO=().\n"
            "- Activity names in nodes={} MUST be single-quoted: 'Activity Name'.\n\n"
            "MANDATORY workflow (follow in order, do NOT skip steps):\n"
            "1. Generate a POWL model covering ALL activities from the DFG.\n"
            "2. Call validate_powl(powl_string=...) — must return is_valid=true.\n"
            "3. Call check_activity_coverage(powl_string=..., expected_activities=[...]) — must return no errors.\n"
            "4. If coverage has missing activities, regenerate the model adding ALL missing activities, then go to step 2.\n"
            "5. ONLY call finish(powl_model=...) after BOTH validate_powl AND check_activity_coverage pass.\n\n"
            "Key rules:\n"
            "- Every activity label from the DFG MUST appear in the nodes set.\n"
            "- Copy activity names EXACTLY as they appear in the DFG (including spaces, colons, parentheses).\n"
            "- For large logs (>10 activities), use PO=( nodes={...}, order={...} ) with ALL activities in nodes.\n"
            "- For the order field, use 'A'-->'B' syntax matching the DFG edges exactly.\n"
            "- Do NOT abbreviate or omit low-frequency activities.\n"
            "- Rare activities (appearing in few cases) are often the MOST important for process discovery — never omit them.\n"
            "- Count every activity from the DFG before generating. Your nodes set must have exactly the same count."
        )
        signature = dspy.Signature(
            'log_abstraction, trajectory, functions -> next_selected_fn, args: dict[str, Any]',
            instructions=instructions,
        )
        self.react = dspy.ChainOfThought(signature)
        if demos:
            self.react.predict.demos = demos

    def forward(self, log_abstraction, functions):
        from pm4py.algo.dspy.powl.generation import fn_metadata, wrap_function_with_timeout, validate_powl, check_activity_coverage

        tools = {
            fn_name: fn_metadata(fn)
            for fn_name, fn in functions.items()
        }

        trajectory = []
        last_output = None

        for _ in range(self.max_steps):
            pred = self.react(
                log_abstraction=log_abstraction,
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

            if selected_fn == "finish":
                break

        answer = last_output.get("return_value", "") if last_output else ""
        # Guard: if the LLM returned a dict instead of a string, extract the value
        if isinstance(answer, dict):
            answer = answer.get("powl_model", str(answer))

        # Post-hoc coverage retry: if valid but missing activities, re-prompt once
        if answer and self.expected_activities:
            v_result = validate_powl(answer)
            if v_result.get("is_valid"):
                c_result = check_activity_coverage(answer, self.expected_activities)
                if c_result.get("errors"):
                    missing = c_result["return_value"]
                    retry_abstraction = (
                        log_abstraction + "\n\n"
                        f"CRITICAL: Your previous POWL model was VALID but is MISSING these activities: {missing}. "
                        "You MUST include ALL of them in the nodes set. Do NOT call finish until coverage is 100%."
                    )
                    trajectory = []
                    for _ in range(self.max_steps):
                        pred = self.react(
                            log_abstraction=retry_abstraction,
                            trajectory=trajectory,
                            functions=tools,
                        )
                        selected_fn = getattr(pred, "next_selected_fn", None)
                        if not selected_fn:
                            break
                        selected_fn = selected_fn.strip('"').strip("'")
                        if selected_fn not in functions:
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
                        if selected_fn == "finish":
                            break
                    answer = last_output.get("return_value", "") if last_output else ""

        return dspy.Prediction(answer=answer, trajectory=trajectory)

    def save(self, path: str):
        """Save the optimized agent to disk.

        Saves the SIMBA-optimized prompts/instructions so they can be
        loaded later without re-running optimization.

        Parameters
        ----------
        path : str
            File path to save the agent state (JSON).
        """
        state = {
            "max_steps": self.max_steps,
            "expected_activities": self.expected_activities,
            "react_signature": str(self.react.signature),
        }
        # Extract the optimized demos/prompt if SIMBA was used
        if hasattr(self.react, "demos") and self.react.demos:
            state["demos"] = [
                {k: str(v) for k, v in d.items()}
                for d in self.react.demos
            ]
        # Save the updated signature instructions (SIMBA modifies these)
        if hasattr(self.react, "signature"):
            sig = self.react.signature
            if hasattr(sig, "instructions"):
                state["instructions"] = sig.instructions
        with open(path, "w") as f:
            json.dump(state, f, indent=2)

    @classmethod
    def load(cls, path: str):
        """Load a previously saved agent from disk.

        Parameters
        ----------
        path : str
            File path to load the agent state from.

        Returns
        -------
        POWLAgent
            The loaded agent with optimized prompts.
        """
        with open(path, "r") as f:
            state = json.load(f)

        agent = cls(
            max_steps=state.get("max_steps", 10),
            expected_activities=state.get("expected_activities"),
        )

        # Restore optimized instructions if available
        if "instructions" in state:
            # Rebuild with optimized instructions
            old_sig = agent.react.signature
            agent.react = dspy.ChainOfThought(dspy.Signature(
                'log_abstraction, trajectory, functions -> next_selected_fn, args: dict[str, Any]',
                instructions=state["instructions"],
            ))

        # Restore demos if available (SIMBA few-shot examples)
        if "demos" in state:
            agent.react.demos = state["demos"]

        return agent
