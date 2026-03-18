#!/bin/bash
echo "Запуск панели управления MCP (Mac/Linux)..."

cd "$(dirname "$0")"

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo ""
    echo "Python3 не найден на вашем компьютере."
    echo ""
    echo "Установите его одним из способов:"
    echo "  1. Homebrew (рекомендуется):"
    echo "     /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo "     brew install python3"
    echo ""
    echo "  2. Официальный сайт: https://python.org/downloads"
    echo ""
    read -p "Нажмите Enter для выхода..."
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "[Создаю виртуальную среду Python...]"
    python3 -m venv venv
    echo "[Устанавливаю зависимости...]"
    ./venv/bin/pip install mcp pydantic --quiet
    echo "Готово."
fi

./venv/bin/python manager.py
