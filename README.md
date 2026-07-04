# Germen

Germen 是一个个人向安卓阅读 App 小说提取工具：按固定区域或图像输入源采集页面，使用 OpenAI API 进行图片 OCR，自动翻页，并把 OCR 文本合并、整理成最终小说文本。

## 当前架构

- `GUI.py`：推荐入口，可配置目录、OpenAI API、截图区域、翻页方式、采集页数，并启动采集/合并/格式化。
- `OpenAIOCR.py`：唯一 OCR 后端，使用 OpenAI API 识别截图文本。
- `workflow.py`：采集、OCR、翻页、合并、格式化的公共流程，GUI 和命令行共用。
- `frame_sources.py`：统一屏幕区域和图像输入源采帧。
- `adb_controller.py`：连接 ADB、发送音量键、监听一次用户触摸并学习点击坐标。
- `MainProgram.py`：命令行兼容入口，适合已有配置后快速运行。

## 配置文件

`config.json` 的主要字段：

1. `PictureDir`：截图保存目录。
2. `OCROutPaDir`：OpenAI OCR 生成的文本保存目录。
3. `MergeBookDir`：合并后、未格式化文本的保存目录。
4. `FinalNovelDir`：最终文本保存目录。
5. `Cycle`：每一轮截图、OCR、翻页后的等待秒数。
6. `OpenAIURL`：OpenAI API Base URL，官方接口通常为 `https://api.openai.com/v1`。
7. `OpenAIAPIKEY`：OpenAI API Key。也可以留空并设置环境变量 `OPENAI_API_KEY`。
8. `OpenAIOCRModel`：用于 OCR 的视觉模型。
9. `OpenAIOCRPrompt`：OCR 提示词。
10. `CaptureSource`：`屏幕区域` 或 `图像输入源`。
11. `InputSource`：图像输入源编号，通常从 `0` 开始。
12. `ADBSerial`：ADB 设备序列号。单设备连接时可以留空，由程序自动识别。
13. `ADBTapX` / `ADBTapY`：ADB 模拟点击学习到的屏幕坐标。
14. `PageMethod`：`模拟按键`、`模拟点击`、`音量下` 或 `模拟点击学习`。
15. `PageKey`：模拟按键翻页时发送的按键。
16. `CapturePages`：计划采集页数。

## 使用方法

1. 创建并进入 Python 3.10+ 虚拟环境。
2. 安装依赖：

```powershell
pip install -r requirements.txt
```

3. 运行 GUI：

```powershell
python GUI.py
```

4. 在 GUI 中配置 OpenAI API Key、模型、截图目录和输出目录。
5. 选择采集来源：
   - `屏幕区域`：点击“选择截图区域”，框选小说正文区域。
   - `图像输入源`：点击“扫描输入源”，选择可读取的输入源编号。
6. 连接真实安卓设备时，点击“连接 ADB”。如果只接入一台已授权设备，序列号可以留空。
7. 选择翻页方式：
   - `模拟按键`：先在模拟器中配置键盘映射，再填入按键。
   - `模拟点击`：点击“选择点击坐标”，选择翻页点击位置。
   - `音量下`：通过 ADB 发送音量下按键翻页。
   - `模拟点击学习`：点击“学习点击位置”，按提示在手机上点击一次下一页区域，程序会保存该坐标并在采集时复用。
8. 点击“开始采集”或“一键采集并生成”。

## 注意事项

- 项目已移除本地 PaddleOCR 代码和依赖，不再需要下载 OCR 模型或安装 Paddle。
- 如果模拟器以管理员权限运行，Python/终端也可能需要管理员权限才能发送点击或按键。
- 采集时不要遮挡阅读窗口；截图区域、点击坐标和翻页按键都应提前确认。
- 使用图像输入源需要安装 `opencv-python`，并保证输入源在其他软件中没有被独占。
- 使用 ADB 翻页需要手机开启 USB 调试，并在手机上确认授权。
- GUI 的后台采集使用线程执行，界面日志和进度通过主线程刷新；点击“停止采集”会在当前页 OCR 完成后退出。
