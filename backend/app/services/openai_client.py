import os
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from openai import OpenAI


def chat_completion(
    messages: List[Dict[str, Any]],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Missing OPENAI_API_KEY")

    resolved_model = model or os.getenv("OPENAI_MODEL", "gpt-5")

    try:
        client = OpenAI(api_key=api_key)
        params: Dict[str, Any] = {
            "model": resolved_model,
            "messages": messages,
        }

        if not str(resolved_model).startswith("gpt-5"):
            if temperature is not None and temperature != 1:
                params["temperature"] = temperature

        completion = client.chat.completions.create(**params)
        return completion.choices[0].message.content
    except Exception as exc:  # pragma: no cover - surface upstream
        raise HTTPException(status_code=500, detail=str(exc))


