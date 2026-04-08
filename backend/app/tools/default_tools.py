import os
import shlex
import subprocess
from pathlib import Path

import httpx

from app.core.config import get_settings
from app.tools.tool_registry import ToolResult

settings = get_settings()


def read_file(path: str) -> ToolResult:
    p = Path(path)
    if not p.exists() or not p.is_file():
        return ToolResult(False, "file not found", {})
    return ToolResult(True, p.read_text()[:10000], {"path": str(p)})


def write_file(path: str, content: str) -> ToolResult:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return ToolResult(True, "written", {"path": str(p), "bytes": len(content)})


def list_files(path: str = ".") -> ToolResult:
    p = Path(path)
    files = [str(x) for x in p.iterdir()][:200]
    return ToolResult(True, "\n".join(files), {"count": len(files)})


def http_request(url: str, method: str = "GET") -> ToolResult:
    method = method.upper()
    if method not in {"GET", "HEAD"}:
        return ToolResult(False, "only GET/HEAD allowed in MVP", {})
    r = httpx.request(method, url, timeout=10)
    return ToolResult(True, r.text[:4000], {"status_code": r.status_code})


def run_command(command: str) -> ToolResult:
    parts = shlex.split(command)
    if not parts:
        return ToolResult(False, "empty command", {})
    if parts[0] not in settings.command_allowlist:
        return ToolResult(False, f"command '{parts[0]}' not allowed", {})
    result = subprocess.run(parts, capture_output=True, text=True, timeout=10, cwd=os.getcwd())
    output = (result.stdout + "\n" + result.stderr).strip()[:4000]
    return ToolResult(result.returncode == 0, output, {"return_code": result.returncode})


def search_local_data(query: str, path: str = ".") -> ToolResult:
    matches = []
    for root, _, files in os.walk(path):
        for file in files[:100]:
            fp = Path(root) / file
            try:
                txt = fp.read_text(errors="ignore")
            except Exception:
                continue
            if query.lower() in txt.lower():
                matches.append(str(fp))
            if len(matches) >= 20:
                break
        if len(matches) >= 20:
            break
    return ToolResult(True, "\n".join(matches), {"count": len(matches)})
