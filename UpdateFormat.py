#运行Word宏对小说进行格式处理
import win32com
import os
from win32com.client import Dispatch

#定义函数执行宏代码，参数为合并后的小说文本文件路径
def UpdateFormat(NovelBookFilePath):

    PathExist1 = os.path.exists(NovelBookFilePath)
    if (PathExist1 == False):
        # 检查路径是否存在
        print('合并后的小说文本文件路径错误，程序将退出。')
        return "Error"

    docApp = win32com.client.DispatchEx('Word.Application')
    try:
        doc = docApp.Documents.Open(NovelBookFilePath)
        #VBA代码 Start

        #VBA代码End
        doc.Save()
        print("小说文本格式整理成功")
    except Exception as e:
        print(e)
    #保证即使出错也能关掉窗口，否则后台会出现大量word进程且可能占用文件
    docApp.Quit()


def TestFeature():
    BookPath=""
    UpdateFormat(BookPath)


