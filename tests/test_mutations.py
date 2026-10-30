"""Mutation tests, including input-file immutability."""

import contextlib
import io
from pathlib import Path
import unittest

from commands import install as install_commands
from mutations import install
from shell import Shell
from vfs import VFS


class MutationTests(unittest.TestCase):
    """Verify content, subtree movement and invalid operations."""

    def setUp(self):
        """Read the fixture and register all commands."""
        self.path = Path("examples/vfs.json")
        self.before = self.path.read_bytes()
        self.shell = Shell(VFS.load(self.path))
        install_commands(self.shell)
        install(self.shell)

    def execute(self, line):
        """Run without printing test output."""
        with contextlib.redirect_stdout(io.StringIO()):
            return self.shell.execute(line)

    def test_touch(self):
        """touch creates files and preserves existing file content."""
        self.assertTrue(self.execute("touch /new.txt /empty/a"))
        self.assertEqual(self.shell.vfs.text("/new.txt"), "")
        node = self.shell.vfs.node("/docs/notes.txt")
        node["mtime"] = 0
        self.assertTrue(self.execute("touch /docs/notes.txt"))
        self.assertGreater(node["mtime"], 0)
        self.assertEqual(node["content"], b"first\nsecond\nthird\n")

    def test_move_file_and_overwrite(self):
        """mv renames files and overwrites existing file targets."""
        self.assertTrue(self.execute("touch /dest.txt"))
        self.assertTrue(self.execute("mv /docs/notes.txt /dest.txt"))
        self.assertNotIn("/docs/notes.txt", self.shell.vfs.nodes)
        self.assertTrue(self.shell.vfs.text("/dest.txt").startswith("first"))

    def test_move_subtree_and_cwd(self):
        """Moving a directory relocates children and the active cwd."""
        self.assertTrue(self.execute("cd /docs/a/b"))
        self.assertTrue(self.execute("mv /docs/a /empty"))
        self.assertIn("/empty/a/b/c.txt", self.shell.vfs.nodes)
        self.assertEqual(self.shell.cwd, "/empty/a/b")

    def test_errors(self):
        """Reject recursive moves, root moves and missing parents."""
        for command in ("mv /docs /docs/a", "mv / /root", "touch",
                        "touch /missing/a", "mv /missing /a", "mv a",
                        "mv /docs /binary.bin", "touch -x"):
            with self.subTest(command=command):
                self.assertFalse(self.execute(command))

    def test_disk_unchanged(self):
        """Changes affect memory and disappear after a fresh load."""
        self.assertTrue(self.execute("touch /temp.txt"))
        self.assertTrue(self.execute("mv /docs /renamed"))
        self.assertEqual(self.path.read_bytes(), self.before)
        fresh = VFS.load(self.path)
        self.assertIn("/docs", fresh.nodes)
        self.assertNotIn("/temp.txt", fresh.nodes)

    def test_rejected_moves_preserve_all_nodes(self):
        """Invalid destinations must leave the complete VFS unchanged."""
        from copy import deepcopy

        before = deepcopy(self.shell.vfs.nodes)
        commands = ("mv / /root", "mv /docs /docs/a",
                    "mv /docs /binary.bin",
                    "mv /docs/notes.txt /missing/new.txt")
        for command in commands:
            with self.subTest(command=command):
                self.assertFalse(self.execute(command))
                self.assertEqual(self.shell.vfs.nodes, before)

    def test_move_overwrites_file_inside_directory(self):
        """A directory target keeps the source basename when overwriting."""
        self.assertTrue(self.execute("touch /empty/notes.txt"))
        self.assertTrue(self.execute("mv /docs/notes.txt /empty"))
        self.assertEqual(self.shell.vfs.text("/empty/notes.txt"),
                         "first\nsecond\nthird\n")
        self.assertNotIn("/docs/notes.txt", self.shell.vfs.nodes)

    def test_move_same_file_is_unchanged(self):
        """Moving a file onto itself succeeds without changing its data."""
        from copy import deepcopy

        before = deepcopy(self.shell.vfs.nodes)
        self.assertTrue(self.execute("mv /binary.bin /binary.bin"))
        self.assertEqual(self.shell.vfs.nodes, before)
