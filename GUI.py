# 图形用户程序，便于使用
import json
import os
# 导入tkinter模块
import tkinter as tk

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
label1 = tk.Label(root, text="截图保存文件夹：")
label2 = tk.Label(root, text="图片转文字输出文件夹：")
label3 = tk.Label(root, text="文本合并目录：")
label4 = tk.Label(root, text="书籍最终输出文件夹：")
label5 = tk.Label(root, text="抓取周期：")
labelConfig = tk.Label(root, text="配置文件：config.json")

# 将标签放置在每一行的第一列
labelConfig.grid(row=0, column=0)
label1.grid(row=1, column=0)
label2.grid(row=2, column=0)
label3.grid(row=3, column=0)
label4.grid(row=4, column=0)
label5.grid(row=5, column=0)

# 创建输入框对象，用于接收用户输入的数据
entryPictureDir = tk.Entry(root)
entryOCROutPaDir = tk.Entry(root)
entryMergeBookDir = tk.Entry(root)
entryFinalNovelDir = tk.Entry(root)
entryCycle = tk.Entry(root)

# 将输入框放置在第二列
entryPictureDir.grid(row=1, column=1)
entryOCROutPaDir.grid(row=2, column=1)
entryMergeBookDir.grid(row=3, column=1)
entryFinalNovelDir.grid(row=4, column=1)
entryCycle.grid(row=5, column=1)

# 创建复选框对象
checkUseOldImagePlot = tk.Checkbutton(root, text="使用上次记录的截图坐标")
checkUseOldClickPlot = tk.Checkbutton(root, text="使用上次记录的模拟点击坐标")
# 复选框放置
checkUseOldImagePlot.grid(row=6, column=0)
checkUseOldClickPlot.grid(row=7, column=0)












# 创建按钮对象，用于触发函数
loadConfigjson = tk.Button(root, text="获取配置信息", command=loadconfig)
RegetpicturePlot = tk.Button(root, text="重新获取", command=getPicturePlot)
RegetclickPlot = tk.Button(root, text="重新获取", command=getClickPlot)

# 将按钮放置在第五行的第一列和第二列之间（跨越两列）
#loadConfigjson.grid(row=5, columnspan=2)
# 放置按钮
loadConfigjson.grid(row=0, column=1)
RegetpicturePlot.grid(row=6, column=1)
RegetclickPlot.grid(row=7, column=1)

# 运行窗体对象，等待事件的发生
root.mainloop()

