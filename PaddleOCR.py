#基于paddleOCR的本地图片识别
import os
import time
import datetime
# 使用paddleocr模块而不是paddlehub里的ocrserver
import paddleocr
import logging

# 设置日志
logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.INFO,
                    filename='./log/ocr.log',
                    filemode='a')


# 首次运行需要下载模型并加载入内存
ocr_program = paddleocr.PaddleOCR(use_angle_cls=False, lang="ch",
                                  # 模型下载：https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/doc/doc_ch/models_list.md
                                  det_model_dir="models/ch_PP-OCRv4_det_server_infer",
                                  rec_model_dir="models/ch_PP-OCRv4_rec_server_infer")
logging.info(f"OCR检测模型：models/ch_PP-OCRv4_det_server_infer，识别模型：models/ch_PP-OCRv4_rec_server_infer")

def OCR(PicturePath,OCROutPath):
#定义OCR函数，参数是图片文件路径和OCR文本输出路径
#注意，图片文件路径不支持中文
    pathExist1=os.path.exists(PicturePath)
    pathExist2= os.path.exists(OCROutPath)
    if (pathExist1  == False):
    #检查路径是否存在
        logging.error('图片文件路径路径错误，程序将退出。')
        print('图片文件路径路径错误，程序将退出。')
        return "Error"
    if (pathExist2  == False):
    #检查路径是否存在
        logging.error('OCR文本输出路径错误，程序将退出。')
        print('OCR文本输出路径错误，程序将退出。')
        return "Error"

    logging.info(f"本次图片转文字开始时间：{datetime.datetime.now()}")
    #print("本次图片转文字开始时间：",datetime.datetime.now(),"\n")

    # 图片OCR
    # 基于模块的ocr
    ocr_result = ocr_program.ocr(PicturePath, cls=True)


    # 定义需要写入的文本为空字符串
    text = ""
    # 将文本组合成以行相隔的字符串列表
    result = ocr_result[0]
    OCRTxtList = [line[1][0] for line in result]
    #print(OCRTxtList)
    # 初始的现在行数为1
    currentLine = 1
    # 计算总行数
    lineNumber = len(OCRTxtList)
    logging.info(f"当前页面文字行数：{lineNumber}")

    for elements in OCRTxtList:
            # 将列表元素赋给当前行
            line = elements
            # 输出行内容
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
    # 使用UTF8编码打开，防止出现UnicodeEncodeError: 'gbk' codec can't encode character '\xb2'
    txtfile = open(txtpath, 'w', encoding="utf-8")
    txtfile.write(text)
    txtfile.close()
    logging.info(f"本次图片转文字结束时间：{datetime.datetime.now()}，文件保存为{txtpath}")
    #print("本次图片转文字结束时间：",datetime.datetime.now(),"\n")

    return 0

def TestFeature():
    #Image='E:/个人文件/Documents/GITHUB/Germen/NovelPictures/sample.png'
    Image='./NovelPictures/sample.png'
    #Image=""
    OCROutDir='C:/Users/XKW/Documents/GITHUB/Germen/NovelOCRText'
    OCR(Image,OCROutDir)
    return 0

#TestFeature()




