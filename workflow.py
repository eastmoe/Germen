import glob
import subprocess
import sys
import time
from pathlib import Path
from threading import Event
from typing import Any, Callable, Dict, Optional

from app_config import PROJECT_ROOT, ensure_project_dirs, load_config, resolve_path
from log_utils import get_logger


logger = get_logger("germen.workflow", "main.log")
EventCallback = Optional[Callable[[str, Dict[str, Any]], None]]


def emit(callback: EventCallback, message: str, **payload: Any) -> None:
    logger.info(message)
    if callback:
        callback(message, payload)


def run_helper(script_name: str) -> None:
    subprocess.run([sys.executable, str(PROJECT_ROOT / script_name)], cwd=PROJECT_ROOT, check=True)


def find_latest_file(folder_path: str, file_type: str) -> Optional[str]:
    folder = resolve_path(folder_path)
    files = glob.glob(str(folder / file_type))
    if files:
        return max(files, key=lambda path: Path(path).stat().st_mtime)
    return None


def pin_foreground_window(callback: EventCallback = None) -> None:
    import win_input

    win_input.pin_foreground_window()
    emit(callback, "已置顶当前活动窗口。")


def run_capture(
    config: Optional[Dict[str, Any]] = None,
    stop_event: Optional[Event] = None,
    callback: EventCallback = None,
    pin_window: bool = False,
) -> int:
    import ImageGrab
    import OpenAIOCR

    config = config or load_config()
    ensure_project_dirs(config)
    stop_event = stop_event or Event()

    picture_dir = str(config["PictureDir"])
    ocr_dir = str(config["OCROutPaDir"])
    cycle = float(config.get("Cycle") or 10)
    total_pages = int(config.get("CapturePages") or 1)
    page_method = str(config.get("PageMethod") or "模拟按键")
    page_key = str(config.get("PageKey") or "n")

    if pin_window:
        emit(callback, "请在 3 秒内切换到模拟器/阅读器窗口，随后会置顶当前活动窗口。")
        time.sleep(3)
        pin_foreground_window(callback)

    click_module = None
    if page_method == "模拟点击":
        import Click

        click_module = Click
    else:
        import win_input

    captured = 0
    for page in range(1, total_pages + 1):
        if stop_event.is_set():
            emit(callback, "采集已停止。", page=page, total=total_pages)
            break

        emit(callback, f"开始采集第 {page}/{total_pages} 页。", page=page, total=total_pages)
        result = ImageGrab.GrabReadImage(picture_dir)
        if result == "Error":
            raise RuntimeError("截图失败，请检查截图保存目录和截图区域。")

        latest_image = find_latest_file(picture_dir, "*.png")
        if not latest_image:
            raise RuntimeError("没有找到刚刚保存的截图。")

        emit(callback, f"正在 OCR: {latest_image}", page=page, total=total_pages)
        text_path = OpenAIOCR.OCR(latest_image, ocr_dir, config)
        captured += 1
        emit(callback, f"OCR 完成: {text_path}", page=page, total=total_pages, text_path=text_path)

        if page < total_pages and not stop_event.is_set():
            if page_method == "模拟点击":
                click_module.ClickToNextPage()
                emit(callback, "已执行模拟点击翻页。", page=page, total=total_pages)
            else:
                win_input.press_and_release(page_key)
                emit(callback, f"已发送翻页按键: {page_key}", page=page, total=total_pages)

            end_at = time.time() + cycle
            while time.time() < end_at:
                if stop_event.is_set():
                    break
                time.sleep(0.1)

    emit(callback, f"采集结束，共完成 {captured} 页。", page=captured, total=total_pages)
    return captured


def merge_book(config: Optional[Dict[str, Any]] = None, callback: EventCallback = None) -> str:
    import TextMerge

    config = config or load_config()
    ensure_project_dirs(config)
    merge_dir = resolve_path(str(config["MergeBookDir"]))
    ocr_dir = str(config["OCROutPaDir"])
    output_path = merge_dir / f"{time.strftime('%Y-%m-%d-%H-%M-%S')}.txt"

    file_list = TextMerge.GetFileList(str(resolve_path(ocr_dir)))
    if file_list == "Error":
        raise RuntimeError("OCR 输出目录没有可合并的文本文件。")
    TextMerge.Merge(file_list, str(resolve_path(ocr_dir)), str(output_path))
    emit(callback, f"合并完成: {output_path}", merged_path=str(output_path))
    return str(output_path)


def format_book(
    merged_file: str,
    config: Optional[Dict[str, Any]] = None,
    callback: EventCallback = None,
) -> str:
    import FormatReplace

    config = config or load_config()
    ensure_project_dirs(config)
    final_dir = resolve_path(str(config["FinalNovelDir"]))
    output_path = final_dir / f"{time.strftime('%Y-%m-%d-%H-%M-%S')}.txt"

    FormatReplace.AddSpaceForParagraphs(merged_file, str(output_path))
    FormatReplace.UpdateFormat(str(output_path))
    emit(callback, f"格式化完成: {output_path}", final_path=str(output_path))
    return str(output_path)
