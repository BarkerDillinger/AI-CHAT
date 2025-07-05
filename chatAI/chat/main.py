import os
import requests
import markdown2
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter

from .conversation import create_conversation, add_message, get_conversation, list_conversations
from .routes.models import router as models_router

import sys
print("Python executable:", sys.executable)


# Set up markdown2 renderer
md = markdown2.Markdown(extras=["fenced-code-blocks", "tables", "strike", "footnotes", "cuddled-lists"])

router = APIRouter()

def create_app():
    app = FastAPI()

    # Mount router
    app.include_router(models_router)

    # Set Ollama API endpoint
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

    # Store chat history
    history = []

    # Static files and Jinja2 templates
    app.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="templates")

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request):
        selected_model = request.cookies.get("selected_model", "hermes3:latest")

        rendered_history = []
        for entry in history:
            rendered_entry = dict(entry)
            rendered_entry["response_html"] = md.convert(entry["response"])
            rendered_history.append(rendered_entry)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "history": rendered_history,
            "default_model": selected_model
        })

    @app.post("/ask")
    def ask(request: Request, prompt: str = Form(...), model: str = Form("hermes3")):
        print(f"[INFO] Received prompt using model: {model}")

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

        history.append({
            "prompt": prompt,
            "response": result,
            "model": model
        })

        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="selected_model", value=model, max_age=3600 * 24 * 30)
        return response

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("chat.main:app", host="127.0.0.1", port=8080, reload=True)
