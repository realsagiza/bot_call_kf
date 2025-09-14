from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from openai import OpenAI


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
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Missing OPENAI_API_KEY")

        model = req.model or os.getenv("OPENAI_MODEL", "gpt-5")

        try:
            client = OpenAI(api_key=api_key)
            params: dict = {
                "model": model,
                "messages": req.messages,
            }
            # Some models (e.g., gpt-5) do not support overriding temperature.
            if not str(model).startswith("gpt-5"):
                if req.temperature is not None and req.temperature != 1:
                    params["temperature"] = req.temperature

            completion = client.chat.completions.create(**params)
            content = completion.choices[0].message.content
            return ChatResponse(reply=content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app


app = create_app()

