# chat/routes/models.py

from fastapi import APIRouter
from fastapi.responses import JSONResponse
import subprocess
import re

router = APIRouter()

@router.get("/models")
def get_models():
    try:
        result = subprocess.run(['ollama', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout.strip().split('\n')
        models = []
        for line in output[1:]:
            parts = re.split(r'\s{2,}', line.strip())
            if parts:
                full_name = parts[0]  # Keep namespace and tag
                models.append(full_name)
        return JSONResponse(content=sorted(set(models)))
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

