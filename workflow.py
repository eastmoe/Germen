import glob
import random
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


def random_reading_delay(config: Dict[str, Any]) -> tuple[float, float, float]:
    cycle = max(0.0, float(config.get("Cycle") or 0))
    minimum = max(0.0, float(config.get("ReadingDelayMin") or 0))
    maximum = max(0.0, float(config.get("ReadingDelayMax") or 0))
    if minimum > maximum:
        minimum, maximum = maximum, minimum
    jitter = random.uniform(minimum, maximum) if maximum > 0 or minimum > 0 else 0.0
    return cycle + jitter, cycle, jitter


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
    import OpenAIOCR
    import frame_sources

    config = config or load_config()
    ensure_project_dirs(config)
    stop_event = stop_event or Event()

    picture_dir = resolve_path(str(config["PictureDir"]))
    ocr_dir = str(config["OCROutPaDir"])
    random_reading_delay(config)
    total_pages = int(config.get("CapturePages") or 1)
    page_method = str(config.get("PageMethod") or "模拟按键")
    page_key = str(config.get("PageKey") or "n")
    capture_source = str(config.get("CaptureSource") or "屏幕区域")
    adb_serial = str(config.get("ADBSerial") or "").strip()

    if pin_window:
        emit(callback, "请在 3 秒内切换到模拟器/阅读器窗口，随后会置顶当前活动窗口。")
        time.sleep(3)
        pin_foreground_window(callback)

    click_module = None
    adb_module = None
    if page_method == "模拟点击":
        import Click

        click_module = Click
    elif page_method in ("音量下", "音量上", "ADB 模拟点击", "模拟点击学习"):
        import adb_controller

        adb_module = adb_controller
        adb_serial = adb_module.connect(adb_serial)
        config["ADBSerial"] = adb_serial
        emit(callback, f"ADB 已连接: {adb_serial}")
        if page_method in ("ADB 模拟点击", "模拟点击学习"):
            if not str(config.get("ADBTapX") or "").strip() or not str(config.get("ADBTapY") or "").strip():
                raise RuntimeError("还没有设置 ADB 点击坐标，请先手动填写、学习点击位置或从 ADB 截图点选。")
    else:
        import win_input

    emit(callback, f"采集来源: {capture_source}；翻页方式: {page_method}")
    captured = 0
    for page in range(1, total_pages + 1):
        if stop_event.is_set():
            emit(callback, "采集已停止。", page=page, total=total_pages)
            break

        emit(callback, f"开始采集第 {page}/{total_pages} 页。", page=page, total=total_pages)
        latest_image = frame_sources.capture_frame(config, picture_dir)

        emit(callback, f"正在 OCR: {latest_image}", page=page, total=total_pages)
        text_path = OpenAIOCR.OCR(str(latest_image), ocr_dir, config)
        captured += 1
        emit(callback, f"OCR 完成: {text_path}", page=page, total=total_pages, text_path=text_path)

        if page < total_pages and not stop_event.is_set():
            if page_method == "模拟点击":
                click_module.ClickToNextPage()
                emit(callback, "已执行模拟点击翻页。", page=page, total=total_pages)
            elif page_method == "音量下":
                adb_module.keyevent(adb_serial, "KEYCODE_VOLUME_DOWN")
                emit(callback, "已发送 ADB 音量下翻页。", page=page, total=total_pages)
            elif page_method == "音量上":
                adb_module.keyevent(adb_serial, "KEYCODE_VOLUME_UP")
                emit(callback, "已发送 ADB 音量上翻页。", page=page, total=total_pages)
            elif page_method in ("ADB 模拟点击", "模拟点击学习"):
                adb_module.tap(adb_serial, int(config["ADBTapX"]), int(config["ADBTapY"]))
                emit(callback, f"已执行 ADB 点击翻页: {config['ADBTapX']}, {config['ADBTapY']}", page=page, total=total_pages)
            else:
                win_input.press_and_release(page_key)
                emit(callback, f"已发送翻页按键: {page_key}", page=page, total=total_pages)

            wait_seconds, cycle_seconds, jitter_seconds = random_reading_delay(config)
            emit(
                callback,
                f"等待 {wait_seconds:.1f} 秒后继续（基础 {cycle_seconds:.1f} 秒，阅读误差 {jitter_seconds:.1f} 秒）。",
                page=page,
                total=total_pages,
                wait_seconds=wait_seconds,
                reading_delay=jitter_seconds,
            )
            end_at = time.time() + wait_seconds
            while time.time() < end_at:
                if stop_event.is_set():
                    break
                time.sleep(0.1)

    emit(callback, f"采集结束，共完成 {captured} 页。", page=captured, total=total_pages)
    return captured


def connect_adb(config: Optional[Dict[str, Any]] = None, callback: EventCallback = None) -> str:
    import adb_controller

    config = config or load_config()
    serial = adb_controller.connect(str(config.get("ADBSerial") or ""))
    emit(callback, f"ADB 已连接: {serial}", adb_serial=serial)
    return serial


def learn_adb_tap(config: Optional[Dict[str, Any]] = None, callback: EventCallback = None) -> Dict[str, int]:
    import adb_controller

    config = config or load_config()
    serial = adb_controller.connect(str(config.get("ADBSerial") or ""))
    timeout = float(config.get("ADBLearnTimeout") or 30)
    emit(callback, f"ADB 监听已开启，请在 {int(timeout)} 秒内点击手机上的下一页区域。")
    x, y = adb_controller.learn_tap(serial, timeout)
    emit(callback, f"已学习 ADB 点击坐标: {x}, {y}", adb_serial=serial, x=x, y=y)
    return {"x": x, "y": y}


def capture_adb_screenshot(config: Optional[Dict[str, Any]] = None, callback: EventCallback = None) -> Dict[str, Any]:
    import adb_controller
    from PIL import Image

    config = config or load_config()
    serial = adb_controller.connect(str(config.get("ADBSerial") or ""))
    target = PROJECT_ROOT / "static" / "adb_screen.png"
    image_path = adb_controller.screencap(serial, target)
    with Image.open(image_path) as image:
        width, height = image.size
    emit(callback, f"ADB 截屏完成: {image_path}", adb_serial=serial, path=str(image_path), width=width, height=height)
    return {"path": str(image_path), "serial": serial, "width": width, "height": height}


def list_adb_devices() -> list[Dict[str, str]]:
    import adb_controller

    return [
        {
            "serial": device.serial,
            "state": device.state,
            "name": device.name or "未知设备",
            "label": device.label,
        }
        for device in adb_controller.list_devices()
    ]


def list_input_source_details(max_index: int = 8) -> list[Dict[str, str]]:
    import frame_sources

    return [
        {"id": source.id, "name": source.name, "label": source.label}
        for source in frame_sources.list_input_source_details(max_index)
    ]


def list_input_sources(max_index: int = 8) -> list[str]:
    import frame_sources

    return frame_sources.list_input_sources(max_index)


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
