import json
import os
import sys
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"
CURRENT_DIR = Path(__file__).parent.resolve()

IS_WINDOWS = sys.platform == "win32"
PYTHON_PATH = CURRENT_DIR / "venv" / ("Scripts" if IS_WINDOWS else "bin") / ("python.exe" if IS_WINDOWS else "python")

def load_config():
    if not CONFIG_PATH.exists():
        return {
            "knowledge_base_paths": [],
            "backup_dir": str(CURRENT_DIR / ".backups"),
            "log_dir": str(CURRENT_DIR / ".logs"),
            "extensions": [".md", ".txt"],
            "ignore_folders": [".git", ".obsidian", ".backups", ".logs", "venv", "__pycache__"]
        }
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def show_connection_info():
    main_py = str(CURRENT_DIR / "main.py")
    python_str = str(PYTHON_PATH)

    # JSON для расширения Claude в VS Code (требует type: stdio)
    claude_ext_config = {
        "mcpServers": {
            "obsidian-universal": {
                "command": python_str,
                "args": [main_py],
                "type": "stdio"
            }
        }
    }

    print("\n=== КАК ПОДКЛЮЧИТЬ К РАСШИРЕНИЮ CLAUDE (VS Code) ===")
    print("1. Откройте терминал в VS Code и введите:")
    if IS_WINDOWS:
        print('   code %APPDATA%\\Claude\\settings.json')
    else:
        print('   code ~/.claude/settings.json')
    print("2. Вставьте этот JSON в открывшийся файл и сохраните:\n")
    print(json.dumps(claude_ext_config, indent=2, ensure_ascii=False))

    print("\n=== КАК ПОДКЛЮЧИТЬ К CLAUDE CODE CLI ===")
    print("Выберите пункт 4 — подключение произойдёт автоматически.")
    print(f'Или вручную: claude mcp add obsidian-universal -- "{python_str}" "{main_py}"')
    print("=" * 55)

def connect_claude_code():
    main_py = str(CURRENT_DIR / "main.py")
    python_str = str(PYTHON_PATH)

    print("\n[Подключаю MCP сервер к Claude Code...]")

    if IS_WINDOWS:
        os.system('claude mcp remove obsidian-universal 2>nul')
    else:
        os.system('claude mcp remove obsidian-universal 2>/dev/null')

    cmd = f'claude mcp add obsidian-universal -- "{python_str}" "{main_py}"'
    result = os.system(cmd)

    if result == 0:
        print("✅ Готово! MCP сервер подключён к Claude Code.")
        print("   Перезапустите VS Code, затем проверьте: claude mcp list")
    else:
        print("❌ Не удалось выполнить команду автоматически.")
        print("   Возможно, Claude Code CLI не установлен или не добавлен в PATH.")
        print("   Выполните вручную в терминале:")
        print(f'   claude mcp add obsidian-universal -- "{python_str}" "{main_py}"')

def main():
    config = load_config()

    while True:
        print("\n--- УПРАВЛЕНИЕ БАЗАМИ ЗНАНИЙ ---")
        paths = config["knowledge_base_paths"]
        if not paths:
            print("Нет подключенных папок.")
        else:
            print("Подключенные папки:")
            for i, p in enumerate(paths, 1):
                print(f"  {i}. {p}")

        print(f"\nПлатформа: {'Windows' if IS_WINDOWS else 'macOS / Linux'}")
        print("\nЧто сделать?")
        print("1. Добавить новую папку")
        print("2. Удалить папку из списка")
        print("3. Показать JSON для подключения к Claude")
        print("4. Подключить к Claude Code (CLI) автоматически ⚡")
        print("5. Выход")

        choice = input("> ").strip()

        if choice == '1':
            new_path = input("Перетащите папку сюда (или введите путь): ").strip().strip('"').strip("'")
            if Path(new_path).exists():
                if new_path not in config["knowledge_base_paths"]:
                    config["knowledge_base_paths"].append(new_path)
                    save_config(config)
                    print("✅ Папка успешно добавлена!")
                else:
                    print("⚠️  Эта папка уже есть в списке.")
            else:
                print("❌ Ошибка: Папка не найдена. Проверьте путь.")

        elif choice == '2':
            if not paths:
                print("Удалять нечего.")
                continue
            idx = input("Введите номер папки для удаления: ")
            try:
                idx_int = int(idx)
                if idx_int < 1:
                    raise ValueError
                del_path = config["knowledge_base_paths"].pop(idx_int - 1)
                save_config(config)
                print(f"✅ Папка удалена из списка (файлы на диске остались): {del_path}")
            except (ValueError, IndexError):
                print("❌ Ошибка: Введён неверный номер.")

        elif choice == '3':
            show_connection_info()

        elif choice == '4':
            connect_claude_code()

        elif choice == '5':
            break

if __name__ == "__main__":
    main()