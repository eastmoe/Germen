import time
from pathlib import Path
from typing import Any, Dict


def _timestamped_png(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"{time.strftime('%Y-%m-%d-%H-%M-%S')}.png"


def parse_input_source(value: str) -> int | str:
    value = str(value or "0").strip()
    if value.isdigit():
        return int(value)
    return value


def capture_desktop_region(output_dir: Path) -> Path:
    import ImageGrab

    result = ImageGrab.GrabReadImage(str(output_dir))
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
    except ImportError as exc:
        raise RuntimeError("使用图像输入源需要安装 opencv-python: pip install opencv-python") from exc

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


def list_input_sources(max_index: int = 8) -> list[str]:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("扫描图像输入源需要安装 opencv-python: pip install opencv-python") from exc

    sources: list[str] = []
    for index in range(max(1, int(max_index))):
        capture = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        try:
            if capture.isOpened():
                ok, _ = capture.read()
                if ok:
                    sources.append(str(index))
        finally:
            capture.release()
    return sources
