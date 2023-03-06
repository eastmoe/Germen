#模拟鼠标点击程序
import numpy as np
import pyautogui

def ClickToNextPage():
    xyclickplot = np.load('.//data/ClickPlot.npy', allow_pickle=True).item()
    # 从文件加载坐标

    print(xyclickplot)

    x = xyclickplot.get("x")
    y = xyclickplot.get("y")
    # 将坐标赋予变量

    pyautogui.click(x, y)

    return 0

