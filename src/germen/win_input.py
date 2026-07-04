import ctypes
import time
from ctypes import wintypes


user32 = ctypes.WinDLL("user32", use_last_error=True)

HWND_TOPMOST = -1
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOOWNERZORDER = 0x0200
SWP_DRAWFRAME = 0x0020
SWP_SHOWWINDOW = 0x0040

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
KEYEVENTF_KEYUP = 0x0002

VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12

SPECIAL_KEYS = {
    "backspace": 0x08,
    "tab": 0x09,
    "enter": 0x0D,
    "return": 0x0D,
    "shift": VK_SHIFT,
    "ctrl": VK_CONTROL,
    "control": VK_CONTROL,
    "alt": VK_MENU,
    "pause": 0x13,
    "capslock": 0x14,
    "esc": 0x1B,
    "escape": 0x1B,
    "space": 0x20,
    "pageup": 0x21,
    "pgup": 0x21,
    "pagedown": 0x22,
    "pgdn": 0x22,
    "end": 0x23,
    "home": 0x24,
    "left": 0x25,
    "up": 0x26,
    "right": 0x27,
    "down": 0x28,
    "insert": 0x2D,
    "delete": 0x2E,
}

for number in range(1, 13):
    SPECIAL_KEYS[f"f{number}"] = 0x6F + number


def _raise_last_error(action: str) -> None:
    error = ctypes.get_last_error()
    if error:
        raise OSError(error, f"{action} 失败")


def click(x: int, y: int) -> None:
    if not user32.SetCursorPos(int(x), int(y)):
        _raise_last_error("设置鼠标位置")
    time.sleep(0.03)
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def pin_foreground_window() -> None:
    handle = user32.GetForegroundWindow()
    if not handle:
        _raise_last_error("获取当前活动窗口")
    result = user32.SetWindowPos(
        handle,
        HWND_TOPMOST,
        0,
        0,
        0,
        0,
        SWP_NOMOVE | SWP_DRAWFRAME | SWP_NOSIZE | SWP_NOOWNERZORDER | SWP_SHOWWINDOW,
    )
    if not result:
        _raise_last_error("置顶当前活动窗口")


def _key_event(vk_code: int, flags: int = 0) -> None:
    user32.keybd_event(wintypes.BYTE(vk_code), wintypes.BYTE(0), wintypes.DWORD(flags), 0)


def _press_vk(vk_code: int) -> None:
    _key_event(vk_code)
    time.sleep(0.03)
    _key_event(vk_code, KEYEVENTF_KEYUP)


def _vk_from_token(token: str) -> tuple[int, bool, bool, bool]:
    normalized = token.strip().lower()
    if normalized in SPECIAL_KEYS:
        return SPECIAL_KEYS[normalized], False, False, False
    if len(token) != 1:
        raise ValueError(f"不支持的按键名称: {token}")

    result = user32.VkKeyScanW(token)
    if result == -1:
        raise ValueError(f"无法映射按键: {token}")
    vk_code = result & 0xFF
    shift_state = (result >> 8) & 0xFF
    return vk_code, bool(shift_state & 1), bool(shift_state & 2), bool(shift_state & 4)


def press_and_release(key: str) -> None:
    key = str(key).strip()
    if not key:
        raise ValueError("翻页按键不能为空。")

    tokens = [part.strip() for part in key.replace("+", " ").split() if part.strip()]
    if len(tokens) > 1:
        modifiers = []
        for token in tokens[:-1]:
            vk_code, _, _, _ = _vk_from_token(token)
            modifiers.append(vk_code)
        target_vk, needs_shift, needs_ctrl, needs_alt = _vk_from_token(tokens[-1])
        if needs_shift:
            modifiers.append(VK_SHIFT)
        if needs_ctrl:
            modifiers.append(VK_CONTROL)
        if needs_alt:
            modifiers.append(VK_MENU)
        for modifier in modifiers:
            _key_event(modifier)
        _press_vk(target_vk)
        for modifier in reversed(modifiers):
            _key_event(modifier, KEYEVENTF_KEYUP)
        return

    target_vk, needs_shift, needs_ctrl, needs_alt = _vk_from_token(key)
    modifiers = []
    if needs_shift:
        modifiers.append(VK_SHIFT)
    if needs_ctrl:
        modifiers.append(VK_CONTROL)
    if needs_alt:
        modifiers.append(VK_MENU)
    for modifier in modifiers:
        _key_event(modifier)
    _press_vk(target_vk)
    for modifier in reversed(modifiers):
        _key_event(modifier, KEYEVENTF_KEYUP)
