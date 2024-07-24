#获取模拟点击坐标的程序
import tkinter as tk
import numpy as np
import logging

# 设置日志
logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG,
                    filename='./log/click.log',
                    filemode='a')

print('请选取小说的阅读页面的模拟点击目标。')

#定义一个透明的窗口，让它的大小与屏幕一样
root = tk.Tk()
root.overrideredirect(True)         # 隐藏窗口的标题栏
root.attributes("-alpha", 0.1)      # 窗口透明度10%
root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
root.configure(bg="black")
#alhpa参数用于设定透明度；geometry函数用于设定窗口大小

#记录点击坐标：
def button_1(event):
    global x, y
    x, y = event.x, event.y
    # print("event.x, event.y = ", event.x, event.y)
    savexyplot(x, y)
    sys_out(button_1)
    logging.info(f"获取点击坐标x：{x}，y：{y}")





#保存坐标
def savexyplot(x1,y1):
    xyclickplot={"x":x1,"y":y1}
    np.save('.//data/ClickPlot.npy', xyclickplot)
    logging.info(f"保存点击坐标至文件：.//data/ClickPlot.npy")


#退出程序
def sys_out(even):
    logging.info(f"检测到用户按下ESC键，退出获取模拟点击坐标程序。")
    root.destroy()

#监听鼠标和键盘事件，实时监控框选区域和截屏
root.bind('<Escape>',sys_out)      # 键盘Esc键->退出
root.bind("<Button-1>", button_1)  # 鼠标左键点击->记录点击坐标
root.mainloop()