@echo off
cd backend
if not exist .venv python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
if not exist .env copy .env.example .env
python seed.py
uvicorn app.main:app --reload --port 8000
