# Germen

Germen 是一个个人向安卓阅读 App 小说提取工具：按固定区域或图像输入源采集页面，使用通用 VLM 或专用 OCR 模型进行图片 OCR，自动翻页，并把 OCR 文本合并、整理成最终小说文本。

## 当前架构

- `src/germen/gui.py`：推荐 GUI 入口，可配置目录、OpenAI API、截图区域、翻页方式、采集页数，并启动采集/合并/格式化。
- `src/germen/web/main.py`：浏览器入口，按步骤配置 API、服务器端图像输入源、翻页方式、保存目录，并查看采集进度。
- `src/germen/openai_ocr.py`：统一 OCR 后端，可走通用 OpenAI 兼容 VLM，也可走专用图片-only OCR 模型。
- `src/germen/workflow.py`：采集、OCR、翻页、合并、格式化的公共流程，GUI、WebUI 和命令行共用。
- `src/germen/frame_sources.py`：统一屏幕区域和图像输入源采帧。
- `src/germen/adb_controller.py`：连接 ADB、发送音量键、截取设备屏幕、监听一次用户触摸并学习点击坐标。
- `src/germen/main_program.py`：命令行入口，适合已有配置后快速运行。

## 项目结构

- `src/germen/`：主程序包。
- `src/germen/web/`：WebUI 服务。
- `data/`：坐标、替换词表等运行数据。
- `static/`：WebUI 测试图片、预览图片等静态文件。
- `tools/`：外部辅助工具和宏文件。
- `legacy/streamlit/`：旧版 Streamlit 原型，默认运行路径不依赖它。
- `NovelPictures/`、`NovelOCRText/`、`MergeText/`、`FinalBooks/`、`log/`：运行产物目录，默认不提交。

## 配置文件

`config.json` 的主要字段：

1. `PictureDir`：截图保存目录。
2. `OCROutPaDir`：OpenAI OCR 生成的文本保存目录。
3. `MergeBookDir`：合并后、未格式化文本的保存目录。
4. `FinalNovelDir`：最终文本保存目录。
5. `Cycle`：每一轮截图、OCR、翻页后的基础等待秒数。
6. `ReadingDelayMin` / `ReadingDelayMax`：模拟人类阅读时间波动的额外随机暂停范围，默认每次翻页后随机增加 `5` 到 `45` 秒。
7. `OCRBackend`：`通用VLM路径` 或 `专用OCR路径`。
8. `OpenAIURL`：OpenAI 兼容 API Base URL，官方接口通常为 `https://api.openai.com/v1`；本地 Unlimited-OCR 常用 `http://127.0.0.1:8080/v1`。
9. `OpenAIAPIKEY`：OpenAI 兼容 API Key。第三方付费服务可在这里填写；本地服务不需要密钥时可以留空。
10. `OpenAIOCRModel`：OCR 模型。通用路径默认 `gpt-4.1-mini`；选择专用 OCR 路径时界面会自动填入 `Unlimited-OCR`，仍可手动改成服务实际暴露的模型名。
11. `OpenAIOCRPrompt`：通用 VLM OCR 提示词；选择专用 OCR 路径时界面和后台会自动清空，真实请求不会发送提示词。
12. `DedicatedOCRStripCoordinates`：专用 OCR 返回 `text [x, y, x, y]正文` 时是否在后台剥离坐标前缀，默认 `true`。
13. `CaptureSource`：`屏幕区域` 或 `图像输入源`。
14. `InputSource`：图像输入源编号，通常从 `0` 开始。
15. `ADBSerial`：ADB 设备序列号。单设备连接时可以留空，由程序自动识别。
16. `ADBTapX` / `ADBTapY`：ADB 模拟点击使用的屏幕坐标，可手动填写、触摸学习或从 ADB 截图点选。
17. `PageMethod`：`模拟按键`、`模拟点击`、`音量下`、`音量上`、`ADB 模拟点击` 或兼容旧配置的 `模拟点击学习`。
18. `PageKey`：模拟按键翻页时发送的按键。
19. `CapturePages`：计划采集页数。
20. `WebUIPassword`：WebUI 访问密码，默认值为 `germen`，请在首次使用前修改。

## 使用方法

1. 创建并进入 Python 3.10+ 虚拟环境。
2. 安装项目和依赖：

```powershell
python -m pip install -e .
```

3. 运行命令行采集流程：

```powershell
germen
germen --admin
```

4. 运行 GUI：

```powershell
germen ui
germen ui --admin
```

5. 在 GUI 中选择 OCR 路径，配置 OpenAI 兼容 API、模型、截图目录和输出目录；两条路径共用同一组 URL、Key 和模型字段。
6. 选择采集来源：
   - `屏幕区域`：点击“选择截图区域”，框选小说正文区域。
   - `图像输入源`：点击“扫描输入源”，选择可读取的输入源编号，再点击“预览输入源”确认画面。
7. 连接真实安卓设备时，点击“连接 ADB”。如果只接入一台已授权设备，序列号可以留空。
8. 选择翻页方式：
   - `模拟按键`：先在模拟器中配置键盘映射，再填入按键。
   - `模拟点击`：点击“选择点击坐标”，选择翻页点击位置。
   - `音量下` / `音量上`：通过 ADB 发送音量键翻页。
   - `ADB 模拟点击`：可以手动填写 ADB 点击 X/Y，点击“学习点击位置”后在手机上触摸一次，或点击“ADB 截图点选”截取手机当前屏幕并在图片上点选坐标。
   - `模拟点击学习`：兼容旧配置，内部仍使用 ADB 点击坐标翻页。
9. 点击“开始采集”或“一键采集并生成”。

## WebUI

启动 WebUI：

```powershell
germen web
germen web --admin
```

自定义监听地址和端口：

```powershell
germen web --host 0.0.0.0 --port 7860
germen web --host ::1 --port 7860
germen web --admin --host 0.0.0.0 --port 7860
```

默认访问地址为 `http://127.0.0.1:7860/`，默认密码在 `config.json` 的 `WebUIPassword` 字段中设置。WebUI 只支持服务器端图像输入源采集，不支持远程上传图片作为输入源，也不使用屏幕区域截图。
IPv4 本机访问通常使用 `127.0.0.1`，IPv4 全网卡监听可用 `0.0.0.0`；IPv6 本机访问通常使用 `::1`，IPv6 全网卡监听可用 `::`。
如果模拟器以管理员权限运行，请给 Germen 命令加上 `--admin`，程序会通过 Windows UAC 请求管理员权限后重新启动。
如果预览或扫描输入源提示缺少 OpenCV，请以启动 WebUI 的同一个 Python 为准检查环境：`python -c "import sys; print(sys.executable); import cv2; print(cv2.__version__)"`。需要安装时也使用同一个解释器执行：`python -m pip install opencv-python`。

WebUI 的配置流程：

1. 配置 OCR 路径和 OpenAI 兼容接口，并可用 `static\sample.png` 测试 OCR。
2. 扫描或手动填写服务器端图像输入源，点击“预览”确认画面。
3. 选择音量上、音量下、服务器端模拟点击或 ADB 模拟点击翻页；ADB 模拟点击可截取当前设备屏幕并用鼠标点选坐标。
4. 配置图片、OCR 文本、合并文本、最终文本目录、采集页数、基础翻页等待时间和阅读误差随机范围。
5. 点击“开始获取”。任务运行后，可以随时重新打开同一个 URL 查看进度和日志。

## 注意事项

- 项目已移除本地 PaddleOCR 代码和依赖，不再需要下载 OCR 模型或安装 Paddle。
- 如果模拟器以管理员权限运行，Python/终端也可能需要管理员权限才能发送点击或按键。
- 采集时不要遮挡阅读窗口；截图区域、点击坐标和翻页按键都应提前确认。
- 使用图像输入源需要安装 `opencv-python`，并保证输入源在其他软件中没有被独占。
- 打开图像输入源预览时会占用该输入源；开始采集或一键采集前，GUI 会自动关闭预览并释放设备。
- 使用 ADB 翻页需要手机开启 USB 调试，并在手机上确认授权。
- GUI 的后台采集使用线程执行，界面日志和进度通过主线程刷新；点击“停止采集”会在当前页 OCR 完成后退出。
