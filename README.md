# AgentAirgap

AgentAirgap is a dependency-free harness for testing whether a Python agent still behaves when network sockets and child-process escape paths are denied. It injects a Python audit hook before the target script starts, supplies a minimal environment, captures output, and enforces a timeout.

```bash
python -m agentairgap --probe
python -m agentairgap --timeout 10 -- python my_agent.py
```

The JSON result records the command, return code, timeout state, stdout, and stderr. The built-in probe must report both sockets and subprocesses as blocked.

## Honest boundary

This is a Python-runtime test harness, not an operating-system sandbox. Native extensions, non-Python executables, hostile code, filesystem access, and kernel exploits are outside its security boundary. Use containers, namespaces, seccomp, or a separate machine for adversarial isolation. Its practical purpose is reproducibly proving that ordinary Python agent workflows do not silently depend on DNS, sockets, inherited credentials, or subprocess tools.

## Test

```bash
python -m unittest discover -s tests -v
```

## Fund more development

Donations increase RequiredTruth development production. See [SUPPORT.md](SUPPORT.md); confirmed donors may claim a transaction hash in an issue and request a specific direction.

Apache-2.0 licensed.


## Install and run

```sh
chmod +x install.sh run.sh
./install.sh
./run.sh --help
```
