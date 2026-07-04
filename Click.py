#模拟鼠标点击程序
from coordinates import load_click_plot
import win_input


def ClickToNextPage():
    xyclickplot = load_click_plot()
    # 从文件加载坐标

    print(xyclickplot)

    x = xyclickplot.get("x")
    y = xyclickplot.get("y")
    # 将坐标赋予变量

    win_input.click(x, y)

    return 0

def TestFeature():
    #while True:
        ClickToNextPage()
        import Memory
        Memory.ShowMemoryType()


if __name__ == "__main__":
    TestFeature()
