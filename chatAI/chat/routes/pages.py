# File: chat/routes/pages.py

import os
import markdown2
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..conversation import (
    list_conversations,
    get_conversation,
    delete_conversation,
    delete_message,
)

router = APIRouter()

# If you run uvicorn from the repo root, this is simplest:
templates = Jinja2Templates(directory="templates")

md = markdown2.Markdown(
    extras=["fenced-code-blocks", "tables", "strike", "footnotes", "cuddled-lists"]
)

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    selected_model = request.cookies.get("selected_model", "hermes3:latest")
    conversations = list_conversations()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "history": [],
            "default_model": selected_model,
            "conversations": conversations,
            "conversation_id": None,
        },
    )

@router.get("/conversation/{conversation_id}", response_class=HTMLResponse)
async def load_conversation(conversation_id: int, request: Request):
    selected_model = request.cookies.get("selected_model", "hermes3:latest")
    messages = get_conversation(conversation_id)
    if not messages:
        return HTMLResponse("Conversation not found", status_code=404)

    history = []
    model = None
    prompt = None

    # rows are dict-like if using the suggested conversation.py
    for row in messages:
        role = row["sender"]
        content = row["message"]
        msg_model = row["model"]

        if role == "user":
            prompt = content
        elif role == "assistant" and prompt:
            history.append(
                {
                    "prompt": prompt,
                    "response": content,
                    "model": msg_model or "hermes3:latest",
                    "response_html": md.convert(content),
                }
            )
            if not model:
                model = msg_model
            prompt = None

    conversations = list_conversations()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "history": history,
            "default_model": model or selected_model,
            "conversations": conversations,
            "conversation_id": conversation_id,
        },
    )

# IMPORTANT: unindented, top-level route registrations

@router.delete("/conversation/{conversation_id}")
def api_delete_conversation(conversation_id: int):
    if not delete_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "ok"}

@router.delete("/message/{message_id}")
def api_delete_message(message_id: int):
    if not delete_message(message_id):
        raise HTTPException(status_code=404, detail="Message not found")
    return {"status": "ok"}
