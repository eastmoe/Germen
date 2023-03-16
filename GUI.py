# 图形用户程序，便于使用
import json
import os
# 导入tkinter模块
import tkinter as tk
import tkinter.ttk as ttk

#定义全局变量
OCROutPaDir=""
MergeBookDir=""
FinalNovelDir=""
Cycle=""
UseOldImagePlot=""
UseOldClickPlot=""

# 函数，加载配置，返回各个函数所需的路径和周期
def loadconfig():
    print("加载配置文件.....")
    with open("config.json", encoding='gb18030') as config:
        ConfigInfo = json.load(config)
    PictureDir = ConfigInfo["PictureDir"]
    # 设置窗体默认值
    entryPictureDir.insert(0, PictureDir)
    OCROutPaDir = ConfigInfo["OCROutPaDir"]
    entryOCROutPaDir.insert(0, OCROutPaDir)
    MergeBookDir = ConfigInfo["MergeBookDir"]
    entryMergeBookDir.insert(0, MergeBookDir)
    FinalNovelDir = ConfigInfo["FinalNovelDir"]
    entryFinalNovelDir.insert(0, FinalNovelDir)
    Cycle = ConfigInfo["Cycle"]
    entryCycle.insert(0, Cycle)
    # return PictureDir,OCROutPaDir,MergeBookDir,FinalNovelDir,Cycle

# 定义一个函数，用于读取复选框的状态，
def getplotstate():
    UseOldImagePlot = checkUseOldImagePlot.getvar()
    UseOldClickPlot = checkUseOldClickPlot.getvar()

# 定义函数，获取截图区域及点击坐标
def getPicturePlot():
    # 执行Python程序，获取截图区域
    os.system('python GetNovelImagePlot.py')
def getClickPlot():
    # 执行Python程序，获取点击位置
    os.system('python GetClickPlot.py')


# 创建一个窗体对象
root = tk.Tk()

# 设置窗体标题
root.title("Germen GUI")

# 设置窗体大小
root.geometry("340x300")

# 创建标签对象，显示文字
label1 = ttk.Label(root, text="截图保存文件夹：")
label2 = ttk.Label(root, text="图片转文字输出文件夹：")
label3 = ttk.Label(root, text="文本合并目录：")
label4 = ttk.Label(root, text="书籍最终输出文件夹：")
label5 = ttk.Label(root, text="抓取周期：")
labelConfig = ttk.Label(root, text="配置文件：config.json")
labelkey = ttk.Label(root, text="模拟按键：")
labeltimes = ttk.Label(root,text="翻页次数")


# 将标签放置在每一行的第一列
labelConfig.grid(row=0, column=0)
label1.grid(row=1, column=0)
label2.grid(row=2, column=0)
label3.grid(row=3, column=0)
label4.grid(row=4, column=0)
label5.grid(row=5, column=0)

# 创建输入框对象，用于接收用户输入的数据
entryPictureDir = ttk.Entry(root)
entryOCROutPaDir = ttk.Entry(root)
entryMergeBookDir = ttk.Entry(root)
entryFinalNovelDir = ttk.Entry(root)
entryCycle = ttk.Entry(root)
entryKey = ttk.Entry(root)
entrytime= ttk.Entry(root)


# 将输入框放置在第二列
entryPictureDir.grid(row=1, column=1)
entryOCROutPaDir.grid(row=2, column=1)
entryMergeBookDir.grid(row=3, column=1)
entryFinalNovelDir.grid(row=4, column=1)
entryCycle.grid(row=5, column=1)

# 创建复选框对象
checkUseOldImagePlot = ttk.Checkbutton(root, text="使用上次记录的截图坐标")
checkUseOldClickPlot = ttk.Checkbutton(root, text="使用上次记录的模拟点击坐标")

# 创建按钮对象，用于触发函数
loadConfigjson = ttk.Button(root, text="获取配置信息", command=loadconfig)
RegetpicturePlot = ttk.Button(root, text="重新获取", command=getPicturePlot)
RegetclickPlot = ttk.Button(root, text="重新获取", command=getClickPlot)

# 定义一个变量，用于存储下拉菜单的选择值
pagemethod = tk.StringVar()

# 创建一个下拉菜单对象，显示"请选择翻页触发方式"
option = ttk.OptionMenu(root, pagemethod, "" ,"模拟点击", "模拟按键")
# 将下拉菜单放置在第一行的第一列
option.grid(row=6, column=0)


# 定义一个函数，用于根据选择值显示额外的文本框和标签与按钮
def show_extra(*args):
    # 获取选择值
    value = pagemethod.get()
    # 如果选择值存在，则显示额外的文本框和标签与按钮
    if value in ["模拟点击"]:
        # 复选框放置
        checkUseOldImagePlot.grid(row=7, column=0)
        checkUseOldClickPlot.grid(row=8, column=0)
        # 放置按钮
        RegetpicturePlot.grid(row=7, column=1)
        RegetclickPlot.grid(row=8, column=1)
        # 隐藏之前的部件
        if labelkey.winfo_exists():
            labelkey.grid_forget()
        if entryKey.winfo_exists():
            entryKey.grid_forget()
    if value in ["模拟按键"]:
        # 放置文本标签
        labelkey.grid(row=8,column=0)
        # 放置输入框
        entryKey.grid(row=8,column=1)
        # 设置输入框默认值
        entryKey.insert(0,"N")
        # 复选框放置
        checkUseOldImagePlot.grid(row=7, column=0)
        # 放置按钮
        RegetpicturePlot.grid(row=7, column=1)
        # 隐藏之前的部件
        if checkUseOldClickPlot.winfo_exists():
            checkUseOldClickPlot.grid_forget()
        if RegetclickPlot.winfo_exists():
            RegetclickPlot.grid_forget()


# 使用trace方法绑定show_extra函数到var变量上，当用户选择了翻页方式时的写入操作时就会触发show_extra函数
pagemethod.trace("w", show_extra)








# 将按钮放置在第五行的第一列和第二列之间（跨越两列）
#loadConfigjson.grid(row=5, columnspan=2)
# 放置按钮
loadConfigjson.grid(row=0, column=1)


# 运行窗体对象，等待事件的发生
root.mainloop()
