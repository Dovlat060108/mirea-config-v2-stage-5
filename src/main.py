"""Entry point for the shell emulator."""
import sys
from shell import Shell
from config import arguments, run_script
from vfs import VFS


def main():
    """Initialize and run the current stage."""
    args = arguments()
    print(f"VFS: {args.vfs}")
    print(f"Скрипт: {args.script or 'не задан'}")
    print(f"Без REPL: {args.no_repl}")
    try:
        vfs = VFS.load(args.vfs)
    except (OSError, ValueError, UnicodeError) as error:
        print(f"Ошибка загрузки VFS: {error}")
        return 1
    shell = Shell(vfs)
    print(f"Загружено узлов VFS: {len(vfs.nodes)}")
    success = True
    if args.script:
        success = run_script(shell, args.script)
    if shell.running and not args.no_repl:
        shell.repl()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
