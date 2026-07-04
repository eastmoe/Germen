import os
import queue
import threading
import traceback
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk

from app_config import DEFAULT_CONFIG, load_config, resolve_path, save_config
import workflow


class GermenGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Germen OCR")
        self.geometry("760x680")
        self.minsize(720, 640)

        self.config_data = load_config()
        self.queue: queue.Queue = queue.Queue()
        self.worker: threading.Thread | None = None
        self.stop_event = threading.Event()
        self.last_merged_file = ""

        self.vars = {
            key: tk.StringVar(value=str(self.config_data.get(key, DEFAULT_CONFIG.get(key, ""))))
            for key in DEFAULT_CONFIG
        }
        self.pin_window_var = tk.BooleanVar(value=False)

        self._build_ui()
        self._poll_queue()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        config_frame = ttk.LabelFrame(self, text="路径与 OpenAI 配置")
        config_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        config_frame.columnconfigure(1, weight=1)

        path_fields = [
            ("截图保存目录", "PictureDir"),
            ("OCR 文本目录", "OCROutPaDir"),
            ("合并文本目录", "MergeBookDir"),
            ("最终小说目录", "FinalNovelDir"),
        ]
        for row, (label, key) in enumerate(path_fields):
            ttk.Label(config_frame, text=label).grid(row=row, column=0, sticky="w", padx=8, pady=5)
            ttk.Entry(config_frame, textvariable=self.vars[key]).grid(
                row=row, column=1, sticky="ew", padx=8, pady=5
            )
            ttk.Button(config_frame, text="浏览", command=lambda item=key: self._choose_dir(item)).grid(
                row=row, column=2, padx=8, pady=5
            )

        api_fields = [
            ("OpenAI Base URL", "OpenAIURL"),
            ("OpenAI API Key", "OpenAIAPIKEY"),
            ("OCR 模型", "OpenAIOCRModel"),
            ("请求超时秒", "OpenAIRequestTimeout"),
            ("最大输出 tokens", "OpenAIMaxOutputTokens"),
        ]
        for offset, (label, key) in enumerate(api_fields, start=len(path_fields)):
            ttk.Label(config_frame, text=label).grid(row=offset, column=0, sticky="w", padx=8, pady=5)
            show = "*" if key == "OpenAIAPIKEY" else ""
            ttk.Entry(config_frame, textvariable=self.vars[key], show=show).grid(
                row=offset, column=1, columnspan=2, sticky="ew", padx=8, pady=5
            )

        prompt_row = len(path_fields) + len(api_fields)
        ttk.Label(config_frame, text="OCR 提示词").grid(row=prompt_row, column=0, sticky="nw", padx=8, pady=5)
        self.prompt_text = tk.Text(config_frame, height=3, wrap="word")
        self.prompt_text.insert("1.0", self.vars["OpenAIOCRPrompt"].get())
        self.prompt_text.grid(row=prompt_row, column=1, columnspan=2, sticky="ew", padx=8, pady=5)

        capture_frame = ttk.LabelFrame(self, text="采集控制")
        capture_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=8)
        for col in range(8):
            capture_frame.columnconfigure(col, weight=1)

        ttk.Label(capture_frame, text="翻页方式").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        method_box = ttk.Combobox(
            capture_frame,
            values=("模拟按键", "模拟点击"),
            textvariable=self.vars["PageMethod"],
            state="readonly",
            width=12,
        )
        method_box.grid(row=0, column=1, sticky="ew", padx=8, pady=6)

        ttk.Label(capture_frame, text="按键").grid(row=0, column=2, sticky="e", padx=8, pady=6)
        ttk.Entry(capture_frame, textvariable=self.vars["PageKey"], width=10).grid(
            row=0, column=3, sticky="w", padx=8, pady=6
        )

        ttk.Label(capture_frame, text="页数").grid(row=0, column=4, sticky="e", padx=8, pady=6)
        ttk.Entry(capture_frame, textvariable=self.vars["CapturePages"], width=10).grid(
            row=0, column=5, sticky="w", padx=8, pady=6
        )

        ttk.Label(capture_frame, text="周期秒").grid(row=0, column=6, sticky="e", padx=8, pady=6)
        ttk.Entry(capture_frame, textvariable=self.vars["Cycle"], width=10).grid(
            row=0, column=7, sticky="w", padx=8, pady=6
        )

        ttk.Checkbutton(
            capture_frame,
            text="开始前 3 秒置顶当前活动窗口",
            variable=self.pin_window_var,
        ).grid(row=1, column=0, columnspan=3, sticky="w", padx=8, pady=6)

        ttk.Button(capture_frame, text="选择截图区域", command=self._select_image_area).grid(
            row=1, column=3, sticky="ew", padx=8, pady=6
        )
        ttk.Button(capture_frame, text="选择点击坐标", command=self._select_click_point).grid(
            row=1, column=4, sticky="ew", padx=8, pady=6
        )
        ttk.Button(capture_frame, text="保存配置", command=self._save_config_from_ui).grid(
            row=1, column=5, sticky="ew", padx=8, pady=6
        )
        ttk.Button(capture_frame, text="清空 OCR 文本", command=self._clear_ocr_text).grid(
            row=1, column=6, columnspan=2, sticky="ew", padx=8, pady=6
        )

        action_frame = ttk.Frame(self)
        action_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=8)
        for col in range(6):
            action_frame.columnconfigure(col, weight=1)

        self.start_button = ttk.Button(action_frame, text="开始采集", command=self._start_capture)
        self.stop_button = ttk.Button(action_frame, text="停止采集", command=self._stop_capture, state="disabled")
        self.merge_button = ttk.Button(action_frame, text="合并文本", command=self._start_merge)
        self.format_button = ttk.Button(action_frame, text="格式化", command=self._start_format)
        self.auto_button = ttk.Button(action_frame, text="一键采集并生成", command=self._start_auto)
        self.open_config_button = ttk.Button(action_frame, text="打开配置文件", command=self._open_config_file)

        for col, button in enumerate(
            [
                self.start_button,
                self.stop_button,
                self.merge_button,
                self.format_button,
                self.auto_button,
                self.open_config_button,
            ]
        ):
            button.grid(row=0, column=col, sticky="ew", padx=4)

        log_frame = ttk.LabelFrame(self, text="运行日志")
        log_frame.grid(row=3, column=0, sticky="nsew", padx=12, pady=(8, 12))
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap="word", height=12)
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self.progress = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(log_frame, variable=self.progress, maximum=100)
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))

    def _choose_dir(self, key: str) -> None:
        selected = filedialog.askdirectory(initialdir=str(resolve_path(self.vars[key].get())))
        if selected:
            self.vars[key].set(selected)

    def _read_ui_config(self) -> dict:
        config = {key: var.get() for key, var in self.vars.items()}
        config["OpenAIOCRPrompt"] = self.prompt_text.get("1.0", "end").strip()
        return config

    def _save_config_from_ui(self) -> dict:
        config = self._read_ui_config()
        save_config(config)
        self.config_data = config
        self._log("配置已保存。")
        return config

    def _select_image_area(self) -> None:
        self._start_background("选择截图区域", lambda: workflow.run_helper("GetNovelImagePlot.py"))

    def _select_click_point(self) -> None:
        self._start_background("选择点击坐标", lambda: workflow.run_helper("GetClickPlot.py"))

    def _open_config_file(self) -> None:
        os.startfile("config.json")

    def _clear_ocr_text(self) -> None:
        if not messagebox.askyesno("确认", "确认删除 OCR 文本目录里的所有 txt 文件吗？"):
            return
        ocr_dir = resolve_path(self.vars["OCROutPaDir"].get())
        deleted = 0
        for txt_file in ocr_dir.glob("*.txt"):
            txt_file.unlink()
            deleted += 1
        self._log(f"已删除 {deleted} 个 OCR 文本文件。")

    def _start_capture(self) -> None:
        config = self._save_config_from_ui()
        self.stop_event.clear()
        self._start_background(
            "采集",
            lambda: workflow.run_capture(
                config,
                stop_event=self.stop_event,
                callback=self._worker_callback,
                pin_window=self.pin_window_var.get(),
            ),
            capture_mode=True,
        )

    def _stop_capture(self) -> None:
        self.stop_event.set()
        self._log("已请求停止，当前页处理结束后会退出。")

    def _start_merge(self) -> None:
        config = self._save_config_from_ui()

        def task() -> None:
            self.last_merged_file = workflow.merge_book(config, self._worker_callback)

        self._start_background("合并文本", task)

    def _start_format(self) -> None:
        config = self._save_config_from_ui()
        merged_file = self.last_merged_file
        if not merged_file:
            merge_dir = resolve_path(config["MergeBookDir"])
            files = sorted(merge_dir.glob("*.txt"), key=lambda item: item.stat().st_mtime)
            merged_file = str(files[-1]) if files else ""
        if not merged_file:
            messagebox.showerror("缺少合并文本", "请先合并文本，或确认合并文本目录内已有 txt 文件。")
            return

        self._start_background(
            "格式化",
            lambda: workflow.format_book(merged_file, config, self._worker_callback),
        )

    def _start_auto(self) -> None:
        config = self._save_config_from_ui()
        self.stop_event.clear()

        def task() -> None:
            workflow.run_capture(
                config,
                stop_event=self.stop_event,
                callback=self._worker_callback,
                pin_window=self.pin_window_var.get(),
            )
            if self.stop_event.is_set():
                return
            self.last_merged_file = workflow.merge_book(config, self._worker_callback)
            workflow.format_book(self.last_merged_file, config, self._worker_callback)

        self._start_background("一键采集并生成", task, capture_mode=True)

    def _start_background(self, name: str, target, capture_mode: bool = False) -> None:
        if self.worker and self.worker.is_alive():
            messagebox.showwarning("任务运行中", "已有任务正在运行，请等待完成或先停止采集。")
            return

        self._set_busy(True, capture_mode)
        self._log(f"{name}开始。")

        def runner() -> None:
            try:
                target()
                self.queue.put(("done", f"{name}完成。", None))
            except Exception as exc:
                self.queue.put(("error", f"{name}失败: {exc}", traceback.format_exc()))

        self.worker = threading.Thread(target=runner, daemon=True)
        self.worker.start()

    def _worker_callback(self, message: str, payload: dict) -> None:
        self.queue.put(("event", message, payload))

    def _poll_queue(self) -> None:
        while True:
            try:
                kind, message, payload = self.queue.get_nowait()
            except queue.Empty:
                break

            self._log(message)
            if kind == "event" and payload:
                total = payload.get("total")
                page = payload.get("page")
                if total and page is not None:
                    self.progress.set(min(100, max(0, page / total * 100)))
            elif kind == "error":
                self._log(payload or "")
                self._set_busy(False)
                messagebox.showerror("任务失败", message)
            elif kind == "done":
                self._set_busy(False)

        self.after(150, self._poll_queue)

    def _set_busy(self, busy: bool, capture_mode: bool = False) -> None:
        state = "disabled" if busy else "normal"
        self.start_button.configure(state=state)
        self.merge_button.configure(state=state)
        self.format_button.configure(state=state)
        self.auto_button.configure(state=state)
        self.stop_button.configure(state="normal" if busy and capture_mode else "disabled")

    def _log(self, message: str) -> None:
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")


if __name__ == "__main__":
    GermenGUI().mainloop()
