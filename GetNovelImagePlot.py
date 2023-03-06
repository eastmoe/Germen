#获取截图坐标的程序
import tkinter as tk
import numpy as np
#from tkinter import messagebox
#import pyautogui

print('请选取小说的阅读页面，不需要包含边框，建议提高对比度以改善OCR文字识别效率。')

#定义一个透明的窗口，让它的大小与屏幕一样
root = tk.Tk()
root.overrideredirect(True)         # 隐藏窗口的标题栏
root.attributes("-alpha", 0.1)      # 窗口透明度10%
root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
root.configure(bg="black")
#alhpa参数用于设定透明度；geometry函数用于设定窗口大小

#创建一个子窗口，用于显示框选区域
cv = tk.Canvas(root)
x, y = 0, 0
xstart,ystart = 0 ,0
xend,yend = 0, 0
rec = ''


#监听鼠标光标位置：
def move(event):
    global x, y ,xstart,ystart
    new_x = (event.x-x)+tk.Canvas.winfo_x()
    new_y = (event.y-y)+tk.Canvas.winfo_y()
    s = "300x200+" + str(new_x)+"+" + str(new_y)
    tk.Canvas.place(x = new_x - xstart,y = new_y -ystart)
    print("s = ", s)
    print(root.winfo_x(), root.winfo_y())
    print(event.x, event.y)

#创建子窗口：
def button_1(event):
    global x, y ,xstart,ystart
    global rec
    x, y = event.x, event.y
    xstart,ystart = event.x, event.y
    print("event.x, event.y = ", event.x, event.y)
    xstart,ystart = event.x, event.y
    cv.configure(height=1)
    cv.configure(width=1)
    cv.config(highlightthickness=0) # 无边框
    cv.place(x=event.x, y=event.y)
    rec = cv.create_rectangle(0,0,0,0,outline='red',width=8,dash=(4, 4))

#改变子窗口大小：
def b1_Motion(event):
    global x, y,xstart,ystart
    x, y = event.x, event.y
    print("event.x, event.y = ", event.x, event.y)
    cv.configure(height = event.y - ystart)
    cv.configure(width = event.x - xstart)
    cv.coords(rec,0,0,event.x-xstart,event.y-ystart)


#松开鼠标，记录最后的光标位置
def buttonRelease_1(event):
    global xend,yend
    xend, yend = event.x, event.y
    savexyplot(xstart,ystart,xend,yend)
    #保存当前截图坐标到字典文件
    sys_out(None)

#保存坐标
def savexyplot(x1,y1,x2,y2):
    xyplot={"xstart":x1,"ystart":y1,"xend":x2,"yend":y2}
    print(xyplot)
    np.save('.//data/ImagePlot.npy', xyplot)

#退出程序
def sys_out(even):
    root.destroy()



#监听鼠标和键盘事件，实时监控框选区域和截屏
#tk.Canvas.bind("<B1-Motion>",pyautogui.move)   # 鼠标左键移动->显示当前光标位置
root.bind('<Escape>',sys_out)      # 键盘Esc键->退出
root.bind("<Button-1>", button_1)  # 鼠标左键点击->显示子窗口
root.bind("<B1-Motion>", b1_Motion)# 鼠标左键移动->改变子窗口大小
root.bind("<ButtonRelease-1>", buttonRelease_1) # 鼠标左键释放->记录最后光标的位置
#root.bind("<Button-3>",button_3)   #鼠标右键点击->截屏并保存图片
root.mainloop()