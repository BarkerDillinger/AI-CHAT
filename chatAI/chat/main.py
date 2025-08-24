# File: chat/main.py

import os
import sys
import time
import markdown2
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Routers
from .routes.pages import router as pages_router
from .routes.prompts import router as prompts_router
from .routes.system import router as system_router
from .routes.models import router as models_router

# DB Init
from .conversation import init_db

print("Python executable:", sys.executable)

# Markdown renderer (shared if needed)
md = markdown2.Markdown(
    extras=["fenced-code-blocks", "tables", "strike", "footnotes", "cuddled-lists"]
)

# Templates directory + cache buster
templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "..", "templates")
)
templates.env.globals["BUILD_ID"] = os.getenv("BUILD_ID", str(int(time.time())))


def create_app() -> FastAPI:
    app = FastAPI()

    # Initialize database
    init_db()

    # Mount routes
    app.include_router(pages_router)
    app.include_router(prompts_router)
    app.include_router(system_router)
    app.include_router(models_router)

    # Static files
    app.mount(
        "/static",
        StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "static")),
        name="static",
    )

    # No-store for dynamic pages (leave /static cacheable)
    @app.middleware("http")
    async def no_store_for_dynamic(request: Request, call_next):
        response = await call_next(request)
        if not request.url.path.startswith("/static/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("chat.main:app", host="127.0.0.1", port=4242, reload=True)
