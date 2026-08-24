from __future__ import annotations

import argparse
import json
import sys

from .runner import python_probe, run_airgapped


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a Python agent with sockets and child processes denied.")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--probe", action="store_true", help="run the built-in enforcement probe")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = python_probe() if args.probe else args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("provide --probe or a command after --")
    result = run_airgapped(command, timeout=args.timeout)
    print(json.dumps({
        "command": list(result.command), "returncode": result.returncode,
        "timed_out": result.timed_out, "stdout": result.stdout, "stderr": result.stderr,
    }, indent=2))
    return result.returncode
