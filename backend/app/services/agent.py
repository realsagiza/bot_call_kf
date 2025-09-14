from typing import Any, Dict, List, Optional


# Central agent registry. Add new agents here.
AGENT_SYSTEM_PROMPTS: Dict[str, str] = {
    "default": (
        "You are a helpful, concise assistant."
    ),
    "sale": (
        "You are Sale, a proactive sales assistant. Qualify leads, ask clarifying questions, "
        "recommend relevant products/services with clear benefits and pricing when possible, "
        "handle objections empathetically, and move toward a concrete next step (trial, demo, or purchase). "
        "Be concise, structured, and action-oriented."
    ),
}


def get_agent_system_prompt(agent: Optional[str]) -> str:
    if not agent:
        return AGENT_SYSTEM_PROMPTS["default"]
    agent_key = str(agent).strip().lower()
    return AGENT_SYSTEM_PROMPTS.get(agent_key, AGENT_SYSTEM_PROMPTS["default"])


def apply_agent_to_messages(
    messages: List[Dict[str, Any]],
    agent: Optional[str],
) -> List[Dict[str, Any]]:
    """Ensure the message list begins with the system prompt for the chosen agent.

    - Strips any existing system messages from the client for safety and determinism.
    - Prepends the resolved agent system message.
    """

    safe_messages: List[Dict[str, Any]] = [
        {"role": m.get("role"), "content": m.get("content")}
        for m in messages
        if isinstance(m, dict) and m.get("role") != "system"
    ]

    system_prompt = get_agent_system_prompt(agent)
    return [{"role": "system", "content": system_prompt}, *safe_messages]


