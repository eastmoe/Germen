import os
import queue
import threading
import traceback
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk

from . import workflow
from .app_config import DEFAULT_CONFIG, PROJECT_ROOT, load_config, resolve_path, resource_path, save_config


class GermenGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Germen OCR")
        logo_path = resource_path("static/logo.png")
        self.logo_image = tk.PhotoImage(file=str(logo_path)) if logo_path.exists() else None
        self.home_logo_image = self.logo_image.subsample(8, 8) if self.logo_image else None
        if self.logo_image:
            self.iconphoto(True, self.logo_image)
        self.geometry("940x820")
        self.minsize(880, 760)

        self.config_data = load_config()
        self.queue: queue.Queue = queue.Queue()
        self.worker: threading.Thread | None = None
        self.stop_event = threading.Event()
        self.last_merged_file = ""
        self.preview_window = None
        self.preview_label = None
        self.preview_capture = None
        self.preview_photo = None
        self.preview_after_id = None
        self.preview_source = ""
        self.adb_picker_window = None
        self.adb_picker_photo = None
        self.adb_picker_scale = 1.0

        self.vars = {
            key: tk.StringVar(value=str(self.config_data.get(key, DEFAULT_CONFIG.get(key, ""))))
            for key in DEFAULT_CONFIG
        }
        self.input_source_var = tk.StringVar(value=self.vars["InputSource"].get())
        self.input_source_display_to_id: dict[str, str] = {}
        self.adb_device_var = tk.StringVar(value=self.vars["ADBSerial"].get())
        self.adb_display_to_serial: dict[str, str] = {}
        self.pin_window_var = tk.BooleanVar(value=False)

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build_ui()
        self._poll_queue()

    def _build_ui(self) -> None:
        self.geometry("920x720")
        self.minsize(900, 680)
        self.option_add("*Font", ("Microsoft YaHei UI", 10))
        self._configure_styles()

        self.help_text = {
            "SetupMode": "选择最接近你的实际使用方式。高级用户可选择“自定义组合”。",
            "OCRBackend": "OCR模型会负责从图片中提取文字，通用 VLM 适合 OpenAI 等支持读取图片的 AI 大语言视觉模型；专用 OCR 适合只接收图片的专业图片文字提取服务。",
            "OpenAIURL": "OCR 服务的 API 根地址。OpenAI 官方通常是 https://api.openai.com/v1，本地服务常见为 http://127.0.0.1:8080/v1。",
            "OpenAIAPIKEY": "OCR 服务的访问密钥。本地服务不要求密钥时可以留空。",
            "OpenAIOCRModel": "服务端暴露的模型名称，必须与服务实际支持的名称一致。",
            "OpenAIRequestTimeout": "单页 OCR 最长等待时间，单位为秒。网络较慢或本地模型首次加载时可适当增大。",
            "OpenAIMaxOutputTokens": "单页允许返回的最大文本长度。页面文字被截断时可以调大。",
            "OpenAIOCRPrompt": "告诉通用视觉模型如何识别正文。专用 OCR 路径会自动忽略此项。",
            "CaptureSource": "Germen获取小说图片的方式。屏幕区域直接截取电脑画面；图像输入源用于摄像头、采集卡或网络视频流。",
            "InputSource": "本地设备可填写 0、1 等编号；网络源可填写 HTTP、RTSP 等完整地址。",
            "InputSourceWarmupFrames": "正式保存前丢弃的画面帧数，用于等待摄像头曝光稳定。网络流响应慢时不宜设置过大。",
            "PageMethod": "每页 OCR 完成后如何翻到下一页。向导会根据使用场景只提供适用方式。",
            "PageKey": "模拟器中映射为下一页的键，例如 n、right 或 pagedown。",
            "ADBSerial": "安卓设备序列号。只有一台已授权 ADB 设备时可留空并自动识别。",
            "ADBTapX": "使用USB调试功能点击翻页时，下一页区域在设备原始分辨率中的横坐标。",
            "ADBTapY": "使用USB调试功能点击翻页时，下一页区域在设备原始分辨率中的纵坐标。",
            "CapturePages": "本次计划识别的总页数。需要查看你的小说显示的总页数，可在运行中点击停止。",
            "Cycle": "完成翻页后的固定等待时间，单位为秒。应足够让下一页完全显示。",
            "ReadingDelayMin": "模拟人类的随机性行为。每次翻页额外随机等待的最小秒数；设为 0 可减少等待。",
            "ReadingDelayMax": "模拟人类的随机性行为。每次翻页额外随机等待的最大秒数；程序会在最小值与最大值之间随机选择。",
            "PinWindow": "开始后留出 3 秒切换到模拟器，再把当前活动窗口置顶。仅电脑模拟器场景通常需要。",
            "PictureDir": "保存每一页原始截图的目录。",
            "OCROutPaDir": "保存每一页文本的目录。",
            "MergeBookDir": "保存按顺序合并后的完整文本。",
            "FinalNovelDir": "保存最终格式化小说文本的目录。",
        }
        self.setup_mode_var = tk.StringVar(value=self._infer_setup_mode())
        self.current_page = 0
        self.page_frames: list[ttk.Frame] = []

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        header = ttk.Frame(self, style="Header.TFrame", padding=(30, 20))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="GERMEN", style="Brand.TLabel").grid(row=0, column=0, sticky="w")
        self.step_label = ttk.Label(header, text="", style="Step.TLabel")
        self.step_label.grid(row=0, column=1, sticky="e")

        self.page_host = ttk.Frame(self, padding=(30, 24))
        self.page_host.grid(row=1, column=0, sticky="nsew")
        self.page_host.columnconfigure(0, weight=1)
        self.page_host.rowconfigure(0, weight=1)

        self.footer = ttk.Frame(self, padding=(30, 14))
        self.footer.grid(row=2, column=0, sticky="ew")
        self.footer.columnconfigure(1, weight=1)
        self.back_button = ttk.Button(self.footer, text="上一步", command=self._previous_page)
        self.back_button.grid(row=0, column=0, sticky="w")
        self.home_button = ttk.Button(self.footer, text="返回首页", command=lambda: self._show_page(0))
        self.home_button.grid(row=0, column=1)
        self.next_button = ttk.Button(self.footer, text="下一步", style="Accent.TButton", command=self._next_page)
        self.next_button.grid(row=0, column=2, sticky="e")

        self._build_home_page()
        self._build_mode_page()
        self._build_ocr_page()
        self._build_capture_page()
        self._build_output_page()
        self._build_run_page()
        self._apply_ocr_backend_defaults(initial=True)
        self._show_page(0)

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Header.TFrame", background="#f3f6f8")
        style.configure("Brand.TLabel", background="#f3f6f8", foreground="#174a5b", font=("Segoe UI Semibold", 15))
        style.configure("Step.TLabel", background="#f3f6f8", foreground="#5c6870")
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 22, "bold"), foreground="#17242a")
        style.configure("Subtitle.TLabel", foreground="#5c6870", font=("Microsoft YaHei UI", 10))
        style.configure("Accent.TButton", font=("Microsoft YaHei UI", 10, "bold"))
        style.configure("Mode.TRadiobutton", font=("Microsoft YaHei UI", 11, "bold"), padding=8)
        style.configure("Help.TButton", padding=(5, 1), font=("Segoe UI", 9, "bold"))

    def _new_page(self, title: str, subtitle: str) -> tuple[ttk.Frame, ttk.Frame]:
        page = ttk.Frame(self.page_host)
        page.grid(row=0, column=0, sticky="nsew")
        page.columnconfigure(0, weight=1)
        ttk.Label(page, text=title, style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(page, text=subtitle, style="Subtitle.TLabel", wraplength=760).grid(row=1, column=0, sticky="w", pady=(6, 22))
        body = ttk.Frame(page)
        body.grid(row=2, column=0, sticky="nsew")
        body.columnconfigure(1, weight=1)
        page.rowconfigure(2, weight=1)
        self.page_frames.append(page)
        return page, body

    def _help_button(self, parent, key: str) -> ttk.Button:
        return ttk.Button(parent, text="?", width=2, style="Help.TButton", command=lambda: self._show_help(key))

    def _show_help(self, key: str) -> None:
        messagebox.showinfo("配置说明", self.help_text.get(key, "暂无详细说明。"), parent=self)

    def _field(self, parent, row: int, label: str, key: str, *, show: str = "", browse: bool = False, width: int = 28):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=8)
        widget = ttk.Entry(parent, textvariable=self.vars[key], show=show, width=width)
        widget.grid(row=row, column=1, sticky="ew", padx=(14, 8), pady=8)
        self._help_button(parent, key).grid(row=row, column=2, padx=(0, 8), pady=8)
        if browse:
            ttk.Button(parent, text="浏览…", command=lambda: self._choose_dir(key)).grid(row=row, column=3, pady=8)
        return widget

    def _combo_field(self, parent, row: int, label: str, key: str, values: tuple[str, ...], command=None):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=8)
        widget = ttk.Combobox(parent, values=values, textvariable=self.vars[key], state="readonly")
        widget.grid(row=row, column=1, sticky="ew", padx=(14, 8), pady=8)
        self._help_button(parent, key).grid(row=row, column=2, padx=(0, 8), pady=8)
        if command:
            widget.bind("<<ComboboxSelected>>", command)
        return widget

    def _build_home_page(self) -> None:
        page, body = self._new_page("把小说页面变成可整理的文本", "跟随向导完成设置。")
        intro = ttk.Frame(body, padding=(0, 12))
        intro.grid(row=0, column=0, columnspan=3, sticky="nsew")
        intro.columnconfigure(0, weight=1)
        if self.home_logo_image:
            ttk.Label(intro, image=self.home_logo_image).grid(row=0, column=1, rowspan=6, sticky="ne", padx=(30, 20))
        ttk.Label(intro, text="首次使用", font=("Microsoft YaHei UI", 12, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(intro, text="选择设备方式、连接AI模型、确认翻页，然后即可开始。", foreground="#5c6870").grid(row=1, column=0, sticky="w", pady=(4, 14))
        ttk.Button(intro, text="开始设置", style="Accent.TButton", command=lambda: self._show_page(1)).grid(row=2, column=0, sticky="w")
        ttk.Separator(intro).grid(row=3, column=0, sticky="ew", pady=24)
        ttk.Label(intro, text="已有配置", font=("Microsoft YaHei UI", 12, "bold")).grid(row=4, column=0, sticky="w")
        actions = ttk.Frame(intro)
        actions.grid(row=5, column=0, sticky="w", pady=(12, 0))
        ttk.Button(actions, text="直接进入运行页", command=lambda: self._show_page(5)).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="打开配置文件", command=self._open_config_file).pack(side="left", padx=8)

    def _infer_setup_mode(self) -> str:
        source = self.vars["CaptureSource"].get()
        method = self.vars["PageMethod"].get()
        if source == "屏幕区域" and method in ("模拟按键", "模拟点击"):
            return "电脑 + 安卓模拟器（推荐）"
        if source == "图像输入源" and method in ("音量下", "音量上", "ADB 模拟点击", "模拟点击学习"):
            return "摄像头/采集卡/网络视频 + ADB 设备"
        return "自定义组合（高级）"

    def _build_mode_page(self) -> None:
        page, body = self._new_page("你准备怎样获取小说阅读界面的图片？", "选择最接近的场景。后续页面会自动隐藏视频源或 ADB 等无关设置。")
        choices = (
            ("电脑 + 安卓模拟器（推荐）", "截取电脑上的安卓模拟器画面，并用键盘或鼠标翻页。"),
            ("摄像头/采集卡/网络视频 + ADB 设备", "从视频画面取图，通过 USB 或网络 ADB 控制实体安卓设备翻页。"),
            ("自定义组合（高级）", "自行组合屏幕/视频采集和所有翻页方式。"),
        )
        for row, (value, description) in enumerate(choices):
            card = ttk.Frame(body, padding=(12, 8))
            card.grid(row=row, column=0, columnspan=3, sticky="ew", pady=4)
            card.columnconfigure(0, weight=1)
            ttk.Radiobutton(card, text=value, value=value, variable=self.setup_mode_var, style="Mode.TRadiobutton").grid(row=0, column=0, sticky="w")
            ttk.Label(card, text=description, foreground="#5c6870", wraplength=700).grid(row=1, column=0, sticky="w", padx=30)
        self._help_button(body, "SetupMode").grid(row=3, column=0, sticky="w", pady=(14, 0))

    def _build_ocr_page(self) -> None:
        page, body = self._new_page("连接图像文字提取服务", "Germen 会把每页图片发送到这个服务。常用设置在上方，高级参数放在可展开区域。")
        self._combo_field(body, 0, "OCR 类型", "OCRBackend", ("通用VLM路径", "专用OCR路径"), lambda _event: self._apply_ocr_backend_defaults())
        self._field(body, 1, "服务地址", "OpenAIURL")
        self._field(body, 2, "API Key", "OpenAIAPIKEY", show="•")
        self._field(body, 3, "模型名称", "OpenAIOCRModel")
        self.ocr_advanced_visible = False
        self.ocr_advanced_button = ttk.Button(body, text="显示高级设置", command=self._toggle_ocr_advanced)
        self.ocr_advanced_button.grid(row=4, column=0, sticky="w", pady=(14, 0))
        self.ocr_test_button = ttk.Button(body, text="测试 OCR 服务", style="Accent.TButton", command=self._test_ocr_service)
        self.ocr_test_button.grid(row=4, column=1, sticky="e", padx=(14, 8), pady=(14, 0))
        self.ocr_test_status = ttk.Label(body, text="", foreground="#5c6870", wraplength=760)
        self.ocr_test_status.grid(row=6, column=0, columnspan=3, sticky="w", pady=(12, 4))
        self.ocr_test_result = tk.Text(body, height=5, wrap="word", relief="solid", borderwidth=1, state="disabled")
        self.ocr_test_result.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(0, 4))
        self.ocr_test_status.grid_remove()
        self.ocr_test_result.grid_remove()
        self.ocr_advanced_frame = ttk.LabelFrame(body, text="高级设置", padding=12)
        self.ocr_advanced_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        self.ocr_advanced_frame.columnconfigure(1, weight=1)
        self._field(self.ocr_advanced_frame, 0, "请求超时（秒）", "OpenAIRequestTimeout")
        self._field(self.ocr_advanced_frame, 1, "最大输出 tokens", "OpenAIMaxOutputTokens")
        self.prompt_label = ttk.Label(self.ocr_advanced_frame, text="OCR 提示词")
        self.prompt_label.grid(row=2, column=0, sticky="nw", pady=8)
        self.prompt_text = tk.Text(self.ocr_advanced_frame, height=4, wrap="word", relief="solid", borderwidth=1)
        self.prompt_text.insert("1.0", self.vars["OpenAIOCRPrompt"].get())
        self.prompt_text.grid(row=2, column=1, sticky="ew", padx=(14, 8), pady=8)
        self.prompt_help_button = self._help_button(self.ocr_advanced_frame, "OpenAIOCRPrompt")
        self.prompt_help_button.grid(row=2, column=2, padx=(0, 8), pady=8, sticky="n")
        self.ocr_advanced_frame.grid_remove()

    def _toggle_ocr_advanced(self) -> None:
        self.ocr_advanced_visible = not self.ocr_advanced_visible
        if self.ocr_advanced_visible:
            self.ocr_advanced_frame.grid()
            self.ocr_advanced_button.configure(text="隐藏高级设置")
        else:
            self.ocr_advanced_frame.grid_remove()
            self.ocr_advanced_button.configure(text="显示高级设置")

    def _set_ocr_test_result(self, status: str, text: str = "") -> None:
        self.ocr_test_status.configure(text=status)
        self.ocr_test_status.grid()
        self.ocr_test_result.configure(state="normal")
        self.ocr_test_result.delete("1.0", "end")
        self.ocr_test_result.insert("1.0", text)
        self.ocr_test_result.configure(state="disabled")
        if text:
            self.ocr_test_result.grid()
        else:
            self.ocr_test_result.grid_remove()

    def _test_ocr_service(self) -> None:
        if self.worker and self.worker.is_alive():
            messagebox.showwarning("任务运行中", "已有任务正在运行，请等待完成后再测试 OCR 服务。")
            return

        config = self._read_ui_config()
        sample = resource_path("static/sample.png")
        if not sample.exists():
            self._set_ocr_test_result("测试失败", f"测试图片不存在：{sample}")
            return

        self.ocr_test_button.configure(state="disabled")
        self._set_ocr_test_result("正在使用 static\\sample.png 测试 OCR 服务，请稍候…")

        def runner() -> None:
            try:
                from . import openai_ocr

                text = openai_ocr.recognize_image(str(sample), config)
                self.queue.put(("ocr_test_success", "OCR 服务测试成功。", text or "测试完成，但服务没有返回文本。"))
            except Exception as exc:
                self.queue.put(("ocr_test_error", "OCR 服务测试失败。", str(exc)))

        self.worker = threading.Thread(target=runner, daemon=True)
        self.worker.start()

    def _build_capture_page(self) -> None:
        page, body = self._new_page("设置采集与翻页", "这里的内容会跟随你选择的使用方式变化。")
        self.capture_body = body
        self._render_capture_options()

    def _apply_setup_mode_defaults(self) -> None:
        mode = self.setup_mode_var.get()
        if mode == "电脑 + 安卓模拟器（推荐）":
            self.vars["CaptureSource"].set("屏幕区域")
            if self.vars["PageMethod"].get() not in ("模拟按键", "模拟点击"):
                self.vars["PageMethod"].set("模拟按键")
        elif mode == "摄像头/采集卡/网络视频 + ADB 设备":
            self.vars["CaptureSource"].set("图像输入源")
            if self.vars["PageMethod"].get() not in ("音量下", "音量上", "ADB 模拟点击", "模拟点击学习"):
                self.vars["PageMethod"].set("音量下")

    def _render_capture_options(self) -> None:
        if not hasattr(self, "capture_body"):
            return
        for child in self.capture_body.winfo_children():
            child.destroy()
        self._apply_setup_mode_defaults()
        mode = self.setup_mode_var.get()
        row = 0
        if mode == "自定义组合（高级）":
            self._combo_field(self.capture_body, row, "采集来源", "CaptureSource", ("屏幕区域", "图像输入源"), lambda _event: self._render_capture_options())
            row += 1

        if self.vars["CaptureSource"].get() == "图像输入源":
            ttk.Label(self.capture_body, text="输入源 ID / 网络地址").grid(row=row, column=0, sticky="w", pady=8)
            self.input_source_box = ttk.Combobox(self.capture_body, values=(self.vars["InputSource"].get(),), textvariable=self.input_source_var)
            self.input_source_box.grid(row=row, column=1, sticky="ew", padx=(14, 8), pady=8)
            self.input_source_box.bind("<<ComboboxSelected>>", lambda _event: self._on_input_source_selected())
            self._help_button(self.capture_body, "InputSource").grid(row=row, column=2, padx=(0, 8))
            source_actions = ttk.Frame(self.capture_body)
            source_actions.grid(row=row, column=3, sticky="w")
            ttk.Button(source_actions, text="扫描", command=self._scan_input_sources).pack(side="left", padx=(0, 5))
            ttk.Button(source_actions, text="预览", command=self._preview_input_source).pack(side="left")
            row += 1
            self._field(self.capture_body, row, "预热帧数", "InputSourceWarmupFrames")
            row += 1
        else:
            ttk.Label(self.capture_body, text="截图区域").grid(row=row, column=0, sticky="w", pady=8)
            ttk.Label(self.capture_body, text="只截取小说正文，避免状态栏和按钮干扰 OCR。", foreground="#5c6870").grid(row=row, column=1, sticky="w", padx=(14, 8))
            self._help_button(self.capture_body, "CaptureSource").grid(row=row, column=2, padx=(0, 8))
            ttk.Button(self.capture_body, text="选择区域…", command=self._select_image_area).grid(row=row, column=3)
            row += 1

        if mode == "电脑 + 安卓模拟器（推荐）":
            methods = ("模拟按键", "模拟点击")
        elif mode == "摄像头/采集卡/网络视频 + ADB 设备":
            methods = ("音量下", "音量上", "ADB 模拟点击")
        else:
            methods = ("模拟按键", "模拟点击", "音量下", "音量上", "ADB 模拟点击", "模拟点击学习")
        self._combo_field(self.capture_body, row, "翻页方式", "PageMethod", methods, lambda _event: self._render_capture_options())
        row += 1
        method = self.vars["PageMethod"].get()
        if method == "模拟按键":
            self._field(self.capture_body, row, "翻页按键", "PageKey")
            row += 1
        elif method == "模拟点击":
            ttk.Label(self.capture_body, text="电脑点击位置").grid(row=row, column=0, sticky="w", pady=8)
            ttk.Label(self.capture_body, text="选择模拟器中的下一页区域。", foreground="#5c6870").grid(row=row, column=1, sticky="w", padx=(14, 8))
            self._help_button(self.capture_body, "PageMethod").grid(row=row, column=2)
            ttk.Button(self.capture_body, text="选择坐标…", command=self._select_click_point).grid(row=row, column=3)
            row += 1
        elif method in ("音量下", "音量上", "ADB 模拟点击", "模拟点击学习"):
            ttk.Label(self.capture_body, text="ADB 设备").grid(row=row, column=0, sticky="w", pady=8)
            self.adb_device_box = ttk.Combobox(self.capture_body, values=(self.vars["ADBSerial"].get(),), textvariable=self.adb_device_var)
            self.adb_device_box.grid(row=row, column=1, sticky="ew", padx=(14, 8), pady=8)
            self.adb_device_box.bind("<<ComboboxSelected>>", lambda _event: self._on_adb_device_selected())
            self._help_button(self.capture_body, "ADBSerial").grid(row=row, column=2)
            adb_actions = ttk.Frame(self.capture_body)
            adb_actions.grid(row=row, column=3)
            ttk.Button(adb_actions, text="扫描", command=self._scan_adb_devices).pack(side="left", padx=(0, 5))
            ttk.Button(adb_actions, text="连接", command=self._connect_adb).pack(side="left")
            row += 1
            if method in ("ADB 模拟点击", "模拟点击学习"):
                self._field(self.capture_body, row, "点击 X", "ADBTapX")
                row += 1
                self._field(self.capture_body, row, "点击 Y", "ADBTapY")
                row += 1
                tools = ttk.Frame(self.capture_body)
                tools.grid(row=row, column=1, sticky="w", padx=(14, 8), pady=4)
                ttk.Button(tools, text="从截图点选", command=self._pick_adb_click_from_screenshot).pack(side="left", padx=(0, 6))
                ttk.Button(tools, text="触摸学习", command=self._learn_adb_click).pack(side="left")
                row += 1
        if mode == "电脑 + 安卓模拟器（推荐）" or mode == "自定义组合（高级）":
            pin = ttk.Frame(self.capture_body)
            pin.grid(row=row, column=0, columnspan=3, sticky="w", pady=8)
            ttk.Checkbutton(pin, text="开始前 3 秒置顶当前活动窗口", variable=self.pin_window_var).pack(side="left")
            self._help_button(pin, "PinWindow").pack(side="left", padx=8)

    def _build_output_page(self) -> None:
        page, body = self._new_page("设置任务与保存位置", "默认目录已经可以直接使用；通常只需确认页数和等待时间。")
        self._field(body, 0, "采集页数", "CapturePages")
        self._field(body, 1, "基础等待（秒）", "Cycle")
        self._field(body, 2, "随机等待最小值", "ReadingDelayMin")
        self._field(body, 3, "随机等待最大值", "ReadingDelayMax")
        paths = ttk.LabelFrame(body, text="保存目录", padding=12)
        paths.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(18, 0))
        paths.columnconfigure(1, weight=1)
        self._field(paths, 0, "原始截图", "PictureDir", browse=True)
        self._field(paths, 1, "OCR 分页文本", "OCROutPaDir", browse=True)
        self._field(paths, 2, "合并文本", "MergeBookDir", browse=True)
        self._field(paths, 3, "最终小说", "FinalNovelDir", browse=True)

    def _build_run_page(self) -> None:
        page, body = self._new_page("准备完成", "保存配置后可开始采集。运行日志和进度会一直保留在本页。")
        actions = ttk.Frame(body)
        actions.grid(row=0, column=0, columnspan=3, sticky="ew")
        for col in range(4):
            actions.columnconfigure(col, weight=1)
        self.auto_button = ttk.Button(actions, text="一键采集并生成", style="Accent.TButton", command=self._start_auto)
        self.start_button = ttk.Button(actions, text="只采集 OCR", command=self._start_capture)
        self.stop_button = ttk.Button(actions, text="停止", command=self._stop_capture, state="disabled")
        save_button = ttk.Button(actions, text="仅保存配置", command=self._save_config_from_ui)
        for col, button in enumerate((self.auto_button, self.start_button, self.stop_button, save_button)):
            button.grid(row=0, column=col, sticky="ew", padx=4)

        tools = ttk.Frame(body)
        tools.grid(row=1, column=0, columnspan=3, sticky="w", pady=(14, 8))
        self.merge_button = ttk.Button(tools, text="合并已有文本", command=self._start_merge)
        self.format_button = ttk.Button(tools, text="格式化已有文本", command=self._start_format)
        self.open_config_button = ttk.Button(tools, text="打开配置文件", command=self._open_config_file)
        clear_button = ttk.Button(tools, text="清空 OCR 文本", command=self._clear_ocr_text)
        for button in (self.merge_button, self.format_button, self.open_config_button, clear_button):
            button.pack(side="left", padx=(0, 8))

        log_frame = ttk.LabelFrame(body, text="运行日志", padding=8)
        log_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(8, 0))
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        body.rowconfigure(2, weight=1)
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap="word", height=13, state="normal")
        self.log_text.grid(row=0, column=0, sticky="nsew")
        self.progress = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(log_frame, variable=self.progress, maximum=100)
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(8, 0))

    def _show_page(self, index: int) -> None:
        index = max(0, min(index, len(self.page_frames) - 1))
        self.current_page = index
        if index == 3:
            self._render_capture_options()
        self.page_frames[index].tkraise()
        self.step_label.configure(text="首页" if index == 0 else f"第 {index} / 5 步")
        if index == 0:
            self.footer.grid_remove()
        else:
            self.footer.grid()
            self.back_button.configure(state="normal")
            self.next_button.configure(text="完成" if index == 5 else "下一步")

    def _next_page(self) -> None:
        if self.current_page == 1:
            self._apply_setup_mode_defaults()
        if self.current_page >= 5:
            self._save_config_from_ui()
            return
        self._show_page(self.current_page + 1)

    def _previous_page(self) -> None:
        self._show_page(max(0, self.current_page - 1))

    def _choose_dir(self, key: str) -> None:
        selected = filedialog.askdirectory(initialdir=str(resolve_path(self.vars[key].get())))
        if selected:
            self.vars[key].set(selected)

    def _is_dedicated_backend(self) -> bool:
        return self.vars["OCRBackend"].get() == "专用OCR路径"

    def _set_prompt_text(self, value: str) -> None:
        self.prompt_text.delete("1.0", "end")
        self.prompt_text.insert("1.0", value)

    def _apply_ocr_backend_defaults(self, initial: bool = False) -> None:
        model = self.vars["OpenAIOCRModel"].get().strip()
        prompt = self.prompt_text.get("1.0", "end").strip()
        default_model = str(DEFAULT_CONFIG["OpenAIOCRModel"])
        default_prompt = str(DEFAULT_CONFIG["OpenAIOCRPrompt"])

        if self._is_dedicated_backend():
            if not initial or model == default_model or not model:
                self.vars["OpenAIOCRModel"].set("Unlimited-OCR")
            if self.vars["OpenAIURL"].get().strip() in ("", str(DEFAULT_CONFIG["OpenAIURL"])):
                self.vars["OpenAIURL"].set("http://127.0.0.1:8080/v1")
            if prompt:
                self._set_prompt_text("")
            for widget in (getattr(self, "prompt_label", None), getattr(self, "prompt_text", None), getattr(self, "prompt_help_button", None)):
                if widget:
                    widget.grid_remove()
            return

        if model == "Unlimited-OCR":
            self.vars["OpenAIOCRModel"].set(default_model)
        if not prompt:
            self._set_prompt_text(default_prompt)
        for widget in (getattr(self, "prompt_label", None), getattr(self, "prompt_text", None), getattr(self, "prompt_help_button", None)):
            if widget:
                widget.grid()

    def _current_input_source_id(self) -> str:
        value = self.input_source_var.get().strip()
        return self.input_source_display_to_id.get(value, value)

    def _current_adb_serial(self) -> str:
        value = self.adb_device_var.get().strip()
        return self.adb_display_to_serial.get(value, value)

    def _on_input_source_selected(self) -> None:
        self.vars["InputSource"].set(self._current_input_source_id())

    def _on_adb_device_selected(self) -> None:
        self.vars["ADBSerial"].set(self._current_adb_serial())

    def _set_adb_selection_by_serial(self, serial: str) -> None:
        for label, item_serial in self.adb_display_to_serial.items():
            if item_serial == serial:
                self.adb_device_var.set(label)
                break
        else:
            self.adb_device_var.set(serial)
        self.vars["ADBSerial"].set(serial)

    def _read_ui_config(self) -> dict:
        self.vars["InputSource"].set(self._current_input_source_id())
        self.vars["ADBSerial"].set(self._current_adb_serial())
        config = {key: var.get() for key, var in self.vars.items()}
        config["OpenAIOCRPrompt"] = self.prompt_text.get("1.0", "end").strip()
        if config.get("OCRBackend") == "专用OCR路径":
            if not str(config.get("OpenAIOCRModel") or "").strip() or config.get("OpenAIOCRModel") == DEFAULT_CONFIG["OpenAIOCRModel"]:
                config["OpenAIOCRModel"] = "Unlimited-OCR"
                self.vars["OpenAIOCRModel"].set("Unlimited-OCR")
            if str(config.get("OpenAIURL") or "").strip() in ("", str(DEFAULT_CONFIG["OpenAIURL"])):
                config["OpenAIURL"] = "http://127.0.0.1:8080/v1"
                self.vars["OpenAIURL"].set(config["OpenAIURL"])
            config["OpenAIOCRPrompt"] = ""
            if self.prompt_text.get("1.0", "end").strip():
                self._set_prompt_text("")
        return config

    def _save_config_from_ui(self) -> dict:
        config = self._read_ui_config()
        save_config(config)
        self.config_data = config
        self._log("配置已保存。")
        return config

    def _select_image_area(self) -> None:
        self._start_background("选择截图区域", lambda: workflow.run_helper("get_novel_image_plot"))

    def _select_click_point(self) -> None:
        self._start_background("选择点击坐标", lambda: workflow.run_helper("get_click_plot"))

    def _scan_input_sources(self) -> None:
        try:
            sources = workflow.list_input_source_details()
        except Exception as exc:
            messagebox.showerror("扫描失败", str(exc))
            return
        if not sources:
            self._log("没有扫描到可读取的图像输入源。")
            return
        labels = [source["label"] for source in sources]
        self.input_source_display_to_id = {source["label"]: source["id"] for source in sources}
        self.input_source_box.configure(values=labels)
        current = self.vars["InputSource"].get()
        selected = next((source["label"] for source in sources if source["id"] == current), labels[0])
        self.input_source_var.set(selected)
        self.vars["InputSource"].set(self.input_source_display_to_id[selected])
        self._log(f"已扫描到图像输入源: {', '.join(labels)}")

    def _scan_adb_devices(self) -> None:
        try:
            devices = workflow.list_adb_devices()
        except Exception as exc:
            messagebox.showerror("扫描失败", str(exc))
            return
        if not devices:
            self._log("没有扫描到 ADB 设备。")
            return

        labels = [device["label"] for device in devices]
        self.adb_display_to_serial = {device["label"]: device["serial"] for device in devices}
        self.adb_device_box.configure(values=labels)
        current = self.vars["ADBSerial"].get()
        selected = next((device["label"] for device in devices if device["serial"] == current), labels[0])
        self.adb_device_var.set(selected)
        self.vars["ADBSerial"].set(self.adb_display_to_serial[selected])
        self._log(f"已扫描到 ADB 设备: {', '.join(labels)}")

    def _preview_input_source(self) -> None:
        source = self._current_input_source_id()
        self.vars["InputSource"].set(source)
        if self.preview_window and self.preview_window.winfo_exists():
            if self.preview_source == source:
                self.preview_window.lift()
                return
            self._close_input_preview()

        try:
            import cv2
            from PIL import Image, ImageTk

            from . import frame_sources
        except ImportError as exc:
            messagebox.showerror("预览失败", f"使用图像输入源预览需要安装 opencv-python 和 pillow: {exc}")
            return

        capture = frame_sources.open_input_source(source)
        if not capture.isOpened():
            capture.release()
            messagebox.showerror("预览失败", f"无法打开图像输入源: {source}")
            return

        self.preview_source = source
        self.preview_capture = capture
        self.preview_window = tk.Toplevel(self)
        self.preview_window.title(f"输入源预览 - {source}")
        self.preview_window.geometry("760x520")
        self.preview_window.minsize(420, 300)
        self.preview_window.protocol("WM_DELETE_WINDOW", self._close_input_preview)
        self.preview_label = ttk.Label(self.preview_window, anchor="center")
        self.preview_label.pack(fill="both", expand=True, padx=8, pady=8)
        self._input_preview_image_class = Image
        self._input_preview_photo_class = ImageTk
        self._update_input_preview()

    def _update_input_preview(self) -> None:
        if not self.preview_window or not self.preview_window.winfo_exists() or not self.preview_capture:
            return

        ok, frame = self.preview_capture.read()
        if ok:
            import cv2

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = self._input_preview_image_class.fromarray(frame)
            max_width = max(320, self.preview_label.winfo_width() - 16)
            max_height = max(240, self.preview_label.winfo_height() - 16)
            image.thumbnail((max_width, max_height))
            self.preview_photo = self._input_preview_photo_class.PhotoImage(image)
            self.preview_label.configure(image=self.preview_photo, text="")
        else:
            self.preview_label.configure(image="", text="无法读取图像输入源画面")

        self.preview_after_id = self.after(33, self._update_input_preview)

    def _close_input_preview(self) -> None:
        if self.preview_after_id:
            try:
                self.after_cancel(self.preview_after_id)
            except tk.TclError:
                pass
            self.preview_after_id = None
        if self.preview_capture:
            self.preview_capture.release()
            self.preview_capture = None
        if self.preview_window and self.preview_window.winfo_exists():
            self.preview_window.destroy()
        self.preview_window = None
        self.preview_label = None
        self.preview_photo = None
        self.preview_source = ""

    def _connect_adb(self) -> None:
        config = self._save_config_from_ui()

        def task() -> None:
            serial = workflow.connect_adb(config, self._worker_callback)
            self.queue.put(("adb_serial", f"ADB 序列号已保存: {serial}", {"serial": serial}))

        self._start_background("连接 ADB", task)

    def _learn_adb_click(self) -> None:
        config = self._save_config_from_ui()

        def task() -> None:
            point = workflow.learn_adb_tap(config, self._worker_callback)
            self.queue.put(("adb_tap", "ADB 点击坐标已写入配置。", point))

        self._start_background("学习点击位置", task)

    def _pick_adb_click_from_screenshot(self) -> None:
        config = self._save_config_from_ui()

        def task() -> None:
            screenshot = workflow.capture_adb_screenshot(config, self._worker_callback)
            self.queue.put(("adb_screenshot", "ADB 截屏已打开，请在图片上点击翻页位置。", screenshot))

        self._start_background("ADB 截图点选", task)

    def _open_adb_screenshot_picker(self, payload: dict) -> None:
        try:
            from PIL import Image, ImageTk
        except ImportError as exc:
            messagebox.showerror("打开失败", f"ADB 截图点选需要安装 pillow: {exc}")
            return

        path = Path(str(payload["path"]))
        image = Image.open(path)
        width, height = image.size
        max_width, max_height = 820, 640
        scale = min(max_width / width, max_height / height, 1.0)
        display_size = (max(1, round(width * scale)), max(1, round(height * scale)))
        display_image = image.resize(display_size, Image.LANCZOS) if scale < 1.0 else image.copy()

        if self.adb_picker_window and self.adb_picker_window.winfo_exists():
            self.adb_picker_window.destroy()

        self.adb_picker_scale = scale
        self.adb_picker_window = tk.Toplevel(self)
        self.adb_picker_window.title(f"ADB 截图点选 - {payload.get('serial', '')}")
        self.adb_picker_window.resizable(False, False)
        frame = ttk.Frame(self.adb_picker_window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Label(frame, text="在图片中点击下一页位置，坐标会按手机原始分辨率保存。").pack(anchor="w", pady=(0, 8))
        canvas = tk.Canvas(frame, width=display_size[0], height=display_size[1], highlightthickness=0)
        canvas.pack()
        self.adb_picker_photo = ImageTk.PhotoImage(display_image)
        canvas.create_image(0, 0, image=self.adb_picker_photo, anchor="nw")

        def select_point(event) -> None:
            x = max(0, min(width - 1, round(event.x / self.adb_picker_scale)))
            y = max(0, min(height - 1, round(event.y / self.adb_picker_scale)))
            self.vars["PageMethod"].set("ADB 模拟点击")
            self.vars["ADBTapX"].set(str(x))
            self.vars["ADBTapY"].set(str(y))
            self._save_config_from_ui()
            self._log(f"已从 ADB 截图点选坐标: {x}, {y}")
            if self.adb_picker_window and self.adb_picker_window.winfo_exists():
                self.adb_picker_window.destroy()

        canvas.bind("<Button-1>", select_point)

    def _open_config_file(self) -> None:
        os.startfile(PROJECT_ROOT / "config.json")

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
        self._close_input_preview()
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
        self._close_input_preview()
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
            elif kind == "adb_serial":
                self._set_adb_selection_by_serial(str(payload["serial"]))
                self._save_config_from_ui()
                self._set_busy(False)
            elif kind == "adb_tap":
                if payload:
                    self.vars["PageMethod"].set("ADB 模拟点击")
                    self.vars["ADBTapX"].set(str(payload["x"]))
                    self.vars["ADBTapY"].set(str(payload["y"]))
                    self._save_config_from_ui()
                self._set_busy(False)
            elif kind == "adb_screenshot":
                if payload:
                    self._set_adb_selection_by_serial(str(payload["serial"]))
                    self._open_adb_screenshot_picker(payload)
                self._set_busy(False)
            elif kind == "ocr_test_success":
                self.ocr_test_button.configure(state="normal")
                self._set_ocr_test_result(message, str(payload or ""))
            elif kind == "ocr_test_error":
                self.ocr_test_button.configure(state="normal")
                self._set_ocr_test_result(message, str(payload or "未知错误"))
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

    def _on_close(self) -> None:
        self._close_input_preview()
        if self.adb_picker_window and self.adb_picker_window.winfo_exists():
            self.adb_picker_window.destroy()
        self.destroy()


def main() -> None:
    GermenGUI().mainloop()


if __name__ == "__main__":
    main()
