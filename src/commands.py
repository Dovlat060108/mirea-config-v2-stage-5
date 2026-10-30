"""Basic VFS commands for stage four."""

from datetime import datetime
import fnmatch
import posixpath

from vfs import normalize


FIND_ARGUMENT_COUNTS = (0, 1, 3)
FIND_FILTER_ARGUMENT_COUNT = 3


def require_count(args, maximum, usage, minimum=0):
    """Validate argument count and reject unsupported options."""
    if not minimum <= len(args) <= maximum:
        raise ValueError(f"использование: {usage}")
    if any(arg.startswith("-") for arg in args):
        raise ValueError(f"неподдерживаемый параметр; {usage}")


class Commands:
    """Implement ls, cd, tac, date and find on the virtual filesystem."""

    def __init__(self, shell):
        """Keep references to shell state and the loaded VFS."""
        self.shell = shell
        self.vfs = shell.vfs

    def ls(self, args):
        """List directory children or the supplied file name."""
        require_count(args, 1, "ls [путь]")
        path = normalize(args[0] if args else ".", self.shell.cwd)
        if self.vfs.node(path)["type"] == "file":
            return posixpath.basename(path)
        return "\n".join(posixpath.basename(name)
                         for name in self.vfs.children(path))

    def cd(self, args):
        """Change directory; no arguments return to the VFS root."""
        require_count(args, 1, "cd [каталог]")
        path = normalize(args[0] if args else "/", self.shell.cwd)
        self.vfs.directory(path)
        self.shell.cwd = path

    def tac(self, args):
        """Concatenate files with their line order reversed per file."""
        require_count(args, float("inf"), "tac файл [файл ...]", 1)
        result = []
        for name in args:
            text = self.vfs.text(normalize(name, self.shell.cwd))
            result.extend(reversed(text.splitlines()))
        return "\n".join(result)

    def date(self, args):
        """Show local OS date/time or one strftime format with + prefix."""
        require_count(args, 1, "date [+формат]")
        if args and not args[0].startswith("+"):
            raise ValueError("использование: date [+формат]")
        fmt = args[0][1:] if args else "%Y-%m-%d %H:%M:%S %Z"
        return datetime.now().astimezone().strftime(fmt)

    def find(self, args):
        """Recursively list paths, optionally filtering by -name glob."""
        root, pattern = self._find_settings(args)
        names = self._find_paths(root)
        return "\n".join(name for name in names
                         if fnmatch.fnmatchcase(posixpath.basename(name)
                                               or "/", pattern))

    def _find_settings(self, args):
        """Validate find arguments and resolve its root and pattern."""
        count = len(args)
        if count not in FIND_ARGUMENT_COUNTS:
            raise ValueError("использование: find [путь] [-name шаблон]")
        filtered = count == FIND_FILTER_ARGUMENT_COUNT
        if filtered and args[1] != "-name":
            raise ValueError("find: поддерживается только -name")
        root = normalize(args[0] if args else ".", self.shell.cwd)
        self.vfs.node(root)
        pattern = args[2] if filtered else "*"
        return root, pattern

    def _find_paths(self, root):
        """List the root and descendants without matching sibling names."""
        prefix = root.rstrip("/") + "/"
        return sorted(name for name in self.vfs.nodes
                      if name == root or name.startswith(prefix))


def install(shell):
    """Register the five fully implemented stage-four commands."""
    commands = Commands(shell)
    for name in ("ls", "cd", "tac", "date", "find"):
        shell.commands[name] = getattr(commands, name)
