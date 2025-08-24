# File: chat/routes/prompts.py
import os
import requests
import sqlite3

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from threading import Thread
from typing import cast
from ..conversation import (
    create_conversation,
    add_message,
    update_conversation_title,
    save_summarized_memory,
)

router = APIRouter()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

# Paths relative to this file: chat/routes → parent is chat/
CHAT_DIR = os.path.dirname(os.path.dirname(__file__))
DB_FILE = os.path.join(CHAT_DIR, "data", "conversation_memory.db")
MEM_DIR = os.path.join(CHAT_DIR, "data", "memory")


def _conversation_exists(cid: int | None) -> bool:
    if cid is None:
        return False
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM conversations WHERE id = ? LIMIT 1", (cid,))
            return cur.fetchone() is not None
    except Exception:
        return False


@router.post("/ask")
async def ask(request: Request, prompt: str = Form(...), model: str = Form("hermes3")):
    # Normalize cookie → conversation_id (int | None)
    raw = request.cookies.get("conversation_id")
    try:
        conversation_id = int(raw) if raw is not None else None
    except (ValueError, TypeError):
        conversation_id = None

    new_convo = False
    if not _conversation_exists(conversation_id):
        # Create the conversation and give it a quick title from the prompt
        conversation_id = create_conversation("New Chat")
        quick_title = (prompt.strip() or "New Chat")[:60].rstrip()
        try:
            update_conversation_title(conversation_id, quick_title)
        except Exception:
            pass
        new_convo = True

    # Memory context
    os.makedirs(MEM_DIR, exist_ok=True)
    memory_path = os.path.join(MEM_DIR, f"convo_{conversation_id}.txt")
    if os.path.exists(memory_path):
        with open(memory_path, "r", encoding="utf-8") as f:
            memory_context = f.read().strip()
        memory_context = (
            "The following is memory from previous parts of the conversation. "
            "Use it only if it helps with the current query:\n\n" + memory_context
        )
    else:
        memory_context = ""

    full_prompt = f"{memory_context}\n\nCurrent user input:\n{prompt}"

    # Ask Ollama
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": full_prompt, "stream": False},
            timeout=120,
        )
        resp.raise_for_status()
        result = resp.json().get("response", "[No Response]")
    except Exception as e:
        result = f"[Error contacting Ollama: {e}]"

    # Narrow Optional[int] → int for type checker (we created the convo above if missing)
    if conversation_id is None:
        raise RuntimeError("Conversation ID missing after creation")
    cid: int = cast(int, conversation_id)

    # Persist the exchange
    add_message(cid, "user", prompt, model)
    add_message(cid, "assistant", result, model)

    # Save a lightweight memory summary in the background
    try:
        summary_text = f"Last prompt:\n{prompt}\n\nLast response:\n{result}\n"
        Thread(target=save_summarized_memory, args=(cid, summary_text), daemon=True).start()
    except Exception:
        pass

    # Redirect to the conversation page and set cookies
    redirect = RedirectResponse(url=f"/conversation/{cid}", status_code=303)
    redirect.set_cookie(key="selected_model", value=model, max_age=3600 * 24 * 30, path="/", samesite="lax")
    redirect.set_cookie(key="conversation_id", value=str(cid), max_age=3600 * 24 * 30, path="/", samesite="lax")
    return redirect

