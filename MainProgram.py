#主程序
import json
import keyboard
import time
import os





#加载配置，返回各个函数所需的路径和周期
def LoadConfig():
    print("加载配置文件.....")
    with open("config.json",encoding='gb18030') as config:
        ConfigInfo = json.load(config)
    PictureDir = ConfigInfo["PictureDir"]
    OCROutPaDir = ConfigInfo["OCROutPaDir"]
    MergeBookDir = ConfigInfo["MergeBookDir"]
    FinalNovelDir = ConfigInfo["FinalNovelDir"]
    Cycle = ConfigInfo["Cycle"]
    return PictureDir,OCROutPaDir,MergeBookDir,FinalNovelDir,Cycle

PictureDir,OCROutPaDir,MergeBookDir,FinalNovelDir,Cycle=LoadConfig()
print("配置加载完成："
      "\n截图保存文件夹：",PictureDir,
      "\n图片转文字输出文件夹：",OCROutPaDir,
      "\n文本合并目录：",MergeBookDir,
      "\n书籍最终输出文件夹：",FinalNovelDir,
      "\n抓取周期：",Cycle," 秒\n")

#获取截图范围
print("请打开安卓模拟器，并打开阅读app，转到阅读页面。\n确认后请按回车键，使用鼠标左键选择截图范围。")
input()
#with open('GetNovelImagePlot.py','r') as GetNovelImagePlot:
#exec("python GetNovelImagePlot.py")
os.system('python GetNovelImagePlot.py')

#获取模拟点击坐标
print("接下来，程序将获取模拟点击坐标，确认后请按回车键，然后在你需要的地方点按鼠标左键。")
input()
#with open('GetClickPlot.py','r') as GetClickPlot:
    #exec(GetClickPlot.read())
#exec("python GetClickPlot.py")
os.system('python GetClickPlot.py')

#设置翻页/截图间隔
#print("请输入翻页/截图间隔，单位为秒(s)，默认值为250。")
#Cycle_new=input()
#if Cycle_new ==

#开始获取图片并进行OCR
import ImageGrab
import PaddleOCR
print("确认上述配置正确，请按回车键执行采集任务。\n警告：该过程目前无法自动控制结束，请在抓取结束时按下两次回车键以进入下一步。\n")
input()
while True:
    ImageGrab.GrabReadImage(PictureDir)
    print("截取图像成功。\n")
    PaddleOCR.OCR(PictureDir,OCROutPaDir)
    start = time.time()
    # 执行一个Cycle秒的等待
    while time.time() - start < Cycle:
        if keyboard.is_pressed():
            break
        time.sleep(0.1)
    if keyboard.is_pressed():
        break
print("采集结束\n")

#合并文本
import TextMerge
print("准备进行文本合并......")
#利用时间命名合并之后的文件
MergedFiletime = time.strftime('%Y-%m-%d-%H-%M-%S')
MergedFileName = str(MergedFiletime) + ".txt"
MergedFilePath=os.path.join(MergeBookDir,MergedFileName)
print("按时间顺序列出文本列表.......\n")
TextList=TextMerge.GetFileList(OCROutPaDir)
print(TextList)
TextMerge.Merge(TextList,OCROutPaDir,MergedFilePath)
print("合并成功。\n")

#格式处理
import FormatReplace
#利用时间命名处理之后的文件
NovelFiletime = time.strftime('%Y-%m-%d-%H-%M-%S')
NovelFileName = str(NovelFiletime) + ".txt"
NovelFilePath=os.path.join(FinalNovelDir,NovelFileName)
FormatReplace.AddSpaceForParagraphs(MergedFilePath,NovelFilePath)
print("添加段落空格成功")
FormatReplace.UpdateFormat(NovelFilePath)
print("格式修改成功！\n最终生成的文件位于",NovelFilePath)
print("\n感谢您的使用，请按任意键退出。\n")
if keyboard.is_pressed():
    print("退出")
