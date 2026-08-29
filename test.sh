#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PY="$ROOT/.venv/bin/python"

if [[ ! -x "$PY" ]]; then
    echo "Run ./install.sh first." >&2
    exit 1
fi

cd "$ROOT"
"$PY" -m compileall -q agentairgap tests project_gui.py
"$PY" -m unittest discover -s tests -p 'test_*.py' -v

probe_output="$("$ROOT/cli.sh" --probe)"
"$PY" -c '
import json
import sys

payload = json.load(sys.stdin)
assert payload["returncode"] == 0, payload
assert payload["timed_out"] is False, payload
probe = json.loads(payload["stdout"])
assert probe["socket"].startswith("blocked:"), probe
assert probe["subprocess"].startswith("blocked:"), probe
' <<<"$probe_output"

echo "AgentAirgap tests and enforcement probe passed."
