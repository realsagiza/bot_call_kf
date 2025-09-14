from __future__ import annotations

from typing import Any, Dict, List, Optional
from threading import RLock

from app.services.agent import apply_agent_to_messages
from app.services.openai_client import chat_completion


class InMemorySessionStore:
    """Very simple in-memory session message store.

    Stores only non-system messages. System prompts are injected per-request via agent.
    """

    def __init__(self, max_messages: int = 20) -> None:
        self._sessions: Dict[str, List[Dict[str, Any]] ] = {}
        self._lock = RLock()
        self._max_messages = max_messages

    def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._sessions.get(session_id, []))

    def _set_messages(self, session_id: str, messages: List[Dict[str, Any]]) -> None:
        with self._lock:
            self._sessions[session_id] = messages[-self._max_messages :]

    def append_user(self, session_id: str, content: str) -> None:
        history = self.get_messages(session_id)
        history.append({"role": "user", "content": content})
        self._set_messages(session_id, history)

    def append_assistant(self, session_id: str, content: str) -> None:
        history = self.get_messages(session_id)
        history.append({"role": "assistant", "content": content})
        self._set_messages(session_id, history)

    def generate_reply(
        self,
        session_id: str,
        user_text: str,
        agent: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Append user message, call model with agent system + history, append assistant reply."""
        # 1) Append user
        self.append_user(session_id, user_text)

        # 2) Build messages: agent system + history
        history = self.get_messages(session_id)
        resolved = apply_agent_to_messages(history, agent)

        # 3) Call model
        reply_text = chat_completion(messages=resolved, model=model, temperature=temperature)

        # 4) Append assistant
        self.append_assistant(session_id, reply_text)

        return reply_text


SESSION_STORE = InMemorySessionStore(max_messages=40)


