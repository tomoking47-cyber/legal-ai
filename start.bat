@echo off
cd /d C:\Users\ISB\Desktop\legal-ai
start "" "C:\Users\ISB\AppData\Local\Python\pythoncore-3.14-64\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000
timeout /t 3
start "" "C:\Users\ISB\Desktop\legal-ai\chat.html"
