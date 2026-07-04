import base64
import datetime
import mimetypes
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, Optional

from openai import OpenAI

from app_config import DEFAULT_CONFIG, load_config, resolve_path
from log_utils import get_logger


logger = get_logger("germen.openai_ocr", "ocr.log")
GENERIC_VLM_BACKEND = "通用VLM路径"
DEDICATED_OCR_BACKEND = "专用OCR路径"
COORDINATE_PREFIX_RE = re.compile(
    r"^\s*(?:text\s*)?\[\s*-?\d+\s*,\s*-?\d+\s*,\s*-?\d+\s*,\s*-?\d+\s*\]\s*",
    re.IGNORECASE,
)


def _image_data_url(image_path: Path) -> str:
    mime_type = mimetypes.guess_type(image_path.name)[0] or "image/png"
    with image_path.open("rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _get_client(config: Dict[str, Any]) -> OpenAI:
    api_key = str(config.get("OpenAIAPIKEY") or os.getenv("OPENAI_API_KEY") or "").strip()
    base_url = str(config.get("OpenAIURL") or os.getenv("OPENAI_BASE_URL") or "").strip()
    timeout = float(config.get("OpenAIRequestTimeout") or 120)
    if not api_key:
        normalized_url = base_url.rstrip("/").lower()
        if not base_url or normalized_url in {"https://api.openai.com/v1", "https://api.openai.com"}:
            raise RuntimeError("请先在 config.json 的 OpenAIAPIKEY 或环境变量 OPENAI_API_KEY 中配置 API Key。")
        api_key = "not-needed"
    if base_url:
        return OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
    return OpenAI(api_key=api_key, timeout=timeout)


def _is_dedicated_ocr(config: Dict[str, Any]) -> bool:
    backend = re.sub(r"[\s_-]+", "", str(config.get("OCRBackend") or GENERIC_VLM_BACKEND).strip().lower())
    return backend in {
        "专用ocr路径",
        "专用ocr",
        "dedicatedocr",
        "deepseekocr",
        "unlimitedocr",
        "ocr",
    }


def _config_bool(config: Dict[str, Any], key: str, default: bool) -> bool:
    value = config.get(key)
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on", "是", "启用"}


def _strip_coordinate_prefixes(text: str) -> str:
    lines = []
    for line in text.splitlines():
        lines.append(COORDINATE_PREFIX_RE.sub("", line).rstrip())
    return "\n".join(lines).strip()


def _extract_response_text(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if output_text:
        return output_text.strip()

    chunks = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                chunks.append(text)
    return "\n".join(chunks).strip()


def _extract_chat_text(response: Any) -> str:
    text = (response.choices[0].message.content or "").strip()
    if not text:
        raise RuntimeError("OpenAI OCR 返回为空。")
    return text


def _ocr_with_responses_api(client: OpenAI, image_url: str, config: Dict[str, Any]) -> str:
    prompt = str(config.get("OpenAIOCRPrompt") or "").strip()
    model = str(config.get("OpenAIOCRModel") or "gpt-4.1-mini").strip()
    max_tokens = int(config.get("OpenAIMaxOutputTokens") or 4096)

    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": image_url},
                ],
            }
        ],
        temperature=0,
        max_output_tokens=max_tokens,
    )
    text = _extract_response_text(response)
    if not text:
        raise RuntimeError("OpenAI OCR 返回为空。")
    return text


def _ocr_with_chat_completions(client: OpenAI, image_url: str, config: Dict[str, Any]) -> str:
    prompt = str(config.get("OpenAIOCRPrompt") or "").strip()
    model = str(config.get("OpenAIOCRModel") or "gpt-4.1-mini").strip()
    max_tokens = int(config.get("OpenAIMaxOutputTokens") or 4096)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        temperature=0,
        max_tokens=max_tokens,
    )
    return _extract_chat_text(response)


def _ocr_with_dedicated_model(client: OpenAI, image_url: str, config: Dict[str, Any]) -> str:
    model = str(config.get("OpenAIOCRModel") or "").strip()
    if not model or model == DEFAULT_CONFIG["OpenAIOCRModel"]:
        model = "Unlimited-OCR"
    max_tokens = int(config.get("OpenAIMaxOutputTokens") or 4096)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        temperature=0,
        max_tokens=max_tokens,
    )
    text = _extract_chat_text(response)
    if _config_bool(config, "DedicatedOCRStripCoordinates", True):
        text = _strip_coordinate_prefixes(text)
    if not text:
        raise RuntimeError("专用 OCR 返回为空。")
    return text


def recognize_image(PicturePath: str, config: Optional[Dict[str, Any]] = None) -> str:
    config = config or load_config()
    image_path = resolve_path(PicturePath)
    if not image_path.exists():
        raise FileNotFoundError(f"图片文件不存在: {image_path}")

    dedicated_ocr = _is_dedicated_ocr(config)
    backend_name = DEDICATED_OCR_BACKEND if dedicated_ocr else GENERIC_VLM_BACKEND
    logger.info("%s start: %s", backend_name, datetime.datetime.now())
    image_url = _image_data_url(image_path)
    client = _get_client(config)

    if dedicated_ocr:
        text = _ocr_with_dedicated_model(client, image_url, config)
    else:
        if hasattr(client, "responses"):
            text = _ocr_with_responses_api(client, image_url, config)
        else:
            text = _ocr_with_chat_completions(client, image_url, config)

    logger.info("%s end: %s", backend_name, datetime.datetime.now())
    return text


def OCR(PicturePath: str, OCROutPath: str, config: Optional[Dict[str, Any]] = None) -> str:
    config = config or load_config()
    output_dir = resolve_path(OCROutPath)
    output_dir.mkdir(parents=True, exist_ok=True)
    text = recognize_image(PicturePath, config)

    output_path = output_dir / f"{time.strftime('%Y-%m-%d-%H-%M-%S')}.txt"
    suffix = 1
    while output_path.exists():
        output_path = output_dir / f"{time.strftime('%Y-%m-%d-%H-%M-%S')}-{suffix}.txt"
        suffix += 1

    output_path.write_text(text, encoding="utf-8")
    logger.info("OpenAI OCR saved text: %s", output_path)
    return str(output_path)
