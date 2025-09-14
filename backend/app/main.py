from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import Any, Dict, List

from app.services.openai_client import chat_completion


class ChatRequest(BaseModel):
    messages: list[dict]
    model: str | None = None
    temperature: float | None = None


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
        content = chat_completion(
            messages=req.messages,
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

            ai_reply = chat_completion(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for a LINE user."},
                    {"role": "user", "content": user_text},
                ]
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

