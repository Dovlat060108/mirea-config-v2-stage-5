"""Loading, paths, base64 and validation of virtual filesystem data."""

import json
from pathlib import Path
import tempfile
import unittest

from vfs import VFS, normalize


class VFSTests(unittest.TestCase):
    """Exercise valid fixtures and malformed inputs."""

    def test_paths(self):
        """Relative paths and traversal are confined to VFS root."""
        self.assertEqual(normalize("../a", "/docs"), "/a")
        self.assertEqual(normalize("../../../a"), "/a")
        self.assertEqual(normalize("//a/./b/.."), "/a")

    def test_fixtures(self):
        """All three required filesystem sizes can be loaded."""
        for filename in ("minimal.json", "files.json", "vfs.json"):
            with self.subTest(filename=filename):
                fs = VFS.load(Path("examples") / filename)
                self.assertIn("/", fs.nodes)
        self.assertIn("/docs/a/b/c.txt", fs.nodes)
        self.assertEqual(fs.nodes["/binary.bin"]["content"], b"\x00\xff")

    def test_invalid_data(self):
        """Reject invalid schema, duplicate paths and missing parents."""
        cases = [[], {"nodes": "bad"}, {"nodes": [None]},
                 {"nodes": [{"path": "relative", "type": "dir"}]},
                 {"nodes": [{"path": "/a", "type": "bad"}]},
                 {"nodes": [{"path": "/x/a", "type": "file"}]},
                 {"nodes": [{"path": "/a", "type": "dir"},
                            {"path": "/a", "type": "dir"}]},
                 {"nodes": [{"path": "/a", "type": "file",
                             "encoding": "base64", "content": "!"}]}]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.json"
            for data in cases:
                path.write_text(json.dumps(data), encoding="utf-8")
                with self.subTest(data=data), self.assertRaises(ValueError):
                    VFS.load(path)

    def test_order_independent(self):
        """A child may precede its parent in the JSON list."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "vfs.json"
            path.write_text(json.dumps({"nodes": [
                {"path": "/a/f", "type": "file"},
                {"path": "/a", "type": "dir"}]}), encoding="utf-8")
            self.assertEqual(VFS.load(path).text("/a/f"), "")

    def test_invalid_json(self):
        """Invalid JSON is rejected."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "vfs.json"
            path.write_text("{broken", encoding="utf-8")
            with self.assertRaises(ValueError):
                VFS.load(path)
