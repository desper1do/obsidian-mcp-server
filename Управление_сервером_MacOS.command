#!/bin/bash
echo "Запуск панели управления MCP (Mac/Linux)..."

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "[Создаю виртуальную среду Python...]"
    python3 -m venv venv
    ./venv/bin/pip install mcp pydantic >/dev/null 2>&1
fi

./venv/bin/python manager.py