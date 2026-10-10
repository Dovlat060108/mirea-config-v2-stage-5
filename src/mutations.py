"""Commands which change VFS state only in memory."""

from commands import require_count
from vfs import normalize


class Mutations:
    """Provide mv and touch and preserve the active directory path."""

    def __init__(self, shell):
        """Bind the shell and its VFS."""
        self.shell = shell

    def touch(self, args):
        """Create or timestamp one or more files, requiring parents."""
        require_count(args, float("inf"), "touch файл [файл ...]", 1)
        for name in args:
            self.shell.vfs.touch(normalize(name, self.shell.cwd))

    def mv(self, args):
        """Move one file or directory, updating cwd if its parent moves."""
        require_count(args, 2, "mv источник назначение", 2)
        source = normalize(args[0], self.shell.cwd)
        target = normalize(args[1], self.shell.cwd)
        target = self.shell.vfs.move(source, target)
        current = self.shell.cwd
        if current == source or current.startswith(source + "/"):
            self.shell.cwd = target + current[len(source):]


def install(shell):
    """Register mv and touch."""
    commands = Mutations(shell)
    shell.commands.update({"mv": commands.mv, "touch": commands.touch})
