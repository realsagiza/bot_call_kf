from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import Any, Dict, List

from app.services.openai_client import chat_completion
from app.services.agent import apply_agent_to_messages
from app.services.session_store import SESSION_STORE


class ChatRequest(BaseModel):
    messages: list[dict]
    model: str | None = None
    temperature: float | None = None
    agent: str | None = None
    sessionId: str | None = None


class ChatResponse(BaseModel):
    reply: str


def create_app() -> FastAPI:
    app = FastAPI(title="Chatbot Backend", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/api/chat", response_model=ChatResponse)
    async def chat(req: ChatRequest):
        # If a sessionId is provided and the last message from client is user text,
        # use the session store to maintain continuity. Otherwise, fall back to stateless.
        if req.sessionId:
            # Extract last user text from incoming messages, else ignore
            last_user_text = None
            for m in reversed(req.messages or []):
                if isinstance(m, dict) and m.get("role") == "user":
                    last_user_text = str(m.get("content") or "").strip()
                    if last_user_text:
                        break
            if last_user_text:
                content = SESSION_STORE.generate_reply(
                    session_id=req.sessionId,
                    user_text=last_user_text,
                    agent=req.agent,
                    model=req.model,
                    temperature=req.temperature,
                )
            else:
                # no latest user message; just return empty reply
                content = ""
        else:
            resolved_messages = apply_agent_to_messages(req.messages, req.agent)
            content = chat_completion(
                messages=resolved_messages,
                model=req.model,
                temperature=req.temperature,
            )
        return ChatResponse(reply=content)

    # --- LINE-like webhook simulation ---
    @app.post("/webhooks/line")
    async def line_webhook(payload: Dict[str, Any]):
        # Expected minimal shape:
        # {
        #   "events": [
        #     {
        #       "type": "message",
        #       "message": {"type": "text", "text": "Hello"},
        #       "replyToken": "...",
        #       "source": {"type": "user", "userId": "Uxxx"}
        #     }
        #   ]
        # }
        events: List[Dict[str, Any]] = payload.get("events") or []
        if not isinstance(events, list) or len(events) == 0:
            raise HTTPException(status_code=400, detail="Invalid payload: missing events[]")

        replies: List[Dict[str, Any]] = []
        for event in events:
            if not isinstance(event, dict):
                continue
            if event.get("type") != "message":
                continue
            message = event.get("message") or {}
            if message.get("type") != "text":
                continue
            user_text = str(message.get("text") or "").strip()
            if not user_text:
                continue

            user_id = (
                ((event.get("source") or {}).get("userId"))
                or "anonymous"
            )

            agent = payload.get("agent") if isinstance(payload, dict) else None
            # Use user_id as session id for LINE-like chats
            ai_reply = SESSION_STORE.generate_reply(
                session_id=f"line:{user_id}",
                user_text=user_text,
                agent=agent,
            )

            replies.append({
                "to": user_id,
                "replyToken": event.get("replyToken") or "SIMULATED",
                "messages": [
                    {"type": "text", "text": ai_reply}
                ],
            })

        if not replies:
            raise HTTPException(status_code=400, detail="No valid text message events to process")

        # In real LINE integration, we'd call LINE Reply API here. In dev, return the would-be payload.
        return {"replies": replies}

    return app


app = create_app()

