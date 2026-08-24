from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
import sys
import tempfile


_HOOK = r'''import sys

_BLOCKED = (
    "socket.",
    "subprocess.Popen",
    "os.system",
    "os.exec",
    "os.spawn",
    "pty.spawn",
)

def _deny(event, args):
    if event.startswith(_BLOCKED):
        raise PermissionError("AgentAirgap blocked audit event: " + event)

sys.addaudithook(_deny)
'''


@dataclass(frozen=True, slots=True)
class AirgapResult:
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool


def _minimal_environment(hook_dir: Path, inherited: dict[str, str]) -> dict[str, str]:
    environment = {
        "PATH": inherited.get("PATH", os.defpath),
        "LANG": inherited.get("LANG", "C.UTF-8"),
        "LC_ALL": inherited.get("LC_ALL", "C.UTF-8"),
        "PYTHONIOENCODING": "utf-8",
        "PYTHONNOUSERSITE": "1",
        "AGENTAIRGAP": "1",
    }
    existing = inherited.get("PYTHONPATH")
    environment["PYTHONPATH"] = str(hook_dir) + (os.pathsep + existing if existing else "")
    return environment


def run_airgapped(command: list[str], *, timeout: float = 30.0) -> AirgapResult:
    if not command:
        raise ValueError("command cannot be empty")
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    with tempfile.TemporaryDirectory(prefix="agentairgap-") as temporary:
        hook_dir = Path(temporary)
        (hook_dir / "sitecustomize.py").write_text(_HOOK, encoding="utf-8")
        try:
            completed = subprocess.run(
                command,
                text=True,
                capture_output=True,
                timeout=timeout,
                env=_minimal_environment(hook_dir, dict(os.environ)),
                check=False,
            )
            return AirgapResult(tuple(command), completed.returncode, completed.stdout, completed.stderr, False)
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            return AirgapResult(tuple(command), 124, stdout, stderr, True)


def python_probe() -> list[str]:
    code = """import json, socket, subprocess, sys
result = {}
for name, action in {
    'socket': lambda: socket.socket(),
    'subprocess': lambda: subprocess.run([sys.executable, '-c', 'pass']),
}.items():
    try:
        action()
        result[name] = 'ALLOWED'
    except PermissionError as exc:
        result[name] = 'blocked: ' + str(exc)
print(json.dumps(result, sort_keys=True))
"""
    return [sys.executable, "-c", code]
