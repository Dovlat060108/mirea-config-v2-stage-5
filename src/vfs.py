"""JSON virtual filesystem; all changes stay in process memory."""

import base64
import binascii
import json
import posixpath
import time
from pathlib import Path


def normalize(path, cwd="/"):
    """Resolve relative paths and dot components from the VFS root."""
    joined = path if path.startswith("/") else posixpath.join(cwd, path)
    return "/" + posixpath.normpath(joined).lstrip("/")


class VFS:
    """Store nodes as absolute paths with bytes and timestamps."""

    def __init__(self):
        """Create an empty root directory."""
        self.nodes = {"/": {"type": "dir", "mtime": time.time()}}

    @classmethod
    def load(cls, path):
        """Read and validate JSON without extracting or writing files."""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("VFS: ожидается объект с массивом nodes")
        if not isinstance(data.get("nodes"), list):
            raise ValueError("VFS: ожидается объект с массивом nodes")
        vfs = cls()
        for item in data["nodes"]:
            vfs.add(item)
        for name in vfs.nodes:
            if name != "/":
                vfs.directory(posixpath.dirname(name))
        return vfs

    def add(self, item):
        """Validate one unique node and decode optional base64 content."""
        if not isinstance(item, dict):
            raise ValueError("VFS: узел должен быть объектом")
        path, kind = item.get("path"), item.get("type")
        if not isinstance(path, str) or not path.startswith("/"):
            raise ValueError("VFS: нужен абсолютный путь")
        if normalize(path) != path or path in self.nodes:
            raise ValueError(f"VFS: некорректный/повторный путь: {path}")
        if kind not in ("dir", "file"):
            raise ValueError("VFS: type должен быть dir или file")
        node = {"type": kind, "mtime": time.time()}
        if kind == "file":
            node["content"] = self.decode(item)
        self.nodes[path] = node

    @staticmethod
    def decode(item):
        """Decode UTF-8 text or strict base64, rejecting other formats."""
        content = item.get("content", "")
        if not isinstance(content, str):
            raise ValueError("VFS: content должен быть строкой")
        encoding = item.get("encoding", "utf-8")
        if encoding == "utf-8":
            return content.encode("utf-8")
        if encoding != "base64":
            raise ValueError("VFS: неизвестная кодировка")
        try:
            return base64.b64decode(content, validate=True)
        except (binascii.Error, ValueError) as error:
            raise ValueError("VFS: неверный base64") from error

    def node(self, path):
        """Return a node or a readable missing-path error."""
        if path not in self.nodes:
            raise ValueError(f"путь не найден: {path}")
        return self.nodes[path]

    def directory(self, path):
        """Require an existing directory."""
        if self.node(path)["type"] != "dir":
            raise ValueError(f"не каталог: {path}")

    def children(self, path):
        """List sorted direct children only."""
        self.directory(path)
        return sorted(name for name in self.nodes
                      if name != "/" and posixpath.dirname(name) == path)

    def text(self, path):
        """Read a UTF-8 file; binary and directory input are errors."""
        node = self.node(path)
        if node["type"] != "file":
            raise ValueError(f"не файл: {path}")
        return node["content"].decode("utf-8")

