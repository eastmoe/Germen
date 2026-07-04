import time
import sys
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class InputSourceInfo:
    id: str
    name: str

    @property
    def label(self) -> str:
        return f"{self.name} (ID: {self.id})"


def _timestamped_png(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"{time.strftime('%Y-%m-%d-%H-%M-%S')}.png"


def parse_input_source(value: str) -> int | str:
    value = str(value or "0").strip()
    if value.isdigit():
        return int(value)
    id_match = re.search(r"\(ID:\s*(\d+)\)|\bID:\s*(\d+)\b", value, flags=re.IGNORECASE)
    if id_match:
        return int(next(group for group in id_match.groups() if group is not None))
    return value


def _opencv_import_error(action: str, exc: Exception) -> RuntimeError:
    python_path = sys.executable
    return RuntimeError(
        f"{action}需要 OpenCV，但当前 WebUI 使用的 Python 无法导入 cv2。\n"
        f"当前 Python: {python_path}\n"
        f"原始错误: {type(exc).__name__}: {exc}\n"
        f"请用已安装 OpenCV 的环境启动 WebUI，或执行: \"{python_path}\" -m pip install opencv-python"
    )


def capture_desktop_region(output_dir: Path) -> Path:
    from . import image_grab

    result = image_grab.GrabReadImage(str(output_dir))
    if result == "Error":
        raise RuntimeError("截图失败，请检查截图保存目录和截图区域。")
    if result:
        return Path(result)

    files = sorted(output_dir.glob("*.png"), key=lambda item: item.stat().st_mtime)
    if not files:
        raise RuntimeError("没有找到刚刚保存的截图。")
    return files[-1]


def capture_input_source(output_dir: Path, source: str = "0", warmup_frames: int = 5) -> Path:
    try:
        import cv2
    except Exception as exc:
        raise _opencv_import_error("使用图像输入源", exc) from exc

    capture = cv2.VideoCapture(parse_input_source(source), cv2.CAP_DSHOW)
    if not capture.isOpened():
        capture.release()
        raise RuntimeError(f"无法打开图像输入源: {source}")

    frame = None
    try:
        for _ in range(max(1, int(warmup_frames))):
            ok, candidate = capture.read()
            if ok:
                frame = candidate
        if frame is None:
            raise RuntimeError(f"无法从图像输入源读取画面: {source}")

        output_path = _timestamped_png(output_dir)
        if not cv2.imwrite(str(output_path), frame):
            raise RuntimeError(f"保存图像输入源画面失败: {output_path}")
        return output_path
    finally:
        capture.release()


def capture_frame(config: Dict[str, Any], output_dir: Path) -> Path:
    source_type = str(config.get("CaptureSource") or "屏幕区域")
    if source_type == "图像输入源":
        return capture_input_source(
            output_dir,
            str(config.get("InputSource") or "0"),
            int(config.get("InputSourceWarmupFrames") or 5),
        )
    return capture_desktop_region(output_dir)


def _windows_video_device_names() -> list[str]:
    if not sys.platform.startswith("win"):
        return []

    command = r"""
$devices = Get-CimInstance Win32_PnPEntity |
  Where-Object {
    $_.PNPClass -in @('Camera','Image') -or
    $_.Name -match 'camera|摄像|video|capture|采集'
  } |
  Select-Object Name, PNPDeviceID
$devices | ConvertTo-Json -Depth 2 -Compress
"""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
            check=False,
        )
    except Exception:
        return []
    if result.returncode != 0 or not result.stdout.strip():
        return []

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    if isinstance(data, dict):
        data = [data]

    names: list[str] = []
    seen: set[str] = set()
    for item in data if isinstance(data, list) else []:
        name = str(item.get("Name") or "").strip()
        if name and name not in seen:
            names.append(name)
            seen.add(name)
    return names


def list_input_source_details(max_index: int = 8) -> list[InputSourceInfo]:
    try:
        import cv2
    except Exception as exc:
        raise _opencv_import_error("扫描图像输入源", exc) from exc

    names = _windows_video_device_names()
    sources: list[InputSourceInfo] = []
    for index in range(max(1, int(max_index))):
        capture = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        try:
            if capture.isOpened():
                ok, _ = capture.read()
                if ok:
                    name = names[index] if index < len(names) else f"图像输入源 {index}"
                    sources.append(InputSourceInfo(str(index), name))
        finally:
            capture.release()
    return sources


def list_input_sources(max_index: int = 8) -> list[str]:
    return [source.id for source in list_input_source_details(max_index)]
