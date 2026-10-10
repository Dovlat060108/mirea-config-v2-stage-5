"""Startup configuration and script error reporting."""

import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from config import arguments, run_script
from shell import Shell


class ConfigTests(unittest.TestCase):
    """Validate all configuration options and startup script modes."""

    def test_arguments(self):
        """Both paths and no-repl can be supplied together."""
        args = arguments(["--vfs", "a.json", "--script", "a.txt",
                          "--no-repl"])
        self.assertEqual(args.vfs, "a.json")
        self.assertEqual(args.script, "a.txt")
        self.assertTrue(args.no_repl)

    def test_comments_and_error(self):
        """Skip comments, echo commands and continue after errors."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "startup.txt"
            path.write_text("# comment\nls # inline\nbad\nexit\n",
                            encoding="utf-8")
            output = io.StringIO()
            shell = Shell()
            with contextlib.redirect_stdout(output):
                self.assertFalse(run_script(shell, path))
            self.assertIn("строка 3", output.getvalue())
            self.assertFalse(shell.running)

    def test_missing_script(self):
        """Missing scripts produce failure with a visible error."""
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertFalse(run_script(Shell(), "/missing/startup"))
