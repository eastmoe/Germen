import base64
import argparse
import json
import secrets
import socket
import sys
import threading
import time
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import unquote, urlparse


from ..app_config import DEFAULT_CONFIG, PROJECT_ROOT, ensure_project_dirs, load_config, save_config
from ..coordinates import save_click_plot


SESSION_COOKIE = "germen_webui_session"
MAX_EVENTS = 400
SESSIONS: set[str] = set()
STOP_EVENT: Optional[threading.Event] = None
TASK_THREAD: Optional[threading.Thread] = None
STATE_LOCK = threading.Lock()
STATE: Dict[str, Any] = {
    "running": False,
    "status": "idle",
    "message": "等待配置。",
    "page": 0,
    "total": 0,
    "startedAt": "",
    "endedAt": "",
    "error": "",
    "captured": 0,
    "mergedPath": "",
    "finalPath": "",
    "events": [],
}


INDEX_HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Germen WebUI</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f6f7f3;
      --panel: #ffffff;
      --ink: #202225;
      --muted: #687076;
      --line: #d9ded5;
      --accent: #1d6f5f;
      --accent-2: #b83f31;
      --soft: #e8f2ee;
      --warn: #fff3d5;
      --danger: #fff0ed;
      --radius: 8px;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
      background: var(--bg);
      color: var(--ink);
    }
    button, input, textarea, select { font: inherit; }
    button {
      border: 1px solid var(--accent);
      background: var(--accent);
      color: white;
      border-radius: 6px;
      padding: 9px 13px;
      cursor: pointer;
    }
    button.secondary { background: white; color: var(--accent); }
    button.danger { border-color: var(--accent-2); background: var(--accent-2); }
    button:disabled { opacity: .55; cursor: wait; }
    label { display: block; color: var(--muted); font-size: 13px; margin-bottom: 5px; }
    input, textarea, select {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 9px 10px;
      background: white;
      color: var(--ink);
    }
    textarea { min-height: 92px; resize: vertical; }
    .hidden { display: none !important; }
    .login {
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 24px;
    }
    .login-box, .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: 0 10px 30px rgba(32, 34, 37, .07);
    }
    .login-box { width: min(420px, 100%); padding: 26px; }
    .login-box h1 { margin: 0 0 4px; font-size: 28px; }
    .login-box p, .hint { color: var(--muted); margin: 6px 0 18px; line-height: 1.55; }
    .shell {
      width: min(1160px, calc(100% - 32px));
      margin: 22px auto 34px;
      display: grid;
      gap: 14px;
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }
    header h1 { margin: 0; font-size: 26px; }
    header p { margin: 4px 0 0; color: var(--muted); }
    .steps {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 8px;
    }
    .step-tab {
      border: 1px solid var(--line);
      background: white;
      color: var(--ink);
      text-align: left;
      min-height: 54px;
    }
    .step-tab.active { border-color: var(--accent); background: var(--soft); }
    .step-tab.done::after { content: " 已保存"; color: var(--accent); font-size: 12px; }
    .panel { padding: 18px; }
    .panel h2 { margin: 0 0 4px; font-size: 20px; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
    .grid.three { grid-template-columns: repeat(3, 1fr); }
    .field { min-width: 0; }
    .actions { display: flex; flex-wrap: wrap; gap: 9px; margin-top: 14px; align-items: center; }
    .result {
      margin-top: 13px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 12px;
      background: #fbfcfa;
      white-space: pre-wrap;
      max-height: 260px;
      overflow: auto;
    }
    .preview {
      margin-top: 14px;
      display: grid;
      grid-template-columns: minmax(220px, 420px) 1fr;
      gap: 14px;
      align-items: start;
    }
    .preview img {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #f0f0f0;
    }
    .pickable { cursor: crosshair; }
    .status-strip {
      display: grid;
      grid-template-columns: 1.4fr 1fr 1fr 1fr;
      gap: 10px;
    }
    .metric {
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px 12px;
      background: white;
      min-width: 0;
    }
    .metric span { color: var(--muted); font-size: 12px; }
    .metric strong {
      display: block;
      margin-top: 3px;
      overflow-wrap: anywhere;
    }
    .bar {
      height: 12px;
      border-radius: 999px;
      background: #e4e7df;
      overflow: hidden;
      margin: 13px 0;
    }
    .bar div { height: 100%; width: 0%; background: var(--accent); transition: width .25s ease; }
    .events {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #16191b;
      color: #e8eee9;
      padding: 12px;
      height: 260px;
      overflow: auto;
      font-family: Consolas, "Courier New", monospace;
      font-size: 13px;
      line-height: 1.5;
      white-space: pre-wrap;
    }
    .notice { background: var(--warn); border: 1px solid #e7c96e; border-radius: 6px; padding: 10px 12px; }
    .error { background: var(--danger); border: 1px solid #e0a093; color: #7b251d; border-radius: 6px; padding: 10px 12px; margin-top: 12px; }
    @media (max-width: 820px) {
      .steps, .grid, .grid.three, .preview, .status-strip { grid-template-columns: 1fr; }
      header { align-items: flex-start; flex-direction: column; }
    }
  </style>
</head>
<body>
  <main id="loginView" class="login">
    <section class="login-box">
      <h1>Germen</h1>
      <p>请输入 `config.json` 中的 WebUIPassword。</p>
      <form id="loginForm">
        <label for="password">访问密码</label>
        <input id="password" type="password" autocomplete="current-password" required>
        <div class="actions">
          <button type="submit">进入 WebUI</button>
        </div>
        <div id="loginError" class="error hidden"></div>
      </form>
    </section>
  </main>

  <main id="appView" class="shell hidden">
    <header>
      <div>
        <h1>Germen WebUI</h1>
        <p>服务器端图像输入源采集、OCR 与自动翻页。</p>
      </div>
      <button id="logoutBtn" class="secondary">退出</button>
    </header>

    <nav class="steps" id="steps"></nav>

    <section class="panel step-panel" data-step="0">
      <h2>1. API</h2>
      <p class="hint">保存 OCR 接口配置后，可以用项目内置的 `static\sample.png` 做一次 OCR 测试。</p>
      <div class="grid">
        <div class="field">
          <label>OCR 路径</label>
          <select id="OCRBackend">
            <option value="通用VLM路径">通用 VLM 路径</option>
            <option value="专用OCR路径">专用 OCR 路径</option>
          </select>
        </div>
        <div class="field"><label>API Base URL</label><input id="OpenAIURL"></div>
        <div class="field"><label>API Key</label><input id="OpenAIAPIKEY" type="password" placeholder="留空表示保留已有密钥"></div>
        <div class="field"><label>OCR 模型</label><input id="OpenAIOCRModel"></div>
        <div class="field"><label>请求超时秒数</label><input id="OpenAIRequestTimeout" inputmode="numeric"></div>
        <div class="field"><label>最大输出 Token</label><input id="OpenAIMaxOutputTokens" inputmode="numeric"></div>
        <div class="field"><label>当前密钥状态</label><input id="apiKeyState" disabled></div>
      </div>
      <div class="field" style="margin-top:14px"><label>OCR 提示词</label><textarea id="OpenAIOCRPrompt"></textarea></div>
      <div class="actions">
        <button data-save="api">保存 API</button>
        <button id="testApiBtn" class="secondary">用 sample.png 测试</button>
      </div>
      <div id="apiResult" class="result hidden"></div>
    </section>

    <section class="panel step-panel hidden" data-step="1">
      <h2>2. 图像输入源</h2>
      <p class="hint">WebUI 只使用服务器端的图像输入源，不使用远程浏览器上传图片，也不使用屏幕区域截图。</p>
      <div class="grid three">
        <div class="field"><label>输入源名称或 ID</label><input id="InputSource" list="sourceOptions"><datalist id="sourceOptions"></datalist></div>
        <div class="field"><label>预热帧数</label><input id="InputSourceWarmupFrames" inputmode="numeric"></div>
        <div class="field"><label>扫描范围</label><input id="scanMax" value="8" inputmode="numeric"></div>
      </div>
      <div class="actions">
        <button id="scanSourcesBtn" class="secondary">扫描输入源</button>
        <button id="previewBtn" class="secondary">预览</button>
        <button data-save="input">保存输入源</button>
      </div>
      <div id="runtimeInfo" class="result"></div>
      <div id="sourceList" class="result hidden"></div>
      <div class="preview hidden" id="previewBox">
        <img id="previewImage" alt="图像输入源预览">
        <div class="notice">预览图来自运行 Web 服务的这台机器。采集开始后会按相同输入源逐页取帧。</div>
      </div>
    </section>

    <section class="panel step-panel hidden" data-step="2">
      <h2>3. 翻页方式</h2>
      <p class="hint">音量键和 ADB 模拟点击会发给安卓设备；模拟点击会在服务器桌面上点击指定坐标。</p>
      <div class="grid">
        <div class="field">
          <label>方式</label>
          <select id="PageMethod">
            <option value="音量下">音量下</option>
            <option value="音量上">音量上</option>
            <option value="模拟点击">模拟点击</option>
            <option value="ADB 模拟点击">ADB 模拟点击</option>
          </select>
        </div>
        <div class="field"><label>ADB 设备名称或 ID</label><input id="ADBSerial" list="adbOptions" placeholder="单设备可留空"><datalist id="adbOptions"></datalist></div>
        <div class="field click-field"><label>桌面点击 X</label><input id="ClickX" inputmode="numeric"></div>
        <div class="field click-field"><label>桌面点击 Y</label><input id="ClickY" inputmode="numeric"></div>
        <div class="field adb-tap-field"><label>ADB 点击 X</label><input id="ADBTapX" inputmode="numeric"></div>
        <div class="field adb-tap-field"><label>ADB 点击 Y</label><input id="ADBTapY" inputmode="numeric"></div>
      </div>
      <div class="actions">
        <button id="scanAdbBtn" class="secondary">扫描 ADB 设备</button>
        <button id="adbScreenshotBtn" class="secondary">截取 ADB 屏幕点选</button>
        <button data-save="page">保存翻页方式</button>
        <button id="testPageBtn" class="secondary">测试翻页</button>
      </div>
      <div id="pageResult" class="result hidden"></div>
      <div class="preview hidden" id="adbScreenshotBox">
        <img id="adbScreenshotImage" class="pickable" alt="ADB 设备屏幕截图">
        <div class="notice">点击截图中的下一页位置，WebUI 会按安卓设备原始屏幕分辨率填入 ADB 点击坐标。</div>
      </div>
    </section>

    <section class="panel step-panel hidden" data-step="3">
      <h2>4. 保存目录</h2>
      <p class="hint">目录可以是相对项目根目录的路径，也可以是绝对路径。</p>
      <div class="grid">
        <div class="field"><label>图片保存目录</label><input id="PictureDir"></div>
        <div class="field"><label>OCR 文本目录</label><input id="OCROutPaDir"></div>
        <div class="field"><label>合并文本目录</label><input id="MergeBookDir"></div>
        <div class="field"><label>最终文本目录</label><input id="FinalNovelDir"></div>
        <div class="field"><label>采集页数</label><input id="CapturePages" inputmode="numeric"></div>
        <div class="field"><label>翻页后等待秒数</label><input id="Cycle" inputmode="decimal"></div>
        <div class="field"><label>阅读误差最小秒</label><input id="ReadingDelayMin" inputmode="decimal"></div>
        <div class="field"><label>阅读误差最大秒</label><input id="ReadingDelayMax" inputmode="decimal"></div>
      </div>
      <div class="actions">
        <label style="display:flex;gap:8px;align-items:center;margin:0;color:var(--ink)">
          <input id="autoMerge" type="checkbox" style="width:auto" checked> 完成采集后自动合并并整理
        </label>
        <button data-save="dirs">保存目录</button>
      </div>
    </section>

    <section class="panel step-panel hidden" data-step="4">
      <h2>5. 开始获取</h2>
      <p class="hint">开始后可以随时重新打开这个 URL 查看当前进度。停止会在当前页 OCR 完成后生效。</p>
      <div class="status-strip">
        <div class="metric"><span>状态</span><strong id="statusText">-</strong></div>
        <div class="metric"><span>页数</span><strong id="pageText">0 / 0</strong></div>
        <div class="metric"><span>开始时间</span><strong id="startedAt">-</strong></div>
        <div class="metric"><span>结束时间</span><strong id="endedAt">-</strong></div>
      </div>
      <div class="bar"><div id="progressBar"></div></div>
      <div class="actions">
        <button id="startBtn">开始获取</button>
        <button id="stopBtn" class="danger">停止</button>
      </div>
      <div class="grid" style="margin-top:14px">
        <div class="metric"><span>合并文本</span><strong id="mergedPath">-</strong></div>
        <div class="metric"><span>最终文本</span><strong id="finalPath">-</strong></div>
      </div>
      <h2 style="margin-top:18px">日志</h2>
      <div id="events" class="events"></div>
    </section>
  </main>

  <script>
    const stepNames = ["API", "图像输入源", "翻页方式", "保存目录", "开始获取"];
    const genericOcrUrl = "https://api.openai.com/v1";
    const localDedicatedOcrUrl = "http://127.0.0.1:8080/v1";
    const genericOcrModel = "gpt-4.1-mini";
    const dedicatedOcrModel = "Unlimited-OCR";
    const genericOcrPrompt = "请对这张小说页面截图进行 OCR。只输出图片中可见的正文文本，保留自然换行，不要解释、不要总结、不要添加图片中不存在的内容。";
    let currentStep = 0;
    let savedSteps = new Set();
    let config = {};
    let inputSources = [];
    let adbDevices = [];
    let adbScreenshotMeta = null;

    const $ = id => document.getElementById(id);
    const api = async (path, options = {}) => {
      const response = await fetch(path, {
        headers: {"Content-Type": "application/json", ...(options.headers || {})},
        ...options
      });
      if (response.status === 401) throw new Error("未登录或会话已过期。");
      const data = await response.json().catch(() => ({}));
      if (!response.ok || data.ok === false) throw new Error(data.error || response.statusText);
      return data;
    };

    function setBusy(button, busy) {
      if (!button) return;
      button.disabled = busy;
    }

    function showResult(id, text, isError = false) {
      const box = $(id);
      box.classList.remove("hidden");
      box.classList.toggle("error", isError);
      box.textContent = text;
    }

    function renderSteps() {
      const nav = $("steps");
      nav.innerHTML = "";
      stepNames.forEach((name, index) => {
        const btn = document.createElement("button");
        btn.className = "step-tab" + (index === currentStep ? " active" : "") + (savedSteps.has(index) ? " done" : "");
        btn.textContent = `${index + 1}. ${name}`;
        btn.onclick = () => setStep(index);
        nav.appendChild(btn);
      });
    }

    function setStep(index) {
      currentStep = index;
      document.querySelectorAll(".step-panel").forEach(panel => {
        panel.classList.toggle("hidden", Number(panel.dataset.step) !== index);
      });
      renderSteps();
    }

    function fillConfig(data) {
      config = data.config || {};
      ["OCRBackend", "OpenAIURL", "OpenAIOCRModel", "OpenAIRequestTimeout", "OpenAIMaxOutputTokens",
       "OpenAIOCRPrompt",
       "InputSource", "InputSourceWarmupFrames", "PageMethod", "ADBSerial", "PictureDir", "OCROutPaDir",
       "MergeBookDir", "FinalNovelDir", "CapturePages", "Cycle", "ReadingDelayMin", "ReadingDelayMax",
       "ADBTapX", "ADBTapY"].forEach(key => {
        if ($(key)) $(key).value = config[key] ?? "";
      });
      $("apiKeyState").value = data.apiKeySet ? "已配置" : "未配置";
      $("ClickX").value = data.clickPlot?.x ?? "";
      $("ClickY").value = data.clickPlot?.y ?? "";
      renderRuntime(data.runtime);
      updatePageFields();
      applyOcrBackendDefaults(true);
    }

    function renderRuntime(runtime) {
      if (!runtime) return;
      const opencv = runtime.opencv || {};
      const lines = [
        `WebUI Python: ${runtime.python}`,
        `Python 版本: ${runtime.pythonVersion}`,
        opencv.ok
          ? `OpenCV: ${opencv.version} (${opencv.file})`
          : `OpenCV: 无法导入 cv2 - ${opencv.error}`,
        opencv.packageVersion ? `opencv-python 包版本: ${opencv.packageVersion}` : "",
        opencv.headlessPackageVersion ? `opencv-python-headless 包版本: ${opencv.headlessPackageVersion}` : ""
      ].filter(Boolean);
      $("runtimeInfo").textContent = lines.join("\n");
      $("runtimeInfo").classList.toggle("error", !opencv.ok);
    }

    function renderDatalist(id, items) {
      const list = $(id);
      list.innerHTML = "";
      items.forEach(item => {
        const option = document.createElement("option");
        option.value = item.label;
        list.appendChild(option);
      });
    }

    function selectedInputSourceId() {
      const value = $("InputSource").value.trim();
      const match = inputSources.find(item => item.label === value);
      return match ? match.id : value;
    }

    function selectedAdbSerial() {
      const value = $("ADBSerial").value.trim();
      const match = adbDevices.find(item => item.label === value);
      return match ? match.serial : value;
    }

    function selectInputSourceById(id) {
      const match = inputSources.find(item => item.id === id);
      $("InputSource").value = match ? match.label : id;
    }

    function selectAdbBySerial(serial) {
      const match = adbDevices.find(item => item.serial === serial);
      $("ADBSerial").value = match ? match.label : serial;
    }

    async function loadConfig() {
      const data = await api("/api/config");
      fillConfig(data);
      $("loginView").classList.add("hidden");
      $("appView").classList.remove("hidden");
      renderSteps();
      pollStatus();
    }

    function updatePageFields() {
      const click = $("PageMethod").value === "模拟点击";
      const adbTap = $("PageMethod").value === "ADB 模拟点击";
      document.querySelectorAll(".click-field").forEach(item => item.classList.toggle("hidden", !click));
      document.querySelectorAll(".adb-tap-field").forEach(item => item.classList.toggle("hidden", !adbTap));
      $("ADBSerial").closest(".field").classList.toggle("hidden", click);
      $("adbScreenshotBtn").classList.toggle("hidden", !adbTap);
      if (!adbTap) $("adbScreenshotBox").classList.add("hidden");
    }

    function applyOcrBackendDefaults(initial = false) {
      const dedicated = $("OCRBackend").value === "专用OCR路径";
      const model = $("OpenAIOCRModel").value.trim();
      const prompt = $("OpenAIOCRPrompt").value.trim();
      if (dedicated) {
        if (!initial || !model || model === genericOcrModel) $("OpenAIOCRModel").value = dedicatedOcrModel;
        if (!$("OpenAIURL").value.trim() || $("OpenAIURL").value.trim() === genericOcrUrl) $("OpenAIURL").value = localDedicatedOcrUrl;
        if (prompt) $("OpenAIOCRPrompt").value = "";
      } else {
        if (model === dedicatedOcrModel) $("OpenAIOCRModel").value = genericOcrModel;
        if (!prompt) $("OpenAIOCRPrompt").value = genericOcrPrompt;
      }
    }

    function apiPayload() {
      applyOcrBackendDefaults(true);
      return {
        OCRBackend: $("OCRBackend").value,
        OpenAIURL: $("OpenAIURL").value,
        OpenAIAPIKEY: $("OpenAIAPIKEY").value,
        OpenAIOCRModel: $("OpenAIOCRModel").value,
        OpenAIRequestTimeout: $("OpenAIRequestTimeout").value,
        OpenAIMaxOutputTokens: $("OpenAIMaxOutputTokens").value,
        OpenAIOCRPrompt: $("OpenAIOCRPrompt").value
      };
    }

    async function saveSection(section, button) {
      setBusy(button, true);
      try {
        const payloads = {
          api: apiPayload(),
          input: {
            CaptureSource: "图像输入源",
            InputSource: selectedInputSourceId(),
            InputSourceWarmupFrames: $("InputSourceWarmupFrames").value
          },
          page: {
            PageMethod: $("PageMethod").value,
            ADBSerial: selectedAdbSerial(),
            ClickX: $("ClickX").value,
            ClickY: $("ClickY").value,
            ADBTapX: $("ADBTapX").value,
            ADBTapY: $("ADBTapY").value
          },
          dirs: {
            PictureDir: $("PictureDir").value,
            OCROutPaDir: $("OCROutPaDir").value,
            MergeBookDir: $("MergeBookDir").value,
            FinalNovelDir: $("FinalNovelDir").value,
            CapturePages: $("CapturePages").value,
            Cycle: $("Cycle").value,
            ReadingDelayMin: $("ReadingDelayMin").value,
            ReadingDelayMax: $("ReadingDelayMax").value
          }
        };
        await api(`/api/config/${section}`, {method: "POST", body: JSON.stringify(payloads[section])});
        savedSteps.add({api:0, input:1, page:2, dirs:3}[section]);
        renderSteps();
        if (section !== "dirs") setStep(currentStep + 1);
      } catch (error) {
        alert(error.message);
      } finally {
        setBusy(button, false);
      }
    }

    async function pollStatus() {
      try {
        const data = await api("/api/status");
        const total = Number(data.total || 0);
        const page = Number(data.page || 0);
        $("statusText").textContent = data.message || data.status || "-";
        $("pageText").textContent = `${page} / ${total}`;
        $("startedAt").textContent = data.startedAt || "-";
        $("endedAt").textContent = data.endedAt || "-";
        $("mergedPath").textContent = data.mergedPath || "-";
        $("finalPath").textContent = data.finalPath || "-";
        $("progressBar").style.width = total ? `${Math.min(100, Math.round(page / total * 100))}%` : "0%";
        $("events").textContent = (data.events || []).map(item => `[${item.time}] ${item.message}`).join("\n");
        $("events").scrollTop = $("events").scrollHeight;
      } catch (error) {
        $("statusText").textContent = error.message;
      } finally {
        setTimeout(pollStatus, 1500);
      }
    }

    $("loginForm").onsubmit = async event => {
      event.preventDefault();
      try {
        await api("/api/login", {method: "POST", body: JSON.stringify({password: $("password").value})});
        await loadConfig();
      } catch (error) {
        showResult("loginError", error.message, true);
      }
    };
    $("logoutBtn").onclick = async () => {
      await api("/api/logout", {method: "POST", body: "{}"});
      location.reload();
    };
    document.querySelectorAll("[data-save]").forEach(button => {
      button.onclick = () => saveSection(button.dataset.save, button);
    });
    $("PageMethod").onchange = updatePageFields;
    $("OCRBackend").onchange = () => applyOcrBackendDefaults();
    $("testApiBtn").onclick = async event => {
      setBusy(event.target, true);
      showResult("apiResult", "正在使用 static\\sample.png 测试 OCR...");
      try {
        await api("/api/config/api", {method: "POST", body: JSON.stringify(apiPayload())});
        const data = await api("/api/test-api", {method: "POST", body: "{}"});
        showResult("apiResult", data.text || "测试完成，但没有返回文本。");
      } catch (error) {
        showResult("apiResult", error.message, true);
      } finally {
        setBusy(event.target, false);
      }
    };
    $("scanSourcesBtn").onclick = async event => {
      setBusy(event.target, true);
      try {
        const current = selectedInputSourceId();
        const data = await api(`/api/input-sources?max=${encodeURIComponent($("scanMax").value)}`);
        inputSources = data.sources || [];
        renderDatalist("sourceOptions", inputSources);
        if (inputSources.length) {
          const selected = inputSources.find(item => item.id === current) || inputSources[0];
          $("InputSource").value = selected.label;
          showResult("sourceList", `可用输入源：\n${inputSources.map(item => item.label).join("\n")}`);
        } else {
          showResult("sourceList", "没有扫描到可用输入源。");
        }
      } catch (error) {
        showResult("sourceList", error.message, true);
      } finally {
        setBusy(event.target, false);
      }
    };
    $("scanAdbBtn").onclick = async event => {
      setBusy(event.target, true);
      try {
        const current = selectedAdbSerial();
        const data = await api("/api/adb-devices");
        adbDevices = data.devices || [];
        renderDatalist("adbOptions", adbDevices);
        if (adbDevices.length) {
          const selected = adbDevices.find(item => item.serial === current) || adbDevices[0];
          $("ADBSerial").value = selected.label;
          showResult("pageResult", `ADB 设备：\n${adbDevices.map(item => item.label).join("\n")}`);
        } else {
          showResult("pageResult", "没有扫描到 ADB 设备。");
        }
      } catch (error) {
        showResult("pageResult", error.message, true);
      } finally {
        setBusy(event.target, false);
      }
    };
    $("adbScreenshotBtn").onclick = async event => {
      setBusy(event.target, true);
      try {
        const data = await api("/api/adb-screenshot", {method: "POST", body: JSON.stringify({
          ADBSerial: selectedAdbSerial()
        })});
        adbScreenshotMeta = data;
        $("ADBSerial").value = data.serial || $("ADBSerial").value;
        $("adbScreenshotImage").src = data.dataUrl;
        $("adbScreenshotBox").classList.remove("hidden");
        showResult("pageResult", "ADB 截屏完成，请在图片上点击下一页位置。");
      } catch (error) {
        showResult("pageResult", error.message, true);
      } finally {
        setBusy(event.target, false);
      }
    };
    $("adbScreenshotImage").onclick = event => {
      const image = $("adbScreenshotImage");
      const rect = image.getBoundingClientRect();
      const naturalWidth = image.naturalWidth || adbScreenshotMeta?.width || 1;
      const naturalHeight = image.naturalHeight || adbScreenshotMeta?.height || 1;
      const x = Math.max(0, Math.min(naturalWidth - 1, Math.round((event.clientX - rect.left) * naturalWidth / rect.width)));
      const y = Math.max(0, Math.min(naturalHeight - 1, Math.round((event.clientY - rect.top) * naturalHeight / rect.height)));
      $("ADBTapX").value = x;
      $("ADBTapY").value = y;
      showResult("pageResult", `已选择 ADB 点击坐标: ${x}, ${y}`);
    };
    $("previewBtn").onclick = async event => {
      setBusy(event.target, true);
      try {
        const data = await api("/api/preview", {method: "POST", body: JSON.stringify({
          InputSource: selectedInputSourceId(),
          InputSourceWarmupFrames: $("InputSourceWarmupFrames").value
        })});
        $("previewImage").src = data.dataUrl;
        $("previewBox").classList.remove("hidden");
      } catch (error) {
        showResult("sourceList", error.message, true);
      } finally {
        setBusy(event.target, false);
      }
    };
    $("testPageBtn").onclick = async event => {
      setBusy(event.target, true);
      try {
        await api("/api/config/page", {method: "POST", body: JSON.stringify({
          PageMethod: $("PageMethod").value,
          ADBSerial: selectedAdbSerial(),
          ClickX: $("ClickX").value,
          ClickY: $("ClickY").value,
          ADBTapX: $("ADBTapX").value,
          ADBTapY: $("ADBTapY").value
        })});
        const data = await api("/api/test-page", {method: "POST", body: "{}"});
        showResult("pageResult", data.message);
      } catch (error) {
        showResult("pageResult", error.message, true);
      } finally {
        setBusy(event.target, false);
      }
    };
    $("startBtn").onclick = async event => {
      setBusy(event.target, true);
      try {
        await saveSection("dirs", document.querySelector("[data-save='dirs']"));
        await api("/api/start", {method: "POST", body: JSON.stringify({autoMerge: $("autoMerge").checked})});
        savedSteps.add(4);
        renderSteps();
      } catch (error) {
        alert(error.message);
      } finally {
        setBusy(event.target, false);
      }
    };
    $("stopBtn").onclick = async () => api("/api/stop", {method: "POST", body: "{}"});
    loadConfig().catch(() => {
      $("loginView").classList.remove("hidden");
      $("appView").classList.add("hidden");
    });
  </script>
</body>
</html>
"""


def now_text() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def add_event(message: str, **payload: Any) -> None:
    with STATE_LOCK:
        STATE["message"] = message
        if "page" in payload:
            STATE["page"] = payload["page"]
        if "total" in payload:
            STATE["total"] = payload["total"]
        STATE["events"].append({"time": now_text(), "message": message})
        if len(STATE["events"]) > MAX_EVENTS:
            STATE["events"] = STATE["events"][-MAX_EVENTS:]


def public_config() -> Dict[str, Any]:
    config = load_config()
    hidden = dict(config)
    hidden["OpenAIAPIKEY"] = ""
    hidden["WebUIPassword"] = ""
    click_plot: Dict[str, int] = {}
    click_path = PROJECT_ROOT / "data" / "ClickPlot.json"
    if click_path.exists():
        try:
            click_plot = json.loads(click_path.read_text(encoding="utf-8"))
        except Exception:
            click_plot = {}
    return {
        "ok": True,
        "config": hidden,
        "apiKeySet": bool(str(config.get("OpenAIAPIKEY") or "").strip()),
        "clickPlot": click_plot,
        "runtime": runtime_info(),
    }


def package_version(package_name: str) -> str:
    try:
        from importlib.metadata import version

        return version(package_name)
    except Exception:
        return ""


def runtime_info() -> Dict[str, Any]:
    opencv: Dict[str, Any] = {
        "ok": False,
        "version": "",
        "file": "",
        "error": "",
        "packageVersion": package_version("opencv-python"),
        "headlessPackageVersion": package_version("opencv-python-headless"),
    }
    try:
        import cv2

        opencv.update(
            {
                "ok": True,
                "version": getattr(cv2, "__version__", ""),
                "file": getattr(cv2, "__file__", ""),
                "error": "",
            }
        )
    except Exception as exc:
        opencv["error"] = f"{type(exc).__name__}: {exc}"

    return {
        "python": sys.executable,
        "pythonVersion": sys.version.split()[0],
        "opencv": opencv,
    }


def address_family_for_host(host: str) -> str:
    return "IPv6" if ":" in str(host) else "IPv4"


def build_server_class(host: str) -> type[ThreadingHTTPServer]:
    if address_family_for_host(host) == "IPv6":
        class IPv6ThreadingHTTPServer(ThreadingHTTPServer):
            address_family = socket.AF_INET6

        return IPv6ThreadingHTTPServer

    class IPv4ThreadingHTTPServer(ThreadingHTTPServer):
        address_family = socket.AF_INET

    return IPv4ThreadingHTTPServer


def server_address(host: str, port: int) -> tuple[Any, ...]:
    if address_family_for_host(host) == "IPv6":
        return (host, port, 0, 0)
    return (host, port)


def read_image_data_url(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def merge_config(updates: Dict[str, Any], keep_empty_api_key: bool = False) -> Dict[str, Any]:
    config = load_config()
    for key, value in updates.items():
        if key == "OpenAIAPIKEY" and keep_empty_api_key and not str(value or "").strip():
            continue
        config[key] = str(value)
    save_config(config)
    ensure_project_dirs(config)
    return config


def handle_config_section(section: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if section == "api":
        allowed = {
            "OCRBackend",
            "OpenAIURL",
            "OpenAIAPIKEY",
            "OpenAIOCRModel",
            "OpenAIRequestTimeout",
            "OpenAIMaxOutputTokens",
            "OpenAIOCRPrompt",
        }
        updates = {key: payload.get(key, "") for key in allowed if key in payload}
        if str(updates.get("OCRBackend") or "").strip() == "专用OCR路径":
            if not str(updates.get("OpenAIOCRModel") or "").strip() or updates.get("OpenAIOCRModel") == DEFAULT_CONFIG["OpenAIOCRModel"]:
                updates["OpenAIOCRModel"] = "Unlimited-OCR"
            if str(updates.get("OpenAIURL") or "").strip() in ("", str(DEFAULT_CONFIG["OpenAIURL"])):
                updates["OpenAIURL"] = "http://127.0.0.1:8080/v1"
            updates["OpenAIOCRPrompt"] = ""
        merge_config(updates, keep_empty_api_key=True)
        return public_config()

    if section == "input":
        updates = {
            "CaptureSource": "图像输入源",
            "InputSource": payload.get("InputSource", "0"),
            "InputSourceWarmupFrames": payload.get("InputSourceWarmupFrames", "5"),
        }
        merge_config(updates)
        return public_config()

    if section == "page":
        method = str(payload.get("PageMethod") or "音量下")
        if method not in ("音量下", "音量上", "模拟点击", "ADB 模拟点击"):
            raise ValueError("WebUI 只支持音量上、音量下、模拟点击或 ADB 模拟点击翻页。")
        updates = {"PageMethod": method, "ADBSerial": payload.get("ADBSerial", "")}
        if method == "模拟点击":
            x = int(str(payload.get("ClickX") or "").strip())
            y = int(str(payload.get("ClickY") or "").strip())
            save_click_plot(x, y)
        elif method == "ADB 模拟点击":
            x = int(str(payload.get("ADBTapX") or "").strip())
            y = int(str(payload.get("ADBTapY") or "").strip())
            if x < 0 or y < 0:
                raise ValueError("ADB 点击坐标不能为负数。")
            updates.update({"ADBTapX": x, "ADBTapY": y})
        merge_config(updates)
        return public_config()

    if section == "dirs":
        allowed = {
            "PictureDir",
            "OCROutPaDir",
            "MergeBookDir",
            "FinalNovelDir",
            "CapturePages",
            "Cycle",
            "ReadingDelayMin",
            "ReadingDelayMax",
        }
        updates = {key: payload.get(key, "") for key in allowed if key in payload}
        preview = load_config()
        preview.update({key: str(value) for key, value in updates.items()})
        int(preview.get("CapturePages") or 1)
        float(preview.get("Cycle") or 1)
        minimum = float(preview.get("ReadingDelayMin") or 0)
        maximum = float(preview.get("ReadingDelayMax") or 0)
        if minimum < 0 or maximum < 0:
            raise ValueError("阅读误差秒数不能为负数。")
        merge_config(updates)
        return public_config()

    raise ValueError(f"未知配置步骤: {section}")


def run_task(auto_merge: bool) -> None:
    global STOP_EVENT
    from .. import workflow

    config = load_config()
    config["CaptureSource"] = "图像输入源"
    save_config(config)
    with STATE_LOCK:
        STATE.update(
            {
                "running": True,
                "status": "running",
                "message": "正在启动采集。",
                "page": 0,
                "total": int(config.get("CapturePages") or 0),
                "startedAt": now_text(),
                "endedAt": "",
                "error": "",
                "captured": 0,
                "mergedPath": "",
                "finalPath": "",
                "events": [],
            }
        )
    add_event("任务已启动。")
    try:
        captured = workflow.run_capture(config, STOP_EVENT, lambda message, payload: add_event(message, **payload))
        with STATE_LOCK:
            STATE["captured"] = captured
        if STOP_EVENT and STOP_EVENT.is_set():
            add_event("任务已请求停止。")
            with STATE_LOCK:
                STATE["status"] = "stopped"
        elif auto_merge:
            add_event("开始合并 OCR 文本。")
            merged = workflow.merge_book(config, lambda message, payload: add_event(message, **payload))
            with STATE_LOCK:
                STATE["mergedPath"] = merged
            add_event("开始整理最终文本。")
            final = workflow.format_book(merged, config, lambda message, payload: add_event(message, **payload))
            with STATE_LOCK:
                STATE["finalPath"] = final
                STATE["status"] = "completed"
        else:
            with STATE_LOCK:
                STATE["status"] = "completed"
        add_event("任务完成。")
    except Exception as exc:
        with STATE_LOCK:
            STATE["status"] = "error"
            STATE["error"] = str(exc)
        add_event(f"任务失败: {exc}")
    finally:
        with STATE_LOCK:
            STATE["running"] = False
            STATE["endedAt"] = now_text()
        STOP_EVENT = None


class WebUIHandler(BaseHTTPRequestHandler):
    server_version = "GermenWebUI/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[{now_text()}] {self.address_string()} {fmt % args}")

    def is_authenticated(self) -> bool:
        cookie = SimpleCookie(self.headers.get("Cookie"))
        morsel = cookie.get(SESSION_COOKIE)
        return bool(morsel and morsel.value in SESSIONS)

    def read_json(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw or "{}")

    def send_bytes(self, data: bytes, content_type: str, status: int = 200, headers: Optional[Dict[str, str]] = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, data: Dict[str, Any], status: int = 200, headers: Optional[Dict[str, str]] = None) -> None:
        self.send_bytes(
            json.dumps(data, ensure_ascii=False).encode("utf-8"),
            "application/json; charset=utf-8",
            status,
            headers,
        )

    def require_auth(self) -> bool:
        if self.is_authenticated():
            return True
        self.send_json({"ok": False, "error": "未登录。"}, HTTPStatus.UNAUTHORIZED)
        return False

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            if path == "/":
                self.send_bytes(INDEX_HTML.encode("utf-8"), "text/html; charset=utf-8")
                return
            if path == "/api/config":
                if not self.require_auth():
                    return
                self.send_json(public_config())
                return
            if path == "/api/status":
                if not self.require_auth():
                    return
                with STATE_LOCK:
                    self.send_json({"ok": True, **STATE})
                return
            if path == "/api/input-sources":
                if not self.require_auth():
                    return
                from .. import workflow

                query = dict(item.split("=", 1) for item in parsed.query.split("&") if "=" in item)
                max_index = int(query.get("max") or 8)
                self.send_json({"ok": True, "sources": workflow.list_input_source_details(max_index)})
                return
            if path == "/api/adb-devices":
                if not self.require_auth():
                    return
                from .. import workflow

                self.send_json({"ok": True, "devices": workflow.list_adb_devices()})
                return
            if path.startswith("/static/"):
                self.serve_static(path)
                return
            self.send_json({"ok": False, "error": "Not found"}, HTTPStatus.NOT_FOUND)
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def serve_static(self, path: str) -> None:
        relative = unquote(path.removeprefix("/static/"))
        target = (PROJECT_ROOT / "static" / relative).resolve()
        static_root = (PROJECT_ROOT / "static").resolve()
        if not str(target).startswith(str(static_root)) or not target.exists() or not target.is_file():
            self.send_json({"ok": False, "error": "Not found"}, HTTPStatus.NOT_FOUND)
            return
        content_type = "image/png" if target.suffix.lower() == ".png" else "application/octet-stream"
        self.send_bytes(target.read_bytes(), content_type)

    def do_POST(self) -> None:
        global STOP_EVENT, TASK_THREAD
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            payload = self.read_json()
            if path == "/api/login":
                config = load_config()
                expected = str(config.get("WebUIPassword") or DEFAULT_CONFIG["WebUIPassword"])
                if secrets.compare_digest(str(payload.get("password") or ""), expected):
                    token = secrets.token_urlsafe(32)
                    SESSIONS.add(token)
                    self.send_json(
                        {"ok": True},
                        headers={
                            "Set-Cookie": f"{SESSION_COOKIE}={token}; HttpOnly; SameSite=Lax; Path=/",
                        },
                    )
                    return
                self.send_json({"ok": False, "error": "访问密码不正确。"}, HTTPStatus.FORBIDDEN)
                return
            if not self.require_auth():
                return
            if path == "/api/logout":
                cookie = SimpleCookie(self.headers.get("Cookie"))
                morsel = cookie.get(SESSION_COOKIE)
                if morsel:
                    SESSIONS.discard(morsel.value)
                self.send_json(
                    {"ok": True},
                    headers={"Set-Cookie": f"{SESSION_COOKIE}=; Max-Age=0; SameSite=Lax; Path=/"},
                )
                return
            if path.startswith("/api/config/"):
                section = path.rsplit("/", 1)[-1]
                self.send_json(handle_config_section(section, payload))
                return
            if path == "/api/test-api":
                from .. import openai_ocr

                sample = PROJECT_ROOT / "static" / "sample.png"
                if not sample.exists():
                    raise FileNotFoundError("static\\sample.png 不存在。")
                text = openai_ocr.recognize_image(str(sample), load_config())
                self.send_json({"ok": True, "text": text})
                return
            if path == "/api/preview":
                from .. import frame_sources

                config = load_config()
                source = str(payload.get("InputSource") or config.get("InputSource") or "0")
                warmup = int(payload.get("InputSourceWarmupFrames") or config.get("InputSourceWarmupFrames") or 5)
                preview_dir = PROJECT_ROOT / "static" / "web_preview"
                image_path = frame_sources.capture_input_source(preview_dir, source, warmup)
                self.send_json({"ok": True, "dataUrl": read_image_data_url(image_path), "path": str(image_path)})
                return
            if path == "/api/adb-screenshot":
                from .. import workflow

                config = load_config()
                if "ADBSerial" in payload:
                    config["ADBSerial"] = str(payload.get("ADBSerial") or "")
                screenshot = workflow.capture_adb_screenshot(config)
                config["ADBSerial"] = screenshot["serial"]
                save_config(config)
                image_path = Path(str(screenshot["path"]))
                self.send_json(
                    {
                        "ok": True,
                        "dataUrl": read_image_data_url(image_path),
                        "path": str(image_path),
                        "serial": screenshot["serial"],
                        "width": screenshot["width"],
                        "height": screenshot["height"],
                    }
                )
                return
            if path == "/api/test-page":
                config = load_config()
                method = str(config.get("PageMethod") or "音量下")
                if method == "模拟点击":
                    from .. import click

                    click.ClickToNextPage()
                    self.send_json({"ok": True, "message": "已执行一次服务器端模拟点击。"})
                    return
                from .. import adb_controller

                serial = adb_controller.connect(str(config.get("ADBSerial") or ""))
                if method == "ADB 模拟点击":
                    x = int(str(config.get("ADBTapX") or "").strip())
                    y = int(str(config.get("ADBTapY") or "").strip())
                    adb_controller.tap(serial, x, y)
                    config["ADBSerial"] = serial
                    save_config(config)
                    self.send_json({"ok": True, "message": f"已向 {serial} 发送 ADB 点击: {x}, {y}。"})
                    return
                key = "KEYCODE_VOLUME_UP" if method == "音量上" else "KEYCODE_VOLUME_DOWN"
                adb_controller.keyevent(serial, key)
                config["ADBSerial"] = serial
                save_config(config)
                self.send_json({"ok": True, "message": f"已向 {serial} 发送 {method}。"})
                return
            if path == "/api/start":
                with STATE_LOCK:
                    if STATE["running"]:
                        self.send_json({"ok": False, "error": "已有任务正在运行。"}, HTTPStatus.CONFLICT)
                        return
                STOP_EVENT = threading.Event()
                TASK_THREAD = threading.Thread(target=run_task, args=(bool(payload.get("autoMerge", True)),), daemon=True)
                TASK_THREAD.start()
                self.send_json({"ok": True})
                return
            if path == "/api/stop":
                if STOP_EVENT:
                    STOP_EVENT.set()
                add_event("已收到停止请求。")
                self.send_json({"ok": True})
                return
            self.send_json({"ok": False, "error": "Not found"}, HTTPStatus.NOT_FOUND)
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)


def parse_args(argv: list[str] | None = None, prog: str | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=prog, description="启动 Germen WebUI。")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址，例如 127.0.0.1、0.0.0.0、::1 或 ::。")
    parser.add_argument("--port", default=7860, type=int, help="监听端口。")
    args = parser.parse_args(argv)
    if args.port < 1 or args.port > 65535:
        parser.error("--port 必须在 1 到 65535 之间。")
    return args


def main(argv: list[str] | None = None, prog: str | None = None) -> None:
    args = parse_args(argv, prog)
    host = str(args.host)
    port = int(args.port)
    family = address_family_for_host(host)
    server_class = build_server_class(host)
    server = server_class(server_address(host, port), WebUIHandler)
    display_host = f"[{host}]" if family == "IPv6" and not host.startswith("[") else host
    print(f"Germen WebUI: http://{display_host}:{port}/")
    print(f"监听协议: {family}")
    print("访问密码在 config.json 的 WebUIPassword 中设置。")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nWebUI 已停止。")


if __name__ == "__main__":
    main()
