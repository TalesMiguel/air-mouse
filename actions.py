import subprocess
import sys
import time
from pynput.mouse import Controller as MouseController

_mouse = MouseController()
_last_action_time: dict[str, float] = {}


def scroll(delta: float, sensitivity: float = 1.0) -> None:
    amount = delta * sensitivity
    _mouse.scroll(0, amount)


def _debounced(key: str, cooldown: float) -> bool:
    now = time.time()
    if now - _last_action_time.get(key, 0) < cooldown:
        return False
    _last_action_time[key] = now
    return True


def minimize_window() -> None:
    if not _debounced("minimize", 1.0):
        return
    if sys.platform.startswith("linux"):
        subprocess.run(["xdotool", "key", "super+Down"], check=False)
    elif sys.platform == "win32":
        subprocess.run(["powershell", "-Command",
                        "(New-Object -ComObject Shell.Application).MinimizeAll()"], check=False)


def close_window() -> None:
    if not _debounced("close", 2.0):
        return
    if sys.platform.startswith("linux"):
        subprocess.run(["xdotool", "key", "alt+F4"], check=False)
    elif sys.platform == "win32":
        subprocess.run(["powershell", "-Command",
                        "Add-Type -AssemblyName Microsoft.VisualBasic; "
                        "[Microsoft.VisualBasic.Interaction]::AppActivate((Get-Process | "
                        "Where-Object {$_.MainWindowHandle -ne 0} | Select-Object -First 1).Id)"],
                       check=False)
        subprocess.run(["powershell", "-Command",
                        "$wshell = New-Object -ComObject wscript.shell; $wshell.SendKeys('%{F4}')"],
                       check=False)
