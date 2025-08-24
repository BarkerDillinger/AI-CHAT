# File: chat/routes/system.py

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter()

@router.get("/new", response_class=RedirectResponse)
async def new_conversation():
    response = RedirectResponse(url="/")
    response.delete_cookie("conversation_id")
    return response
