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

'''
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions GmbH

LiteLLM connector for PM4Py.
Provides unified LLM access across 100+ providers via litellm.
'''
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any
import base64
import os
from pm4py.util import constants


class Parameters(Enum):
    API_KEY = "api_key"
    API_BASE = "api_base"
    LITELLM_MODEL = "litellm_model"
    IMAGE_PATH = "image_path"
    MAX_TOKENS = "max_tokens"
    TEMPERATURE = "temperature"
    EXTRA_PAYLOAD = "extra_payload"


def apply(prompt: str, parameters: Optional[Dict[Any, Any]] = None) -> str:
    """
    Sends a prompt via litellm and returns the response.

    Supports any litellm-compatible model string, e.g.:
        - openai/gpt-4.1
        - anthropic/claude-sonnet-4-20250514
        - gemini/gemini-2.5-flash
        - groq/openai/gpt-oss-20b

    :param prompt: The prompt to send
    :param parameters: Optional parameters including:
        - litellm_model: Model name in litellm format (default from PM4PY_LITELLM_DEFAULT_MODEL env var or "openai/gpt-4.1")
        - api_key: API key (default: from provider-specific env vars picked up by litellm)
        - api_base: Custom API base URL
        - max_tokens: Maximum tokens in response
        - temperature: Sampling temperature (default: 0.0)
        - image_path: Path to image for vision models
        - extra_payload: Additional fields merged into the litellm.completion() call
    :return: The LLM response as a string
    """
    from litellm import completion

    if parameters is None:
        parameters = {}

    image_path = exec_utils.get_param_value(
        Parameters.IMAGE_PATH, parameters, None
    )
    api_key = exec_utils.get_param_value(
        Parameters.API_KEY, parameters, None
    )
    api_base = exec_utils.get_param_value(
        Parameters.API_BASE, parameters, None
    )
    max_tokens = exec_utils.get_param_value(
        Parameters.MAX_TOKENS, parameters, None
    )
    temperature = exec_utils.get_param_value(
        Parameters.TEMPERATURE, parameters, 0.0
    )
    extra_payload = exec_utils.get_param_value(
        Parameters.EXTRA_PAYLOAD, parameters, {}
    )

    model = exec_utils.get_param_value(
        Parameters.LITELLM_MODEL,
        parameters,
        constants.LITELLM_DEFAULT_MODEL if hasattr(constants, 'LITELLM_DEFAULT_MODEL') else "openai/gpt-4.1",
    )

    # Build message content
    if image_path is not None:
        image_format = os.path.splitext(image_path)[1][1:].lower()
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
        content = [
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/{image_format};base64,{base64_image}"
                },
            },
        ]
    else:
        content = prompt

    kwargs = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "temperature": temperature,
    }

    if api_key is not None:
        kwargs["api_key"] = api_key
    if api_base is not None:
        kwargs["api_base"] = api_base
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    if extra_payload:
        kwargs.update(extra_payload)

    response = completion(**kwargs)

    return response.choices[0].message.content
