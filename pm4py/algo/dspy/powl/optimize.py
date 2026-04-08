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



import os
from typing import Optional, List, Dict, Any

import dspy


def configure_lm(
    model: str = "groq/openai/gpt-oss-20b",
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 65536,
):
    """Configure DSPy's language model.

    Parameters
    ----------
    model : str
        Model identifier in litellm format, e.g.:
        - "groq/openai/gpt-oss-20b" (cheap, recommended)
        - "openai/gpt-4o"
        - "anthropic/claude-sonnet-4-20250514"
    api_key : str, optional
        API key. If None, reads from provider-specific env vars.
    api_base : str, optional
        Custom API base URL.
    temperature : float
        Sampling temperature.
    max_tokens : int
        Maximum tokens in response.
    """
    kwargs = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if api_key is not None:
        kwargs["api_key"] = api_key
    if api_base is not None:
        kwargs["api_base"] = api_base

    lm = dspy.LM(**kwargs)
    dspy.configure(lm=lm)
    return lm


def build_powl_agent(
    max_steps: int = 10,
    expected_activities: Optional[list] = None,
    demos=None,
):
    """Build a POWLAgent with the standard set of tools.

    Parameters
    ----------
    max_steps : int
        Maximum reasoning steps (tool calls) per generation.
    expected_activities : list of str, optional
        Expected activity labels. Enables post-hoc coverage retry.
    demos : list of dspy.Example, optional
        Few-shot examples. If None, loads built-in demos.

    Returns
    -------
    POWLAgent
        The configured agent (needs functions passed to forward()).
    """
    from pm4py.algo.dspy.powl.react_agent import POWLAgent

    if demos is None:
        from pm4py.algo.dspy.powl.demos import get_few_shot_demos
        demos = get_few_shot_demos()

    return POWLAgent(max_steps=max_steps, expected_activities=expected_activities, demos=demos)


def build_function_dict(
    log_obj=None,
    expected_activities: Optional[list] = None,
) -> Dict[str, Any]:
    """Build the function dictionary for POWLAgent.

    Always includes validate_powl and finish.
    Optionally includes check_activity_coverage and check_fitness
    depending on what data is available.

    Parameters
    ----------
    log_obj : optional
        Event log for fitness checking.
    expected_activities : list of str, optional
        Expected activity labels for coverage checking.

    Returns
    -------
    dict
        Function name -> callable mapping.
    """
    from pm4py.algo.dspy.powl.generation import (
        validate_powl,
        check_activity_coverage,
        check_fitness,
        finish,
    )

    functions = {
        "validate_powl": validate_powl,
        "finish": finish,
    }

    if expected_activities:
        functions["check_activity_coverage"] = check_activity_coverage

    if log_obj is not None:
        def _check_fitness(powl_string: str) -> dict:
            return check_fitness(powl_string, log_obj)

        _check_fitness.__name__ = "check_fitness"
        _check_fitness.__doc__ = check_fitness.__doc__
        functions["check_fitness"] = _check_fitness

    return functions


def optimize_with_simba(
    agent,
    trainset,
    metric,
    max_steps: int = 12,
    max_demos: int = 10,
    batch_size: int = 32,
    seed: int = 42,
    save_path: Optional[str] = None,
):
    """Optimize a DSPy POWL agent using SIMBA.

    SIMBA (Stochastic Introspective Mini-Batch Ascent) iteratively improves
    the prompt instructions or few-shot examples by analyzing successful
    and failed predictions on the training set.

    IMPORTANT: The agent must be an EvalWrapper or any dspy.Module whose
    forward() takes a single dspy.Example (keyword args). SIMBA calls
    agent(**example) internally.

    Parameters
    ----------
    agent : dspy.Module
        A wrapped POWLAgent (e.g., EvalWrapper) that accepts single-arg forward.
    trainset : list of dspy.Example
        Training examples with log_abstraction as input.
    metric : callable
        Evaluation metric (e.g., parse_only_metric).
    max_steps : int
        Number of optimization iterations.
    max_demos : int
        Maximum few-shot examples to learn.
    batch_size : int
        Mini-batch size per iteration.
    seed : int
        Random seed.
    save_path : str, optional
        If provided, saves the optimized agent to this path using dspy.save.

    Returns
    -------
    dspy.Module
        The optimized agent.
    """
    simba = dspy.SIMBA(
        metric=metric,
        max_steps=max_steps,
        max_demos=max_demos,
        bsize=batch_size,
    )
    optimized = simba.compile(agent, trainset=trainset, seed=seed)

    if save_path:
        import json
        # Serialize the optimized agent's state manually since
        # dspy.save requires a specific directory structure
        state = {
            "max_steps": getattr(agent, "max_steps", 10),
        }
        # Extract optimized instructions from the ChainOfThought
        inner = getattr(optimized, "agent", optimized)
        cot = getattr(inner, "react", None) if hasattr(inner, "react") else getattr(optimized, "react", None)
        if cot and hasattr(cot, "signature") and hasattr(cot.signature, "instructions"):
            state["instructions"] = cot.signature.instructions
        if cot and hasattr(cot, "demos") and cot.demos:
            state["demos"] = [
                {k: str(v) for k, v in d.items()}
                for d in cot.demos
            ]
        with open(save_path, "w") as f:
            json.dump(state, f, indent=2)

    return optimized


def load_optimized_agent(path: str, max_steps: int = 10, expected_activities=None):
    """Load a previously saved optimized POWL agent.

    Parameters
    ----------
    path : str
        File path where the agent was saved (JSON).
    max_steps : int
        Max reasoning steps for the agent.
    expected_activities : list of str, optional
        Expected activity labels for coverage retry.

    Returns
    -------
    POWLAgent
        The loaded agent with optimized prompts.
    """
    from pm4py.algo.dspy.powl.react_agent import POWLAgent
    import json

    with open(path, "r") as f:
        state = json.load(f)

    agent = POWLAgent(
        max_steps=state.get("max_steps", max_steps),
        expected_activities=expected_activities,
    )

    # Restore optimized instructions
    if "instructions" in state:
        agent.react = dspy.ChainOfThought(dspy.Signature(
            'log_abstraction, trajectory, functions -> next_selected_fn, args: dict[str, Any]',
            instructions=state["instructions"],
        ))

    # Restore demos if available
    if "demos" in state:
        agent.react.demos = state["demos"]

    return agent
