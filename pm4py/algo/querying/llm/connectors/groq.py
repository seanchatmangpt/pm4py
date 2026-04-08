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

Groq LLM connector for PM4Py.
Provides fast inference using Groq's API.
'''
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any
import base64
import os
from pm4py.util import constants


class Parameters(Enum):
    API_URL = "api_url"
    API_KEY = "api_key"
    GROQ_MODEL = "groq_model"
    IMAGE_PATH = "image_path"
    MAX_TOKENS = "max_tokens"
    EXTRA_PAYLOAD = "extra_payload"
    CUSTOM_LLM_PROVIDER = "custom_llm_provider"


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def apply(prompt: str, parameters: Optional[Dict[Any, Any]] = None) -> str:
    """
    Sends a prompt to Groq's API and returns the response.

    :param prompt: The prompt to send
    :param parameters: Optional parameters including:
        - api_key: Groq API key (default: from GROQ_API_KEY env var)
        - groq_model: Model name (default: openai/gpt-oss-20b)
        - api_url: Custom API URL (default: https://api.groq.com/openai/v1)
        - max_tokens: Maximum tokens in response
        - image_path: Path to image for vision models
        - extra_payload: Additional fields to merge into request
    :return: The LLM response as a string
    """
    import requests

    if parameters is None:
        parameters = {}

    image_path = exec_utils.get_param_value(
        Parameters.IMAGE_PATH, parameters, None
    )
    api_key = exec_utils.get_param_value(
        Parameters.API_KEY, parameters, os.environ.get("GROQ_API_KEY")
    )
    api_url = exec_utils.get_param_value(Parameters.API_URL, parameters, None)
    max_tokens = exec_utils.get_param_value(
        Parameters.MAX_TOKENS, parameters, None
    )
    extra_payload = exec_utils.get_param_value(
        Parameters.EXTRA_PAYLOAD, parameters, {}
    )
    simple_content_specification = image_path is None

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. Please set the GROQ_API_KEY "
            "environment variable or pass api_key parameter."
        )

    if api_url is None:
        api_url = "https://api.groq.com/openai/v1/"
    else:
        if not api_url.endswith("/"):
            api_url += "/"

    model = exec_utils.get_param_value(
        Parameters.GROQ_MODEL,
        parameters,
        constants.GROQ_DEFAULT_MODEL if hasattr(constants, 'GROQ_DEFAULT_MODEL') else "openai/gpt-oss-20b",  # Best value
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    messages = []
    payload = {"model": model}

    if simple_content_specification:
        messages.append({"role": "user", "content": prompt})
    else:
        messages.append(
            {"role": "user", "content": [{"type": "text", "text": prompt}]}
        )

    if image_path is not None:
        max_tokens = exec_utils.get_param_value(
            Parameters.MAX_TOKENS, parameters, 16384
        )
        image_format = os.path.splitext(image_path)[1][1:].lower()
        base64_image = encode_image(image_path)

        messages[0]["content"].append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/{image_format};base64,{base64_image}"
                },
            }
        )
        payload["max_tokens"] = max_tokens

    if max_tokens is not None:
        payload["max_tokens"] = max_tokens

    payload["messages"] = messages

    if extra_payload:
        payload.update(extra_payload)

    response = requests.post(
        api_url + "chat/completions",
        headers=headers,
        json=payload,
        timeout=20*60
    ).json()

    if "error" in response:
        raise Exception(response["error"]["message"])

    return response["choices"][0]["message"]["content"]
