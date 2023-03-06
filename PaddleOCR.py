#基于paddleOCR的本地API图片识别
import paddlehub as hub
import datetime
import os
import time

def OCR(PicturePath,OCROutPath):
#定义OCR函数，参数是图片文件路径和OCR文本输出路径
#注意，图片文件路径不支持中文
    pathExist1=os.path.exists(PicturePath)
    pathExist2= os.path.exists(OCROutPath)
    if (pathExist1  == False):
    #检查路径是否存在
        print('图片文件路径路径错误，程序将退出。')
        return "Error"
    if (pathExist2  == False):
    #检查路径是否存在
        print('OCR文本输出路径错误，程序将退出。')
        return "Error"

    print("本次图片转文字开始时间：",datetime.datetime.now(),"\n")

    # 图片OCR
    ocr = hub.Module(name="chinese_ocr_db_crnn_server", enable_mkldnn=True)
    # mkldnn加速仅在CPU下有效
    # ocr_result = ocr.recognize_text( images=[cv2.imread('./NovelPictures/sample.png')])
    #print(PicturePath)
    ocr_result = ocr.recognize_text(paths=[PicturePath])
    # print("\n")
    # print(type(ocr_result))
    # print(ocr_result)

    # 处理识别结果
    # OCR返回的结果是list，list里的元素是字典，字典里面的data元素是list，list里面是每一行的识别结果，是一个字典，字典里面的text对应的值才是每一行的内容。
    text = ""
    for item in ocr_result:
    # 遍历list数组，得到其中的唯一一个字典元素
        # print(item)
        # print("\n")
        # print(type(item))
        # print("\n")
        all_data = item.get('data')
        # 提取这个字典元素的data值，为all_data list
        lineNumber = len(all_data)
        # 记录all_data list的长度，即文字的行数
        currentLine = 1
        # 初始的现在行数为1
        # print(all_data)
        # print("\n")
        # print(type(all_data))
        for elements in all_data:
            # print("\n")
            # print(type(elements))
            line = elements.get('text')
            # print(type(line))
            # print("\n")
            print(line)
            if currentLine < lineNumber:
            # 当现在的行数小于总行数，就换行
                text = text + line + '\n'
            else:
                text = text + line
                # 最后一行不换行
            currentLine = currentLine + 1
    # print(text)

    # 保存识别结果到文本文件
    # 文件名格式：年-月-日 时:分:秒
    filetime = time.strftime('%Y-%m-%d-%H-%M-%S')
    #Folderpath = os.getcwd()
    # 获取当前工作目录路径
    # 拼接时间和文件后缀作为完整文件名
    new_name = str(filetime) + ".txt"
    # 拼接文件夹路径和文件名作为完整文件名
    #txtpath = os.path.join(Folderpath, "NovelOCRText", new_name)
    txtpath=os.path.join(OCROutPath,new_name)

    # 若文件不存在，则会自动创建，w表示文件以可写方式打开。
    txtfile = open(txtpath, 'w')
    txtfile.write(text)
    txtfile.close()

    print("本次图片转文字结束时间：",datetime.datetime.now(),"\n")

    return 0

def TestFeature():
    #Image='E:/个人文件/Documents/GITHUB/Germen/NovelPictures/sample.png'
    Image='./NovelPictures/sample.png'
    #Image=""
    OCROutDir='E:/个人文件/Documents/GITHUB/Germen/NovelOCRText'
    OCR(Image,OCROutDir)
    return 0

TestFeature()




