@echo off
chcp 65001 >nul
echo Запуск панели управления...

IF NOT EXIST "venv" (
    echo [Создаю виртуальную среду...]
    python -m venv venv
    venv\Scripts\pip install mcp pydantic >nul 2>&1
)

venv\Scripts\python manager.py
pause