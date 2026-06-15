@echo off
cd /d C:\Users\SvenG\Desktop\GIT\Project1

start cmd /k "C:/Python313/python.exe -m uvicorn backend.main:app --reload"
start cmd /k "cd frontend && C:/Python313/python.exe -m http.server 5500"