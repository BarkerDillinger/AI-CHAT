from fastapi import APIRouter
from ..conversation import DB_FILE, DB_KEY
from fastapi.responses import RedirectResponse, JSONResponse

router = APIRouter()

@router.get("/new", response_class=RedirectResponse)
async def new_conversation():
    response = RedirectResponse(url="/")
    response.delete_cookie("conversation_id")
    return response

@router.get("/health")
async def health():
    return JSONResponse({"status": "ok"})

@router.get("/health/db")
def health_db():
    return {"file": DB_FILE, "encrypted": bool(DB_KEY)}