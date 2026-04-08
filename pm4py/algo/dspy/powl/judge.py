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


class POWLJudge(dspy.Module):
    """Dr. Wil van der Aalst's POWL Quality Judge.

    Evaluates whether a POWL model is a good representation of a process,
    using both real pm4py analysis and LLM reasoning.

    Returns True if the POWL is good, False otherwise.
    """

    def __init__(self, use_demos: bool = True, always_run_once: bool = True,
                 use_real_analysis: bool = True):
        """Initialize the judge.

        Parameters
        ----------
        use_demos : bool
            Whether to use few-shot examples for more nuanced judgment.
            Defaults to True.
        always_run_once : bool
            Whether to always provide feedback once, even if the POWL is correct.
            Defaults to True.
        use_real_analysis : bool
            Whether to run real pm4py analysis before LLM reasoning.
            Defaults to True.
        """
        self.use_demos = use_demos
        self.always_run_once = always_run_once
        self.use_real_analysis = use_real_analysis

        signature = dspy.Signature(
            'powl_string, context_description -> reasoning, verdict: bool, analysis: str',
            instructions=(
                "You are Dr. Wil van der Aalst, the father of process mining. "
                "You evaluate POWL (Partially Ordered Workflow Language) models "
                "for quality. You do NOT compare against any specific ground truth "
                "model — you judge whether the given POWL is a good, sound, and "
                "reasonable process model.\n\n"
                "Evaluation criteria:\n"
                "1. SYNTACTIC VALIDITY: Does the POWL string follow correct syntax? "
                "   - Visible transitions: 'label' (single-quoted)\n"
                "   - XOR choice: X( 'A', 'B' )\n"
                "   - LOOP: *( 'do_part', 'redo_part' )\n"
                "   - Partial Order: PO=( nodes={...}, order={...} )\n"
                "   - Nesting: operators can contain other operators\n"
                "   - No bare -> arrows, no seq notation\n\n"
                "2. STRUCTURAL SOUNDNESS (van der Aalst criteria):\n"
                "   - Deadlock freedom: No branch of an XOR leads to a dead end\n"
                "   - Proper completion: Every execution path can reach a terminal state\n"
                "   - No orphaned nodes: Every activity is reachable from the start\n"
                "   - Liveness: No infinite loops without an escape (unless intentional)\n\n"
                "3. BEHAVIORAL PLAUSIBILITY:\n"
                "   - Does the control flow make logical sense for the described process?\n"
                "   - Are choices (XOR) used where mutually exclusive alternatives exist?\n"
                "   - Are loops (*) used for retry/rework patterns?\n"
                "   - Is partial order (PO) used for concurrent/independent activities?\n\n"
                "4. MODELING QUALITY:\n"
                "   - Is the model appropriately abstract (not too flat, not too deep)?\n"
                "   - Does it avoid unnecessary complexity?\n"
                "   - Are activity names meaningful and consistent?\n"
                "   - Does nesting capture real process structure?\n\n"
                "The 'analysis' parameter contains REAL structural analysis results from pm4py. "
                "USE THIS DATA to inform your judgment. Reference specific metrics, "
                "detected issues, and conversion results in your reasoning.\n\n"
                "context_description is an optional natural language description of "
                "what the process should model. Use it to judge behavioral plausibility.\n"
                "If no context is provided, judge purely on structural soundness.\n\n"
                "Return verdict=True only if the POWL is syntactically valid, "
                "structurally sound, and behaviorally plausible. "
                "Return verdict=False if ANY criterion fails.\n\n"
                "When providing reasoning for a False verdict, be SPECIFIC about "
                "what is wrong and how to fix it. Reference the exact nodes or "
                "operators that are problematic. Explain which structural property "
                "is violated (deadlock, liveness, orphaned node, semantic mismatch).\n\n"
                "When providing reasoning for a True verdict, include CONSTRUCTIVE FEEDBACK: "
                "suggestions for improvement even if the model is sound. Reference the "
                "analysis results to provide specific, actionable suggestions."
            ),
        )
        self.judge = dspy.ChainOfThought(signature)

    def load_demos(self):
        """Load few-shot examples for more nuanced judgment."""
        from pm4py.algo.dspy.powl.judge_demos import get_judge_few_shot_demos
        demos = get_judge_few_shot_demos()
        self.judge.predict.demos = demos

    def _run_real_analysis(self, powl_string: str) -> dict:
        """Run pm4py analysis functions and return structured results.

        Returns dict with 'return_value' (AnalysisResult) and 'errors'.
        """
        from pm4py.algo.dspy.powl.powl_analysis import analyze_powl_comprehensive
        return analyze_powl_comprehensive(powl_string, include_visualization=False)

    def _format_analysis_for_llm(self, analysis_result: dict) -> str:
        """Format analysis results for inclusion in LLM prompt.

        Parameters
        ----------
        analysis_result : dict
            The return value from analyze_powl_comprehensive.

        Returns
        -------
        str
            Formatted analysis summary for LLM context.
        """
        if not analysis_result or not analysis_result.get("is_valid"):
            return "ANALYSIS: POWL parsing or validation failed."

        lines = ["STRUCTURAL ANALYSIS RESULTS:"]

        # Metrics
        metrics = analysis_result.get("metrics", {})
        lines.append(f"- Nodes: {metrics.get('node_count', 0)}")
        lines.append(f"- Activities: {metrics.get('activity_count', 0)}")
        lines.append(f"- Nesting depth: {metrics.get('nesting_depth', 0)}")
        lines.append(f"- Operators: {metrics.get('operator_counts', {})}")

        # Structure
        structure = analysis_result.get("structure", {})
        if structure.get("has_dead_ends"):
            lines.append(f"- DEAD-ENDS DETECTED: {structure.get('potential_orphans', [])}")
        if not structure.get("connectivity_valid"):
            lines.append("- CONNECTIVITY INVALID")
        if not structure.get("partial_orders_valid"):
            lines.append("- PARTIAL ORDERS INVALID")

        # Conversion
        conversion = analysis_result.get("conversion", {})
        lines.append(f"- Petri net conversion: {'SUCCESS' if conversion.get('petri_net_success') else 'FAILED'}")
        lines.append(f"- BPMN conversion: {'SUCCESS' if conversion.get('bpmn_success') else 'FAILED'}")

        # Issues
        issues = analysis_result.get("issues", [])
        if issues:
            lines.append(f"- DETECTED ISSUES: {'; '.join(issues[:5])}")  # Limit to first 5

        return "\n".join(lines)

    def forward(self, powl_string: str, context_description: str = "") -> dspy.Prediction:
        """Judge a POWL model.

        Parameters
        ----------
        powl_string : str
            The POWL model string to evaluate.
        context_description : str, optional
            Natural language description of the process (helps judge plausibility).

        Returns
        -------
        dspy.Prediction
            With 'verdict' (bool), 'reasoning' (str), and 'analysis' (str).
        """
        # Load demos on first forward pass
        if self.use_demos and not hasattr(self.judge.predict, 'demos'):
            self.load_demos()

        # Run real analysis if enabled
        analysis_summary = ""
        analysis_result = None
        if self.use_real_analysis:
            analysis_out = self._run_real_analysis(powl_string)
            analysis_result = analysis_out.get("return_value")
            if analysis_result:
                analysis_summary = self._format_analysis_for_llm(analysis_result)

        # Build enhanced context
        if not context_description:
            context_description = "No specific process context provided. Judge on structural soundness alone."

        if analysis_summary:
            enhanced_context = f"{context_description}\n\n{analysis_summary}"
        else:
            enhanced_context = context_description

        # Call LLM with analysis as context
        pred = self.judge(
            powl_string=powl_string,
            context_description=enhanced_context,
        )

        # Attach analysis result to prediction
        if analysis_result:
            setattr(pred, "analysis", analysis_result)

        return pred


def judge_powl(
    powl_string: str,
    context_description: str = "",
    model: str = "groq/openai/gpt-oss-20b",
    api_key=None,
    api_base=None,
    use_demos: bool = True,
    always_run_once: bool = True,
    use_real_analysis: bool = True,
) -> dict:
    """Judge whether a POWL model is good.

    Parameters
    ----------
    powl_string : str
        The POWL model string to evaluate.
    context_description : str, optional
        Natural language description of the process.
    model : str
        LLM model identifier (litellm format).
    api_key : str, optional
        API key.
    api_base : str, optional
        Custom API base URL.
    use_demos : bool
        Whether to use few-shot examples for more nuanced judgment.
    always_run_once : bool
        Whether to always provide feedback once, even if the POWL is correct.
    use_real_analysis : bool
        Whether to run real pm4py analysis before LLM reasoning.

    Returns
    -------
    dict
        With 'verdict' (bool), 'reasoning' (str), 'analysis' (dict or None).
    """
    from pm4py.algo.dspy.powl.optimize import configure_lm

    configure_lm(model=model, api_key=api_key, api_base=api_base)

    judge = POWLJudge(
        use_demos=use_demos,
        always_run_once=always_run_once,
        use_real_analysis=use_real_analysis
    )
    pred = judge(powl_string=powl_string, context_description=context_description)

    verdict = getattr(pred, "verdict", False)
    if isinstance(verdict, str):
        verdict = verdict.strip().lower() in ("true", "yes", "1")

    reasoning = getattr(pred, "reasoning", "")
    analysis = getattr(pred, "analysis", None)

    return {
        "verdict": bool(verdict),
        "reasoning": str(reasoning),
        "analysis": analysis
    }
