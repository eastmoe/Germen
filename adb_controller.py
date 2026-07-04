import queue
import re
import subprocess
import threading
import time
from dataclasses import dataclass
from typing import Dict, Optional, Tuple


class ADBError(RuntimeError):
    pass


@dataclass
class ADBDevice:
    serial: str
    state: str


def _adb_command(serial: str = "") -> list[str]:
    command = ["adb"]
    if serial:
        command.extend(["-s", serial])
    return command


def _run_adb(args: list[str], serial: str = "", timeout: float = 10) -> str:
    try:
        result = subprocess.run(
            [*_adb_command(serial), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        raise ADBError("未找到 adb，请确认 Android platform-tools 已加入 PATH。") from exc
    except subprocess.TimeoutExpired as exc:
        raise ADBError("adb 命令超时，请检查设备连接。") from exc

    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise ADBError(detail or f"adb 命令失败: {' '.join(args)}")
    return result.stdout.strip()


def list_devices() -> list[ADBDevice]:
    _run_adb(["start-server"], timeout=15)
    output = _run_adb(["devices"])
    devices: list[ADBDevice] = []
    for line in output.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2:
            devices.append(ADBDevice(parts[0], parts[1]))
    return devices


def resolve_serial(serial: str = "") -> str:
    serial = str(serial or "").strip()
    devices = [device for device in list_devices() if device.state == "device"]
    if serial:
        if any(device.serial == serial for device in devices):
            return serial
        raise ADBError(f"未找到已授权设备: {serial}")
    if not devices:
        raise ADBError("没有发现已授权的 ADB 设备，请开启 USB 调试并在手机上授权。")
    if len(devices) > 1:
        serials = ", ".join(device.serial for device in devices)
        raise ADBError(f"发现多台设备，请填写 ADB 序列号: {serials}")
    return devices[0].serial


def connect(serial: str = "") -> str:
    resolved = resolve_serial(serial)
    state = _run_adb(["get-state"], serial=resolved)
    if state != "device":
        raise ADBError(f"设备状态不是 device: {state}")
    return resolved


def keyevent(serial: str, key: str) -> None:
    resolved = resolve_serial(serial)
    _run_adb(["shell", "input", "keyevent", str(key)], serial=resolved)


def tap(serial: str, x: int, y: int) -> None:
    resolved = resolve_serial(serial)
    _run_adb(["shell", "input", "tap", str(int(x)), str(int(y))], serial=resolved)


def screen_size(serial: str) -> Tuple[int, int]:
    resolved = resolve_serial(serial)
    output = _run_adb(["shell", "wm", "size"], serial=resolved)
    match = re.search(r"Physical size:\s*(\d+)x(\d+)", output)
    if not match:
        match = re.search(r"Override size:\s*(\d+)x(\d+)", output)
    if not match:
        raise ADBError(f"无法解析屏幕尺寸: {output}")
    return int(match.group(1)), int(match.group(2))


def _touch_axis_ranges(serial: str) -> Dict[str, Dict[str, Tuple[int, int]]]:
    output = _run_adb(["shell", "getevent", "-p"], serial=serial)
    ranges: Dict[str, Dict[str, Tuple[int, int]]] = {}
    current_device = ""
    current_axis = ""

    for line in output.splitlines():
        device_match = re.search(r"add device \d+:\s+(\S+)", line)
        if device_match:
            current_device = device_match.group(1)
            ranges.setdefault(current_device, {})
            current_axis = ""
            continue

        axis_match = re.search(r"ABS_MT_POSITION_([XY])", line)
        if axis_match:
            current_axis = axis_match.group(1)
            continue

        if current_device and current_axis:
            range_match = re.search(r"min\s+(-?\d+),\s+max\s+(-?\d+)", line)
            if range_match:
                ranges[current_device][current_axis] = (
                    int(range_match.group(1)),
                    int(range_match.group(2)),
                )
                current_axis = ""

    return {
        device: axes
        for device, axes in ranges.items()
        if "X" in axes and "Y" in axes
    }


def _map_raw_to_screen(
    raw_x: int,
    raw_y: int,
    axis_range: Optional[Dict[str, Tuple[int, int]]],
    width: int,
    height: int,
) -> Tuple[int, int]:
    if not axis_range:
        return max(0, min(width - 1, raw_x)), max(0, min(height - 1, raw_y))

    min_x, max_x = axis_range["X"]
    min_y, max_y = axis_range["Y"]
    if max_x == min_x or max_y == min_y:
        return raw_x, raw_y

    x = round((raw_x - min_x) / (max_x - min_x) * (width - 1))
    y = round((raw_y - min_y) / (max_y - min_y) * (height - 1))
    return max(0, min(width - 1, x)), max(0, min(height - 1, y))


def learn_tap(serial: str = "", timeout: float = 30) -> Tuple[int, int]:
    resolved = resolve_serial(serial)
    width, height = screen_size(resolved)
    ranges = _touch_axis_ranges(resolved)
    command = [*_adb_command(resolved), "shell", "getevent", "-lt"]

    try:
        process = subprocess.Popen(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
        )
    except FileNotFoundError as exc:
        raise ADBError("未找到 adb，请确认 Android platform-tools 已加入 PATH。") from exc

    lines: queue.Queue[str] = queue.Queue()

    def reader() -> None:
        assert process.stdout is not None
        for item in process.stdout:
            lines.put(item)

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()

    last_by_device: Dict[str, Dict[str, int]] = {}
    selected_device = ""
    last_position_at = 0.0
    deadline = time.time() + float(timeout)

    try:
        while time.time() < deadline:
            try:
                line = lines.get(timeout=0.1)
            except queue.Empty:
                if selected_device and time.time() - last_position_at > 0.35:
                    break
                continue

            event_match = re.search(
                r"(/\S+):\s+EV_ABS\s+ABS_MT_POSITION_([XY])\s+([0-9a-fA-F]+)",
                line,
            )
            if event_match:
                device, axis, value = event_match.groups()
                last_by_device.setdefault(device, {})[axis] = int(value, 16)
                axes = last_by_device[device]
                if "X" in axes and "Y" in axes:
                    selected_device = device
                    last_position_at = time.time()
                continue

            if selected_device and "BTN_TOUCH" in line and "UP" in line:
                break
    finally:
        process.terminate()
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            process.kill()

    if not selected_device:
        raise ADBError("没有捕获到触摸坐标，请在监听期间点击一次手机阅读页。")

    raw = last_by_device[selected_device]
    axis_range = ranges.get(selected_device)
    return _map_raw_to_screen(raw["X"], raw["Y"], axis_range, width, height)
