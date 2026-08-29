import json
import subprocess
import sys
import unittest

from agentairgap.runner import python_probe, run_airgapped


class RunnerTests(unittest.TestCase):
    def test_probe_blocks_socket_and_subprocess(self) -> None:
        result = run_airgapped(python_probe())
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["socket"].startswith("blocked:"))
        self.assertTrue(payload["subprocess"].startswith("blocked:"))

    def test_plain_python_still_runs(self) -> None:
        result = run_airgapped([sys.executable, "-c", "print(6 * 7)"])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "42")

    def test_timeout_is_machine_readable(self) -> None:
        result = run_airgapped([sys.executable, "-c", "import time; time.sleep(2)"], timeout=0.05)
        self.assertEqual(result.returncode, 124)
        self.assertTrue(result.timed_out)

    def test_cli_probe_is_machine_readable(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-m", "agentairgap", "--probe"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["timed_out"])
        probe = json.loads(payload["stdout"])
        self.assertTrue(probe["socket"].startswith("blocked:"))
        self.assertTrue(probe["subprocess"].startswith("blocked:"))


if __name__ == "__main__":
    unittest.main()
