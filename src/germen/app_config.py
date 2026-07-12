import json
import os
import sys
from pathlib import Path
from typing import Any, Dict


DEFAULT_CONFIG: Dict[str, Any] = {
    "PictureDir": "./NovelPictures/",
    "OCROutPaDir": "./NovelOCRText/",
    "MergeBookDir": "./MergeText/",
    "FinalNovelDir": "./FinalBooks/",
    "Cycle": "10",
    "ReadingDelayMin": "5",
    "ReadingDelayMax": "45",
    "OCRBackend": "通用VLM路径",
    "OpenAIURL": "https://api.openai.com/v1",
    "OpenAIAPIKEY": "",
    "OpenAIOCRModel": "gpt-4.1-mini",
    "OpenAIRequestTimeout": "120",
    "OpenAIMaxOutputTokens": "4096",
    "OpenAIOCRPrompt": (
        "请对这张小说页面截图进行 OCR。只输出图片中可见的正文文本，保留自然换行，"
        "不要解释、不要总结、不要添加图片中不存在的内容。"
    ),
    "DedicatedOCRStripCoordinates": "true",
    "CaptureSource": "屏幕区域",
    "InputSource": "0",
    "InputSourceWarmupFrames": "5",
    "ADBSerial": "",
    "ADBTapX": "",
    "ADBTapY": "",
    "ADBLearnTimeout": "30",
    "PageMethod": "模拟按键",
    "PageKey": "n",
    "CapturePages": "100",
    "WebUIPassword": "germen",
}


def _resolve_project_root() -> Path:
    env_root = os.environ.get("GERMEN_HOME")
    if env_root:
        return Path(os.path.expandvars(os.path.expanduser(env_root))).resolve()

    source_root = Path(__file__).resolve().parents[2]
    if (source_root / "pyproject.toml").exists() and (source_root / "src" / "germen").is_dir():
        return source_root

    return Path.cwd().resolve()


PROJECT_ROOT = _resolve_project_root()
CONFIG_PATH = PROJECT_ROOT / "config.json"


def resource_path(relative: str | Path) -> Path:
    """Resolve a read-only bundled asset while keeping runtime data under PROJECT_ROOT."""
    relative_path = Path(relative)
    project_asset = PROJECT_ROOT / relative_path
    if project_asset.exists():
        return project_asset.resolve()

    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        return (Path(bundle_root) / relative_path).resolve()
    installed_asset = Path(sys.prefix) / relative_path
    if installed_asset.exists():
        return installed_asset.resolve()
    return project_asset.resolve()


def load_config(path: Path = CONFIG_PATH) -> Dict[str, Any]:
    if not path.exists():
        save_config(DEFAULT_CONFIG, path)
        return dict(DEFAULT_CONFIG)

    last_error = None
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            with path.open("r", encoding=encoding) as config_file:
                loaded = json.load(config_file)
            merged = dict(DEFAULT_CONFIG)
            merged.update(loaded)
            return merged
        except UnicodeDecodeError as exc:
            last_error = exc

    raise RuntimeError(f"无法读取配置文件 {path}: {last_error}")


def save_config(config: Dict[str, Any], path: Path = CONFIG_PATH) -> None:
    merged = dict(DEFAULT_CONFIG)
    merged.update(config)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as config_file:
        json.dump(merged, config_file, indent=4, ensure_ascii=False)
        config_file.write("\n")


def resolve_path(value: str) -> Path:
    expanded = os.path.expandvars(os.path.expanduser(value.strip()))
    path = Path(expanded)
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


def ensure_project_dirs(config: Dict[str, Any]) -> None:
    for key in ("PictureDir", "OCROutPaDir", "MergeBookDir", "FinalNovelDir"):
        resolve_path(str(config[key])).mkdir(parents=True, exist_ok=True)
