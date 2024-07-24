#主程序
import json
import keyboard
import time
import os
import glob
import logging

# 设置日志
logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG,
                    filename='./log/main.log',
                    filemode='a')

logging.info("主程序启动")

#函数，加载配置，返回各个函数所需的路径和周期
def LoadConfig():
    logging.info("加载配置文件.....")
    with open("config.json",encoding='gb18030') as config:
        ConfigInfo = json.load(config)
    PictureDir = ConfigInfo["PictureDir"]
    OCROutPaDir = ConfigInfo["OCROutPaDir"]
    MergeBookDir = ConfigInfo["MergeBookDir"]
    FinalNovelDir = ConfigInfo["FinalNovelDir"]
    Cycle = ConfigInfo["Cycle"]
    return PictureDir,OCROutPaDir,MergeBookDir,FinalNovelDir,Cycle

#函数，找出指定目录中修改日期最新的文件并返回文件名，参数是目录，文件类型
def FindLatestFile(folder_path, file_type):
  # 获取指定目录和文件类型的所有文件列表
  files = glob.glob(folder_path + file_type)
  # 如果文件列表不为空，按照修改日期排序并返回最新的文件名
  if files:
    logging.info(f"目录{folder_path}下最新的{file_type}类型文件：{files}")
    return max(files, key=os.path.getmtime)
  # 否则返回None
  else:
    logging.error(f"目录{folder_path}下不存在{file_type}类型文件")
    return None

#使用函数加载配置并输出配置信息
PictureDir,OCROutPaDir,MergeBookDir,FinalNovelDir,Cycle=LoadConfig()
logging.info(f"配置加载完成：截图保存文件夹：{ PictureDir},\n图片转文字输出文件夹：{ OCROutPaDir}\n文本合并目录：{MergeBookDir},\n书籍最终输出文件夹：{FinalNovelDir},\n抓取周期：{Cycle} 秒")
# print("配置加载完成："
#       "\n截图保存文件夹：",PictureDir,
#       "\n图片转文字输出文件夹：",OCROutPaDir,
#       "\n文本合并目录：",MergeBookDir,
#       "\n书籍最终输出文件夹：",FinalNovelDir,
#       "\n抓取周期：",Cycle," 秒\n")

#获取截图范围
print("请打开安卓模拟器，并打开阅读app，转到阅读页面。"
      "\n推荐提高阅读界面的对比度，使用常规字体以获得更高的识别准确率。"
      "\n推荐调整字体大小以提高获取文本的效率。"
      "\n确认后请按回车键，使用鼠标左键选择截图范围。")
input()
# 执行Python程序，获取截图区域
logging.info("执行Python程序，获取截图区域")
os.system('python GetNovelImagePlot.py')

#获取翻页方式
PageMethod=input("请输入操控翻页的方式，1为由本程序控制模拟点击，2为模拟按键，再由模拟器通过设置的键鼠模拟点击翻页"
                 "(注意，部分模拟器在非管理员模式下的点击有可能无效)：")

if PageMethod == "1":
    logging.info("用户选择了模拟点击翻页")
    # 获取模拟点击坐标
    print("接下来，程序将在10秒后获取模拟点击坐标，在你需要的地方点按鼠标左键。确认设置的模拟点击位置在现在和未来的截屏中不会遮挡文字，否则可能造成OCR识别错误、缺字等。在程序运作时，请不要遮挡窗口，也尽量不要做拖拽操作，以免模拟点击被用户操作覆盖。")
    time.sleep(10)
    # 执行Python程序，获取点击位置
    os.system('python GetClickPlot.py')
    logging.info("获取模拟点击坐标")
else:
    logging.info("用户选择了按键翻页")
    import PressKeyboard
    #获取用户设置的按键
    UserSettingKey=PressKeyboard.GetKey()
    logging.info(f"用户当前设置的翻页按键是：{UserSettingKey}")



#开始获取图片并进行OCR
#导入组件
import ImageGrab
import PaddleOCR
import Click
print("程序将会置顶模拟器窗口以防止遮挡截图，请保证当前活动窗口是模拟器。")
print("确认上述配置正确，10秒后将自动执行窗口置顶和采集任务。\n警告：该过程目前无法自动控制结束，请在抓取结束时在控制台中按下C键以进入下一步。\n")
#置顶模拟器窗口
time.sleep(10)
# 导入模块
import win32gui
import win32con
# 获取当前活动的顶层窗口句柄
logging.info("获取当前活动的顶层窗口句柄")
AndroidWindowVM = win32gui.GetForegroundWindow()
# 设置窗口属性，使其置顶
logging.info("设置窗口属性，使其置顶")
win32gui.SetWindowPos(AndroidWindowVM, win32con.HWND_TOPMOST,  0,0,0,0, win32con.SWP_NOMOVE | win32con.SWP_DRAWFRAME | win32con.SWP_NOSIZE| win32con.SWP_NOOWNERZORDER|win32con.SWP_SHOWWINDOW)
# HWND_TOPMOST:将窗口置于所有非顶层窗口之上。即使窗口未被激活窗口也将保持顶级位置。SWP_DRAWFRAME：在窗口周围画一个边框（定义在窗口类描述中）。SWP_NOMOVE：维持当前位置（忽略X和Y参数）。SWP_NOSIZE：维持当前尺寸（忽略cx和Cy参数）。SWP_NOOWNERZORDER：不改变z序中的所有者窗口的位置。SWP_SHOWWINDOW：显示窗口。
#   x：以客户坐标指定窗口新位置的左边界。
#   Y：以客户坐标指定窗口新位置的顶边界。
#   cx:以像素指定窗口的新的宽度。
#   cy：以像素指定窗口的新的高度。
# print("置顶成功，开始采集。")
logging.info("置顶成功")
#初始化页面计数器
PageNumber=1
logging.info(f"初始页面计数器示数为{PageNumber}")
while True:
    #执行截图操作
    ImageGrab.GrabReadImage(PictureDir)
    logging.info("截图成功")
    print("截取图像成功。\n")
    # 使用函数寻找最新的截图，进行OCR操作。
    LatestImage=FindLatestFile(PictureDir,"*.png")
    #LatestImagePath=os.path.join(PictureDir,LatestImage)
    logging.info(f"将对当前截图{LatestImage}执行OCR操作")
    print("当前截图：",LatestImage,"\n")
    #执行OCR操作
    PaddleOCR.OCR(LatestImage,OCROutPaDir)
    if PageMethod=="1":
        # 执行模拟点击操作
        Click.ClickToNextPage()
        logging.info("执行模拟点击成功")
    else:
        #使用keyboard.press_and_release()函数来模拟按键
        keyboard.press_and_release(UserSettingKey)
        logging.info("执行模拟按键输入成功")
    #记录时间以准备进行停顿
    start = time.time()
    logging.info(f"当前周期时间为：{start}，将等待{Cycle}秒后继续")
    # 执行一个Cycle秒的等待
    Cycle=float(Cycle)
    while time.time() - start < Cycle:
        #当按下C键退出循环，转到下一步
        if keyboard.is_pressed("c"):
            logging.info("用户按下了C键，跳转到下一步")
            break
        time.sleep(0.1)
    # 当按下C键退出循环，转到下一步
    if keyboard.is_pressed("c"):
        logging.info("用户按下了C键，跳转到下一步")
        break

    logging.info(f"当前页面计数器示数为{PageNumber}")
    print("当前采集到 第",PageNumber,"页。\n")
    #循环计数器+1
    PageNumber=PageNumber+1
    logging.info(f"页面计数器+1，为{PageNumber}")
    if PageNumber % 100 == 0:
        logging.info(f"当前页面计数器示数为{PageNumber}，暂停采集一分钟并显示性能计数器。")
        import Memory
        #显示内存占用情况
        Memory.ShowMemoryUse()
        print("\n暂停采集1分钟....按C键跳转到下一步。")
        #当采集了100页之后，暂停一分钟
        while time.time() - start < 60:
            # 当按下C键退出循环，转到下一步
            if keyboard.is_pressed("c"):
                logging.info("用户按下了C键，跳转到下一步")
                break
            time.sleep(0.1)
        # 当按下C键退出循环，转到下一步
        if keyboard.is_pressed("c"):
            logging.info("用户按下了C键，跳转到下一步")
            break

logging.info("采集结束，准备处理文本")
print("采集结束\n")

#合并文本
import TextMerge
print("准备进行文本合并......")
#利用时间命名合并之后的文件
MergedFiletime = time.strftime('%Y-%m-%d-%H-%M-%S')
MergedFileName = str(MergedFiletime) + ".txt"
MergedFilePath=os.path.join(MergeBookDir,MergedFileName)
print("按时间顺序列出文本列表.......\n")
#获取OCR产生的文本文件列表，按时间顺序排序
TextList=TextMerge.GetFileList(OCROutPaDir)
logging.info(f"获取OCR产生的文本文件列表，按时间顺序排序:{TextList}")
print(TextList)
#对这些文件进行按时间顺序合并。
TextMerge.Merge(TextList,OCROutPaDir,MergedFilePath)
logging.info("文本合并成功，准备处理格式")

#格式处理
import FormatReplace
#利用时间命名处理之后的文件
NovelFiletime = time.strftime('%Y-%m-%d-%H-%M-%S')
NovelFileName = str(NovelFiletime) + ".txt"
NovelFilePath=os.path.join(FinalNovelDir,NovelFileName)
logging.info(f"将合并后的文件重命名为：{NovelFilePath}")
#添加段落首部空格
FormatReplace.AddSpaceForParagraphs(MergedFilePath,NovelFilePath)
logging.info("添加段落空格成功")
print("添加段落空格成功")
#执行格式整理
FormatReplace.UpdateFormat(NovelFilePath)
logging.info(f"格式修改成功！\n最终生成的文件位于{NovelFilePath}")
print("格式修改成功！\n最终生成的文件位于",NovelFilePath)
logging.info("主程序结束，感谢使用")
print("\n感谢您的使用。\n")

