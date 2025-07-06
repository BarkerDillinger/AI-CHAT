import os
import sys
import requests
import markdown2

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .conversation import (
    create_conversation,
    add_message,
    get_conversation,
    list_conversations,
    update_conversation_title,
    init_db
)
from .routes.models import router as models_router

print("Python executable:", sys.executable)

md = markdown2.Markdown(extras=["fenced-code-blocks", "tables", "strike", "footnotes", "cuddled-lists"])
templates = Jinja2Templates(directory="templates")

def create_app():
    app = FastAPI()

    # Initialize database
    init_db()

    # Mount router
    app.include_router(models_router)

    # Static files and templates
    app.mount("/static", StaticFiles(directory="static"), name="static")

    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

    @app.get("/new", response_class=RedirectResponse)
    async def new_conversation():
        response = RedirectResponse(url="/")
        response.delete_cookie("conversation_id")
        return response

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        selected_model = request.cookies.get("selected_model", "hermes3:latest")
        conversations = list_conversations()

        return templates.TemplateResponse("index.html", {
            "request": request,
            "history": [],
            "default_model": selected_model,
            "conversations": conversations,
            "conversation_id": None
        })

    @app.get("/conversation/{conversation_id}", response_class=HTMLResponse)
    async def load_conversation(conversation_id: int, request: Request):
        selected_model = request.cookies.get("selected_model", "hermes3:latest")
        convo_data = load_conversation_data(conversation_id)
        if not convo_data:
            return HTMLResponse(content="Conversation not found", status_code=404)

        history, model = convo_data
        rendered_history = []

        for entry in history:
            rendered_entry = dict(entry)
            rendered_entry["response_html"] = md.convert(entry["response"])
            rendered_history.append(rendered_entry)

        conversations = list_conversations()

        return templates.TemplateResponse("index.html", {
            "request": request,
            "history": rendered_history,
            "default_model": model or selected_model,
            "conversations": conversations,
            "conversation_id": conversation_id
        })

    @app.post("/ask")
    async def ask(request: Request, prompt: str = Form(...), model: str = Form("hermes3")):
        conversation_id = request.cookies.get("conversation_id")

        if conversation_id is None:
            conversation_id = create_conversation("Default Chat")

            title_prompt = (
                f"Summarize this conversation topic in 3 to 5 words (title case, no punctuation):\n\n\"{prompt}\""
            )
            try:
                ollama_response = requests.post(OLLAMA_URL, json={
                    "model": model,
                    "prompt": title_prompt,
                    "stream": False
                })
                ollama_response.raise_for_status()
                title = ollama_response.json().get("response", "").strip().strip('"')

                # Post-process: enforce word limit and Title Case
                words = title.split()
                trimmed_title = " ".join(words[:5]).title()

                if trimmed_title:
                    update_conversation_title(conversation_id, trimmed_title)
                    print(f"[DB] Conversation {conversation_id} renamed to: {trimmed_title}")
            except Exception as e:
                print(f"[WARN] Title generation failed: {e}")
        else:
            conversation_id = int(conversation_id)

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }

        try:
            response = requests.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            result = response.json().get("response", "[No Response]")
        except Exception as e:
            result = f"[Error contacting Ollama: {e}]"

        add_message(conversation_id, "user", prompt, model)
        add_message(conversation_id, "assistant", result, model)

        response = RedirectResponse(url=f"/conversation/{conversation_id}", status_code=303)
        response.set_cookie(key="selected_model", value=model, max_age=3600 * 24 * 30)
        response.set_cookie(key="conversation_id", value=str(conversation_id), max_age=3600 * 24 * 30)
        return response

    return app


app = create_app()

def load_conversation_data(conversation_id: int):
    messages = get_conversation(conversation_id)
    if not messages:
        return None

    history = []
    model = None
    prompt = None

    for row in messages:
        role = row[2]
        content = row[3]
        msg_model = row[4]

        if role == "user":
            prompt = content
        elif role == "assistant" and prompt:
            history.append({
                "prompt": prompt,
                "response": content,
                "model": msg_model or "hermes3:latest"
            })
            if not model:
                model = msg_model

    return history, model


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("chat.main:app", host="127.0.0.1", port=8080, reload=True)
