# Germen

Germen 是一个个人向安卓阅读 App 小说提取工具：按固定区域截图，使用 OpenAI API 进行图片 OCR，自动翻页，并把 OCR 文本合并、整理成最终小说文本。

## 当前架构

- `GUI.py`：推荐入口，可配置目录、OpenAI API、截图区域、翻页方式、采集页数，并启动采集/合并/格式化。
- `OpenAIOCR.py`：唯一 OCR 后端，使用 OpenAI API 识别截图文本。
- `workflow.py`：采集、OCR、翻页、合并、格式化的公共流程，GUI 和命令行共用。
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
10. `PageMethod`：`模拟按键` 或 `模拟点击`。
11. `PageKey`：模拟按键翻页时发送的按键。
12. `CapturePages`：计划采集页数。

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
5. 点击“选择截图区域”，框选小说正文区域。
6. 选择翻页方式：
   - `模拟按键`：先在模拟器中配置键盘映射，再填入按键。
   - `模拟点击`：点击“选择点击坐标”，选择翻页点击位置。
7. 点击“开始采集”或“一键采集并生成”。

## 注意事项

- 项目已移除本地 PaddleOCR 代码和依赖，不再需要下载 OCR 模型或安装 Paddle。
- 如果模拟器以管理员权限运行，Python/终端也可能需要管理员权限才能发送点击或按键。
- 采集时不要遮挡阅读窗口；截图区域、点击坐标和翻页按键都应提前确认。
- GUI 的后台采集使用线程执行，界面日志和进度通过主线程刷新；点击“停止采集”会在当前页 OCR 完成后退出。
