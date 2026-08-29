"""Exercise the control panel's real demo and test actions offscreen."""

from __future__ import annotations

from collections.abc import Callable
import json

from PySide6.QtCore import QEventLoop, QProcess, QTimer
from PySide6.QtWidgets import QApplication

from project_gui import ControlPanel


def run_action(app: QApplication, action: Callable[[ControlPanel], None]) -> str:
    panel = ControlPanel()
    loop = QEventLoop()
    timed_out = False

    def timeout() -> None:
        nonlocal timed_out
        timed_out = True
        panel.stop()
        loop.quit()

    timer = QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(timeout)
    panel.process.finished.connect(loop.quit)
    action(panel)
    timer.start(15_000)
    loop.exec()
    timer.stop()
    app.processEvents()

    assert not timed_out, panel.output.toPlainText()
    assert panel.process.state() == QProcess.NotRunning
    assert panel.status.text() == "Finished with exit code 0", panel.status.text()
    output = panel.output.toPlainText()
    panel.close()
    return output


def main() -> None:
    app = QApplication([])

    demo = run_action(app, lambda panel: panel.run_demo())
    payload = json.loads(demo[demo.index("{") :])
    assert payload["returncode"] == 0, payload
    probe = json.loads(payload["stdout"])
    assert probe["socket"].startswith("blocked:"), probe
    assert probe["subprocess"].startswith("blocked:"), probe

    tests = run_action(app, lambda panel: panel.run_tests())
    assert "Ran 4 tests" in tests, tests
    assert "AgentAirgap tests and enforcement probe passed." in tests, tests
    print("AgentAirgap GUI demo and test actions passed.")


if __name__ == "__main__":
    main()
