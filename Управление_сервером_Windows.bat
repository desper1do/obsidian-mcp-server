@echo off
chcp 65001 >nul
echo Запуск панели управления...

python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ОШИБКА] Python не найден на вашем компьютере.
    echo.
    echo Установите Python с официального сайта: https://python.org/downloads
    echo ВАЖНО: при установке отметьте галочку "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

IF NOT EXIST "venv" (
    echo [Создаю виртуальную среду...]
    python -m venv venv
    echo [Устанавливаю зависимости...]
    venv\Scripts\pip install mcp pydantic >nul 2>&1
    echo Готово.
)

venv\Scripts\python manager.py
pause