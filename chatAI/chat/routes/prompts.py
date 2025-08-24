# Stage 2: Extract /ask into prompts.py

# File: chat/routes/prompts.py

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from threading import Thread
import os, requests
from ..conversation import (
    create_conversation, add_message, get_recent_conversation_pairs,
    update_conversation_title, save_summarized_memory
)

router = APIRouter()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

@router.post("/ask")
async def ask(request: Request, prompt: str = Form(...), model: str = Form("hermes3")):
    conversation_id = request.cookies.get("conversation_id")
    memory_path = os.path.join("chat", "data", "memory", f"convo_{conversation_id}.txt")

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

    if conversation_id is None:
        conversation_id = create_conversation("Default Chat")
        try:
            resp = requests.post(OLLAMA_URL, json={
                "model": model,
                "prompt": f"Summarize this in 3-5 words:\n\n\"{prompt}\"",
                "stream": False
            })
            resp.raise_for_status()
            title = resp.json().get("response", "").strip().strip('"')
            if title:
                update_conversation_title(conversation_id, title.title())
        except Exception as e:
            print(f"[WARN] Title generation failed: {e}")
    else:
        conversation_id = int(conversation_id)

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": model,
            "prompt": full_prompt,
            "stream": False
        })
        response.raise_for_status()
        result = response.json().get("response", "[No Response]")
    except Exception as e:
        result = f"[Error contacting Ollama: {e}]"

    add_message(conversation_id, "user", prompt, model)
    add_message(conversation_id, "assistant", result, model)

    Thread(target=save_summarized_memory, args=(conversation_id, model)).start()

    redirect = RedirectResponse(url=f"/conversation/{conversation_id}", status_code=303)
    redirect.set_cookie(key="selected_model", value=model, max_age=3600 * 24 * 30)
    redirect.set_cookie(key="conversation_id", value=str(conversation_id), max_age=3600 * 24 * 30)
    return redirect