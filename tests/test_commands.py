"""Basic command integration tests using an in-memory VFS."""

import contextlib
import io
import unittest

from commands import install
from shell import Shell
from vfs import VFS


class CommandTests(unittest.TestCase):
    """Check directory navigation, reverse lines and recursive search."""

    def setUp(self):
        """Load a realistic fixture and install stage-four commands."""
        self.shell = Shell(VFS.load("examples/vfs.json"))
        install(self.shell)

    def output(self, command):
        """Capture output and require a successful command."""
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertTrue(self.shell.execute(command))
        return output.getvalue()

    def test_ls(self):
        """ls shows direct children and supports files and empty dirs."""
        self.assertEqual(self.output("ls /docs"), "a\nnotes.txt\n")
        self.assertEqual(self.output("ls /docs/notes.txt"), "notes.txt\n")
        self.assertEqual(self.output("ls /empty"), "")

    def test_cd(self):
        """cd resolves relative paths, parent paths and no argument."""
        self.output("cd /docs/a")
        self.output("cd ../a/b")
        self.assertEqual(self.shell.cwd, "/docs/a/b")
        self.output("cd")
        self.assertEqual(self.shell.cwd, "/")

    def test_tac(self):
        """tac reverses each file's line order."""
        self.assertEqual(self.output("tac /docs/notes.txt"),
                         "third\nsecond\nfirst\n")
        self.assertEqual(self.output("tac /docs/a/b/c.txt"), "deep\n")

    def test_date(self):
        """date supports its documented formatting mode."""
        self.assertRegex(self.output("date +%Y-%m-%d"),
                         r"^\d{4}-\d{2}-\d{2}\n$")
        self.assertTrue(self.output("date").strip())

    def test_find(self):
        """find recurses and filters basenames using glob matching."""
        self.assertEqual(self.output("find /docs -name *.txt"),
                         "/docs/a/b/c.txt\n/docs/notes.txt\n")
        self.assertIn("/docs/a/b\n", self.output("find /docs"))

    def test_errors(self):
        """Missing paths, binary text and incorrect arguments fail."""
        commands = ["cd /docs/notes.txt", "ls /missing", "ls -a",
                    "tac", "tac /binary.bin", "date bad",
                    "find / -bad x", "find a b", "cd a b"]
        with contextlib.redirect_stdout(io.StringIO()):
            for command in commands:
                with self.subTest(command=command):
                    self.assertFalse(self.shell.execute(command))

    def test_find_modes_and_boundaries(self):
        """Default, relative and file roots must not include siblings."""
        self.shell.vfs.add({"path": "/docs-other", "type": "dir"})
        self.assertIn("/docs-other\n", self.output("find"))
        self.assertNotIn("/docs-other\n", self.output("find /docs"))
        self.output("cd /docs")
        self.assertEqual(self.output("find . -name notes.txt"),
                         "/docs/notes.txt\n")
        self.assertEqual(self.output("find notes.txt"),
                         "/docs/notes.txt\n")
        self.assertEqual(self.output("find . -name absent*"), "")
