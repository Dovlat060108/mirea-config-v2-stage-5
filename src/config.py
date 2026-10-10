"""Command line configuration and startup script execution."""

import argparse
from pathlib import Path


def arguments(argv=None):
    """Parse VFS/script locations and an optional noninteractive mode."""
    parser = argparse.ArgumentParser(description="Эмулятор, вариант 2")
    parser.add_argument("--vfs", default="examples/vfs.json")
    parser.add_argument("--script", help="UTF-8 файл команд")
    parser.add_argument("--no-repl", action="store_true")
    return parser.parse_args(argv)


def run_script(shell, path):
    """Echo script commands, skip Python comments, report each error."""
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        print(f"Ошибка скрипта: {error}")
        return False
    success = True
    for number, raw in enumerate(lines, 1):
        line = raw.partition("#")[0].strip()
        if not line:
            continue
        print(shell.prompt() + line)
        if not shell.execute(line):
            print(f"Ошибка скрипта {path}, строка {number}")
            success = False
        if not shell.running:
            break
    return success
