import json
import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
from mcp.server.fastmcp import FastMCP

CONFIG_PATH = Path(__file__).parent / "config.json"
try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
except Exception:
    raise RuntimeError("Не найден config.json. Запустите Управление_сервером.bat")

KB_PATHS = [Path(p).resolve() for p in config.get("knowledge_base_paths", [])]
BACKUP_DIR = Path(config["backup_dir"]).resolve()
LOG_DIR = Path(config["log_dir"]).resolve()
EXTENSIONS = tuple(config.get("extensions", [".md", ".txt"]))
IGNORE_FOLDERS = config.get("ignore_folders", [])

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_DIR / "mcp_server.log", encoding="utf-8")]
)
logger = logging.getLogger("MCP_Universal")

mcp = FastMCP("Universal KB Server")

def get_safe_path(file_path: str) -> Path:
    """Проверяет, что запрашиваемый файл находится внутри одной из разрешенных папок."""
    for base_path in KB_PATHS:
        target = (base_path / file_path).resolve()
        if target.is_relative_to(base_path):
            return target
    raise ValueError(f"Путь {file_path} находится вне разрешенных баз знаний.")

def create_backup(target_path: Path):
    """Принудительно создает резервную копию перед записью."""
    if not target_path.exists(): return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"{timestamp}_{target_path.name}"
    
    try:
        shutil.copy2(target_path, backup_path)
        logger.info(f"Бэкап создан: {backup_path.name}")
        
        backups = sorted([f for f in BACKUP_DIR.glob("*") if f.is_file()], key=os.path.getctime)
        while len(backups) > 50:
            backups.pop(0).unlink()
    except Exception as e:
        logger.error(f"Ошибка бэкапа: {e}")

@mcp.tool()
def search_notes(query: str) -> str:
    """Ищет файлы во всех подключенных базах знаний."""
    logger.info(f"Поиск: '{query}'")
    query_lower = query.lower()
    results = []

    try:
        for base_path in KB_PATHS:
            if not base_path.exists(): continue
            
            for root, dirs, files in os.walk(base_path):
                dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS]

                for file in files:
                    if not file.endswith(EXTENSIONS): continue

                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(base_path).as_posix()
                    
                    if query_lower in file.lower():
                        results.append(rel_path)
                        continue
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            if query_lower in f.read().lower():
                                results.append(rel_path)
                    except: pass
                    
                    if len(results) >= 15: break
                if len(results) >= 15: break
            if len(results) >= 15: break # <-- Тот самый фикс! Выходим из всех баз
                
        return "Найдены файлы:\n" + "\n".join(f"- {r}" for r in results) if results else "Ничего не найдено."
    except Exception as e: 
        logger.error(f"Ошибка поиска: {e}")
        return f"Ошибка поиска: {e}"

@mcp.tool()
def read_note(file_path: str) -> str:
    """Читает содержимое файла."""
    logger.info(f"Чтение: {file_path}")
    try:
        target = get_safe_path(file_path)
        if not target.exists(): return f"Ошибка: Файл '{file_path}' не существует."
        with open(target, 'r', encoding='utf-8') as f: return f.read()
    except Exception as e: return f"Ошибка чтения: {e}"

@mcp.tool()
def safe_kb_write(file_path: str, content: str, mode: str = "append", target_header: str = None) -> str:
    """
    КРИТИЧЕСКИ ВАЖНО: Используй ТОЛЬКО этот инструмент для изменения файлов. Он создает бэкапы.
    mode: 'append' (в конец), 'full_replace' (полная замена), 'replace_after_header' (после заголовка).
    """
    logger.info(f"Запись в {file_path} (mode: {mode})")
    try:
        target = get_safe_path(file_path)
        if target.exists(): create_backup(target)
        else: target.parent.mkdir(parents=True, exist_ok=True)
            
        if mode == "append":
            with open(target, 'a', encoding='utf-8') as f: f.write(f"\n{content}\n")
            return f"Текст успешно добавлен в конец '{file_path}'."
        elif mode == "full_replace":
            with open(target, 'w', encoding='utf-8') as f: f.write(content)
            return f"Файл '{file_path}' полностью перезаписан."
        elif mode == "replace_after_header" and target_header:
            if not target.exists(): return "Ошибка: Файл не существует."
            with open(target, 'r', encoding='utf-8') as f: lines = f.readlines()
            new_lines, found = [], False
            for line in lines:
                new_lines.append(line)
                if line.strip() == target_header.strip():
                    new_lines.append(f"\n{content}\n")
                    found = True
            if not found: return f"Заголовок '{target_header}' не найден."
            with open(target, 'w', encoding='utf-8') as f: f.writelines(new_lines)
            return f"Текст успешно вставлен после заголовка."
        return "Ошибка режима."
    except Exception as e: 
        logger.error(f"Ошибка записи: {e}")
        return f"Критическая ошибка: {e}"

if __name__ == "__main__":
    mcp.run()