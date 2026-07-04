import json
from pathlib import Path
from typing import Dict

from .app_config import PROJECT_ROOT


DATA_DIR = PROJECT_ROOT / "data"
IMAGE_PLOT_PATH = DATA_DIR / "ImagePlot.json"
CLICK_PLOT_PATH = DATA_DIR / "ClickPlot.json"


def _read_json(path: Path) -> Dict[str, int]:
    if not path.exists():
        raise FileNotFoundError(f"坐标文件不存在: {path}")
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return {key: int(value) for key, value in data.items()}


def _write_json(path: Path, data: Dict[str, int]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump({key: int(value) for key, value in data.items()}, file, indent=4, ensure_ascii=False)
        file.write("\n")


def load_image_plot() -> Dict[str, int]:
    data = _read_json(IMAGE_PLOT_PATH)
    required = {"xstart", "ystart", "xend", "yend"}
    missing = required.difference(data)
    if missing:
        raise ValueError(f"截图区域坐标缺少字段: {', '.join(sorted(missing))}")
    return data


def save_image_plot(xstart: int, ystart: int, xend: int, yend: int) -> None:
    left, right = sorted((xstart, xend))
    top, bottom = sorted((ystart, yend))
    if left == right or top == bottom:
        raise ValueError("截图区域宽度或高度为 0，请重新框选。")
    _write_json(IMAGE_PLOT_PATH, {"xstart": left, "ystart": top, "xend": right, "yend": bottom})


def load_click_plot() -> Dict[str, int]:
    data = _read_json(CLICK_PLOT_PATH)
    required = {"x", "y"}
    missing = required.difference(data)
    if missing:
        raise ValueError(f"点击坐标缺少字段: {', '.join(sorted(missing))}")
    return data


def save_click_plot(x: int, y: int) -> None:
    _write_json(CLICK_PLOT_PATH, {"x": x, "y": y})
