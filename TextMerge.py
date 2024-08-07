#文本合并程序
import os
import logging

# 设置日志
logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG,
                    filename='./log/text.log',
                    filemode='a')

#用于文件按照修改时间顺序排序的函数，参数是OCR输出路径
def GetFileList(file_path):
    dir_list = os.listdir(file_path)
    if not dir_list:
        logging.error(f"错误！配置的OCR输出目录{file_path}无文本文件！")
        print("错误！配置的OCR输出目录无文本文件！")
        return "Error"
    else:
          # 注意，这里使用lambda表达式，将文件按照最后修改时间顺序升序排列
        # os.path.getmtime() 函数是获取文件最后修改时间
         # os.path.getctime() 函数是获取文件最后创建时间
        dir_list = sorted(dir_list,key=lambda x: os.path.getmtime(os.path.join(file_path, x)))
        logging.info(f"OCR文本列表：{dir_list}")
        # print(dir_list)
    return dir_list

#用于合并的函数，参数是OCR识别产生的TXT文件list，OCR输出路径，合并之后未处理格式的整本小说文件路径
def Merge(file_list,dir_path,novelfile):
    PathExist1 = os.path.exists(dir_path)
    if (PathExist1 == False):
        # 检查路径是否存在
        logging.error(f"错误！配置的OCR输出目录{dir_path}无文本文件！")
        print('OCR输出路径错误，程序将退出。')
        return "Error"

    novel=open(novelfile,"w", encoding="utf-8")
    #打开整本小说文件
    for file in file_list:
    #遍历文件列表
        filepath=os.path.join(dir_path,file)
        #目录路径+当前文件名组成完整路径
        nextText=open(filepath, encoding="utf-8")
        #打开下一个文本
        novel.writelines(nextText)
        #将数据每次按行写入
        novel.write("\n")
        #每写完一个文件，就换行
    novel.close()
    logging.info(f"合并成功，文件位于：{novelfile}")
    print("合并成功！文件位于",novelfile)
    return 0

# 功能测试函数
def TestFeature():
    OCROutpath="E:/个人文件/Documents/GITHUB/Germen/NovelOCRText"
    MergeBookPath="E:/个人文件/Documents/GITHUB/Germen/MergeText/ExampleMergeBook.txt"
    OCRTextList=GetFileList(OCROutpath)
    Merge(OCRTextList,OCROutpath,MergeBookPath)
    return 0

#TestFeature()
