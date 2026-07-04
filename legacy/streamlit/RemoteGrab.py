import streamlit as st

import mss
import mss.tools


def capture_screenshot():
    with mss.mss() as sct:
        screenshot = sct.shot(output="screenshot.png")
    return "screenshot.png"

def main():
    st.title("远程桌面截图工具")

    if st.button("捕获屏幕截图"):
        screenshot_path = capture_screenshot()
        st.image(screenshot_path, caption="全屏截图", use_column_width=True)



if __name__ == "__main__":
    main()
