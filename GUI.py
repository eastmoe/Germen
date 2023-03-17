# 图形用户程序，便于使用
import json
import glob
import time
import os
# 导入tkinter模块
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
# 利用多线程完成操作
import threading

# 定义全局变量
PictureDir = ""
OCROutPaDir = ""
MergeBookDir = ""
FinalNovelDir = ""
Cycle = ""
UseOldImagePlot = ""
UseOldClickPlot = ""
CycleTime = ""

# 定义一个全局变量，用于控制子线程的循环条件
stop_process = False


# 函数，加载配置，返回各个函数所需的路径和周期
def loadconfig():
    print("加载配置文件.....")
    with open("config.json", encoding='gb18030') as config:
        ConfigInfo = json.load(config)
    # 函数可以直接读取全局变量的值，但是如果想要修改全局变量的值，就需要在函数内部使用global关键字来声明
    global PictureDir
    global OCROutPaDir
    global MergeBookDir
    global FinalNovelDir
    # 设置输入框的默认值
    PictureDir = ConfigInfo["PictureDir"]
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


# 函数，修改配置文件
def ModConfig():
    messagebox.showinfo(title="信息",
                        message="请在修改完配置文件后重新加载配置。")
    os.startfile("config.json")


# 定义一个函数，用于读取复选框的状态，
def getplotstate():
    global UseOldImagePlot
    global UseOldClickPlot
    UseOldImagePlot = checkUseOldImagePlot.getvar()
    UseOldClickPlot = checkUseOldClickPlot.getvar()


# 定义函数，获取截图区域及点击坐标
def getPicturePlot():
    messagebox.showinfo(title="信息",
                        message="请选取小说的阅读页面，不需要包含边框，建议提高对比度以改善OCR文字识别效率。")
    # 执行Python程序，获取截图区域
    os.system('python GetNovelImagePlot.py')


def getClickPlot():
    messagebox.showinfo(title="信息",
                        message="请选取小说的阅读页面的模拟点击目标。")
    # 执行Python程序，获取点击位置
    os.system('python GetClickPlot.py')


# 函数，找出指定目录中修改日期最新的文件并返回文件名，参数是目录，文件类型
def FindLatestFile(folder_path, file_type):
    # 获取指定目录和文件类型的所有文件列表
    files = glob.glob(folder_path + file_type)

    if files:  # 如果文件列表不为空，按照修改日期排序并返回最新的文件名
        return max(files, key=os.path.getmtime)
    # 否则返回None
    else:
        return None


# 定义采集函数
def CaptureBook():
    import ImageGrab
    import keyboard
    import PaddleOCR
    import Click

    # 将进度条放置在窗体上
    Processbar.place(x=100, y=50)

    PictureDir = entryPictureDir.get()
    OCROutPaDir = entryOCROutPaDir.get()
    Cycle = entryCycle.get()
    # UseOldImagePlot = ""
    # UseOldClickPlot = ""
    CycleTimes = int(entryTime.get())
    # 获取用户设定的按键，默认为N
    UserSettingKey = entryKey.get()
    # 记录循环次数
    t = 1
    Processbar.start()
    while t < CycleTimes:
        # 执行截图操作
        ImageGrab.GrabReadImage(PictureDir)
        print("截取图像成功。\n")
        # 使用函数寻找最新地截图，进行OCR操作。
        LatestImage = FindLatestFile(PictureDir, "*.png")
        # LatestImagePath=os.path.join(PictureDir,LatestImage)
        print("当前截图：", LatestImage, "\n")
        # 执行OCR操作
        PaddleOCR.OCR(LatestImage, OCROutPaDir)
        # 获取选择值
        value = pagemethod.get()
        if value in ["模拟点击"]:
            # 执行模拟点击操作
            Click.ClickToNextPage()
        else:
            # 使用keyboard.press_and_release()函数来模拟按键
            keyboard.press_and_release(UserSettingKey)
        # 记录时间以准备进行停顿
        start = time.time()
        # 执行一个Cycle秒的等待
        Cycle = float(Cycle)
        while time.time() - start < Cycle:
            # 当按下C键退出循环，转到下一步
            # 如果stop_process为True，则跳出循环，并打印"停止运行"
            if stop_process:
                print("停止运行")
                break
            time.sleep(0.1)
        # 当按下C键退出循环，转到下一步
        # 如果stop_mainfunction为True，则跳出循环，并打印"函数停止运行"
        if stop_process:
            print("函数停止运行")
            break
        t = t+1
    Processbar.stop()


# 定义一个函数，用于创建并启动一个子线程来执行mainfunction函数
def startCaptureBook():
    messagebox.showinfo(title="信息",
                        message="请打开安卓模拟器，并打开阅读app，转到阅读页面。确认后请按回车键。注意，如果你需要重新采集或采集新书，请先清空OCR输出目录。")
    # 使用global关键字声明全局变量，并将其设置为False（表示开始运行）
    global stop_process
    stop_process = False
    # 创建一个子线程对象，并传入CaptureBook(采集函数)作为目标函数（target）
    ProcessThread = threading.Thread(target=CaptureBook())
    # 设置子线程为守护线程（daemon），这样当主线程结束时，子线程也会自动结束
    ProcessThread.Daemon = True
    # 启动子线程对象
    ProcessThread.start()


# 定义一个函数，用于设置stop_mainfunction为True（表示停止采集）
def stoptCaptureBook():
    # 使用global关键字声明全局变量，并将其设置为True（表示停止运行）
    # 函数可以直接读取全局变量的值，但是如果想要修改全局变量的值，就需要在函数内部使用global关键字来声明
    global stop_process
    stop_process = True


# 定义函数，用来合成书籍
def MergeBook():
    MergeBookDir = entryMergeBookDir.get()
    OCROutPaDir = entryOCROutPaDir.get()
    import TextMerge
    print("准备进行文本合并......")
    # 利用时间命名合并之后的文件
    MergedFiletime = time.strftime('%Y-%m-%d-%H-%M-%S')
    MergedFileName = str(MergedFiletime) + ".txt"
    global MergedFilePath
    MergedFilePath = os.path.join(MergeBookDir, MergedFileName)
    print("按时间顺序列出文本列表.......\n")
    # 获取OCR产生的文本文件列表，按时间顺序排序
    TextList = TextMerge.GetFileList(OCROutPaDir)
    print(TextList)
    # 对这些文件进行按时间顺序合并。
    TextMerge.Merge(TextList, OCROutPaDir, MergedFilePath)


# 定义函数，删除OCR输出目录里的文本文件
def DeleteOCRText():
    answer = messagebox.askquestion(title="确认删除", message="确认删除图片转文字输出文件夹内的所有文本文件吗？",
                                    icon='warning')
    if answer == 'yes':
        # 删除"./ocroutput"目录下的所有txt文件
        print(OCROutPaDir)
        for file in os.listdir(OCROutPaDir):
            if file.endswith(".txt"):
                os.remove(os.path.join(OCROutPaDir, file))
        messagebox.showinfo(title="信息",
                            message="删除成功！")


# 定义格式化函数
def FormatBook():
    FinalNovelDir = entryFinalNovelDir.get()
    import FormatReplace
    # 利用时间命名处理之后的文件
    NovelFiletime = time.strftime('%Y-%m-%d-%H-%M-%S')
    NovelFileName = str(NovelFiletime) + ".txt"
    NovelFilePath = os.path.join(FinalNovelDir, NovelFileName)
    # 添加段落首部空格
    FormatReplace.AddSpaceForParagraphs(MergedFilePath, NovelFilePath)
    print("添加段落空格成功")
    # 执行格式整理
    FormatReplace.UpdateFormat(NovelFilePath)
    print("格式修改成功！\n最终生成的文件位于", NovelFilePath)


# 定义一键处理函数
def AutoProcess():
    startCaptureBook()
    MergeBook()
    FormatBook()


# 定义一个函数，用于根据选择值显示额外的文本框和标签与按钮
def show_extra(*args):
    # 获取选择值
    value = pagemethod.get()
    # 如果选择值存在，则显示额外的文本框和标签与按钮
    if value in ["模拟点击"]:
        # 复选框放置
        checkUseOldImagePlot.grid(row=8, column=0, sticky="W", padx=10, pady=5)
        checkUseOldClickPlot.grid(row=9, column=0, sticky="W", padx=10, pady=5)
        # 放置按钮
        RegetpicturePlot.grid(row=8, column=1, sticky="W", padx=10, pady=5)
        RegetclickPlot.grid(row=9, column=1, sticky="W", padx=10, pady=5)
        # 显示统一控件
        ShowControlPanel()
        # 隐藏之前的部件
        if labelkey.winfo_exists():
            labelkey.grid_forget()
        if entryKey.winfo_exists():
            entryKey.grid_forget()
    if value in ["模拟按键"]:
        # 放置文本标签
        labelkey.grid(row=9, column=0, sticky="W", padx=10, pady=5)
        # 放置输入框
        entryKey.grid(row=9, column=1, sticky="W", padx=10, pady=5)
        # 使用delete方法删除从第一个字符到最后一个字符的文本
        entryKey.delete(0, "end")
        # 设置输入框默认值
        entryKey.insert(0, "N")
        # 复选框放置
        checkUseOldImagePlot.grid(row=8, column=0, sticky="W", padx=10, pady=5)
        # 放置按钮
        RegetpicturePlot.grid(row=8, column=1, sticky="W", padx=10, pady=5)
        # 显示统一控件
        ShowControlPanel()
        # 隐藏之前的部件
        if checkUseOldClickPlot.winfo_exists():
            checkUseOldClickPlot.grid_forget()
        if RegetclickPlot.winfo_exists():
            RegetclickPlot.grid_forget()


# 定义函数，用来显示在设置完参数后的统一部件
def ShowControlPanel():
    # 分隔符
    sep = ttk.Separator(root, orient='horizontal')
    # sep.grid(row=10 )
    # sep.pack(fill=x)
    # 放置按钮
    StartCapture.grid(row=11, column=0, sticky="W", padx=10, pady=10)
    StopCapture.grid(row=11, column=1, sticky="E", padx=10, pady=10)
    Merge.grid(row=12, column=0, sticky="W", padx=10, pady=10)
    ClearOCR.grid(row=12, columnspan=2)
    Format.grid(row=12, column=1, sticky="E", padx=10, pady=10)
    SimpleProcess.grid(row=13, columnspan=2, sticky=tk.W+tk.E, padx=10, pady=10)


# 创建一个窗体对象
root = tk.Tk()

# 设置窗体标题
root.title("Germen GUI")

# 设置窗体大小
root.geometry("325x550")
root.resizable(False, False)  # 设置窗口的宽度和高度都不可调整

# 创建标签对象，显示文字
label1 = ttk.Label(root, text="截图保存文件夹：")
label2 = ttk.Label(root, text="图片转文字输出文件夹：")
label3 = ttk.Label(root, text="文本合并目录：")
label4 = ttk.Label(root, text="书籍最终输出文件夹：")
label5 = ttk.Label(root, text="抓取周期(秒)：")
labelConfig = ttk.Label(root, text="配置文件：config.json")
labelkey = ttk.Label(root, text="模拟按键：")
labeltimes = ttk.Label(root, text="翻页次数")

# 将标签放置在每一行的第一列
labelConfig.grid(row=0, column=0, sticky="W", padx=10, pady=10)
label1.grid(row=1, column=0, sticky="W", padx=10, pady=5)
label2.grid(row=2, column=0, sticky="W", padx=10, pady=5)
label3.grid(row=3, column=0, sticky="W", padx=10, pady=5)
label4.grid(row=4, column=0, sticky="W", padx=10, pady=5)
label5.grid(row=5, column=0, sticky="W", padx=10, pady=5)
labeltimes.grid(row=6, column=0, sticky="W", padx=10, pady=10)

# 创建输入框对象，用于接收用户输入的数据
entryPictureDir = ttk.Entry(root)
entryOCROutPaDir = ttk.Entry(root)
entryMergeBookDir = ttk.Entry(root)
entryFinalNovelDir = ttk.Entry(root)
entryCycle = ttk.Entry(root)
entryKey = ttk.Entry(root)
entryTime = ttk.Entry(root)


# 将输入框放置在第二列
entryPictureDir.grid(row=1, column=1, sticky="E", padx=10, pady=5)
entryOCROutPaDir.grid(row=2, column=1, sticky="E", padx=10, pady=5)
entryMergeBookDir.grid(row=3, column=1, sticky="E", padx=10, pady=5)
entryFinalNovelDir.grid(row=4, column=1, sticky="E", padx=10, pady=5)
entryCycle.grid(row=5, column=1, sticky="E", padx=10, pady=5)
entryTime.grid(row=6, column=1, sticky="E", padx=10, pady=10)

# 设置采集页数(循环次数)输入框默认值
entryTime.insert(0, "1000")

# 创建一个IntVar对象，用于存储复选框的状态
checkvar = tk.IntVar()
# 设置初始值为1，表示默认选中
checkvar.set(1)

# 创建复选框对象
checkUseOldImagePlot = ttk.Checkbutton(root, text="使用截图", variable=checkvar)
checkUseOldClickPlot = ttk.Checkbutton(root, text="使用模拟点击", variable=checkvar)

# 创建按钮对象，用于触发函数
loadConfigjson = ttk.Button(root, text="获取", command=loadconfig)
ModConfigjson = ttk.Button(root, text="修改", command=ModConfig)
RegetpicturePlot = ttk.Button(root, text="重新获取", command=getPicturePlot)
RegetclickPlot = ttk.Button(root, text="重新获取", command=getClickPlot)
StartCapture = ttk.Button(root, text="开始采集", command=startCaptureBook)
StopCapture = ttk.Button(root, text="结束采集", command=stoptCaptureBook)
Merge = ttk.Button(root, text="合成书籍", command=MergeBook)
ClearOCR = ttk.Button(root, text="清理OCR路径", command=DeleteOCRText)
Format = ttk.Button(root, text="格式化书籍", command=FormatBook)
SimpleProcess = ttk.Button(root, text="一键采集", command=AutoProcess)

# 创建一个进度条，设置长度为200，模式为indeterminate（不确定的）
Processbar = ttk.Progressbar(root, length=200, mode="indeterminate")

# 放置加载与修改按钮
loadConfigjson.grid(row=0, column=1, sticky="W", padx=10, pady=10)
ModConfigjson.grid(row=0, columnspan=2, sticky="E", padx=0, pady=10)

# 定义一个变量，用于存储下拉菜单的选择值
pagemethod = tk.StringVar()

# 创建一个下拉菜单对象，显示"请选择翻页触发方式"
option = ttk.OptionMenu(root, pagemethod, "", "模拟点击", "模拟按键")
# 放置下拉菜单
option.grid(row=7, column=0, sticky="W", padx=10, pady=20)

# 使用trace方法绑定show_extra函数到pagemethod变量上，当用户选择了翻页方式时的写入操作时就会触发show_extra函数
pagemethod.trace("w", show_extra)

# 将按钮放置在第五行的第一列和第二列之间（跨越两列）
# loadConfigjson.grid(row=5, columnspan=2)

# 设置按钮间距
col_count, row_count = root.grid_size()
for col in range(col_count):
    root.grid_columnconfigure(col, minsize=20)  # 设置列间距为20像素
for row in range(row_count):
    root.grid_rowconfigure(row, minsize=30)  # 设置行间距为20像素

# 运行窗体对象，等待事件的发生
root.mainloop()
