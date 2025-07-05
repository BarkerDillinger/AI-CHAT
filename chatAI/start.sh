#!/bin/bash

source chatai/venv/bin/activate
PYTHONPATH=. uvicorn chat.main:app --reload --port 4242
