#运行Word宏对小说进行格式处理(已弃用，因为出现了问题，程序运行成功但是没有进行UpdateFormat)
import win32com
import os
from win32com.client import Dispatch

#定义函数，恢复段落前空格，参数为合并后的小说文本文件路径
def AddSpaceForParagraphs(NovelBookFilePath):
    # 打开txt文件
    novelfile = open(NovelBookFilePath, "r+")

    # 读取文件中的所有行，并存储在一个列表中
    lines = novelfile.readlines()

    # 计算每一行的字符数，并存储在另一个列表中
    char_counts = []
    for line in lines:
        char_counts.append(len(line))

    # 计算字符数的平均值
    avg = sum(char_counts) / len(char_counts)

    # 在字符数少于平均值的行的下一行前面加上两个空格，并写入新的列表中
    new_lines = []
    for i in range(len(lines)):
        if i==0:
            #给首行加上段落空格
            lines[i]="    "+lines[i]
        if char_counts[i] < avg:
            new_lines.append( lines[i]+"\n    ")
        else:
            new_lines.append(lines[i])

    # 关闭原始文件，并用新的列表覆盖它
    novelfile.close()
    novelfile = open(NovelBookFilePath, "w")
    novelfile.writelines(new_lines)
    novelfile.close()
    return 0



#定义函数执行格式调整宏代码，参数为合并后的小说文本文件路径
def UpdateFormat(NovelBookFilePath):
    PathExist1 = os.path.exists(NovelBookFilePath)
    if (PathExist1 == False):
        # 检查路径是否存在
        print('合并后的小说文本文件路径错误，程序将退出。')
        return "Error"

    # 创建一个Word应用对象
    word_app = win32com.client.Dispatch("Word.Application")
    # 打开一个word文档对象
    word_doc = word_app.Documents.Open(NovelBookFilePath)
    # 获取一个范围对象，表示文档中的所有内容
    word_range = word_doc.Range()
    # 获取一个查找对象，用于执行查找和替换操作
    word_find = word_range.Find

    #-------------------------第一次替换-----------------------
    # 指定要查找和替换的内容，以及其他参数
    find_text = "^p"
    #换行符替换为无，即取消换行
    replace_text = ""
    match_case = False  # 是否区分大小写
    match_whole_word = True  # 是否匹配整个单词

    # 执行查找和替换操作，如果返回值为True，说明找到了匹配项
    found = word_find.Execute(find_text, match_case, match_whole_word, ReplaceWith=replace_text)

    # 如果需要对查找结果进行处理，可以使用范围对象的Select方法将其选中，然后使用Selection属性获取一个选择对象，该对象可以修改选中的内容
    while found:
        # 选中查找结果
        word_range.Select()
        # 获取一个选择对象
        #word_selection = word_app.Selection

        # 在这里可以对选择对象进行修改，例如改变字体颜色或样式等

        # 继续执行查找和替换操作，直到没有更多匹配项为止
        found = word_find.Execute(find_text, match_case, match_whole_word, ReplaceWith=replace_text)

    # -------------------------第二次替换-----------------------
    find_text_2 = "  "
    #从空格前换行，即按段落换行
    replace_text_2 = "^p  "
    found_2 = word_find.Execute(find_text_2, match_case, match_whole_word, ReplaceWith=replace_text_2)
    while found_2:
        word_range.Select()
        found_2 = word_find.Execute(find_text_2, match_case, match_whole_word, ReplaceWith=replace_text_2)

    # 保存修改后的文档，并关闭文档
    word_doc.Save()
    word_doc.Close()
    # 退出Word应用
    word_app.Quit()





def TestFeature():
    BookPath="E:/个人文件/Desktop/临时文件/ExampleMergeBook.txt"
    AddSpaceForParagraphs(BookPath)
    #UpdateFormat(BookPath)
    return 0

#TestFeature()


