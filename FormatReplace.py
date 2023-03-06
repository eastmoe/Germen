#处理合并之后的文件换行与段落格式
import os

#定义函数，恢复段落前空格，参数为合并后的小说文本文件路径，最终输出的小说路径
def AddSpaceForParagraphs(MergeTextFile,NovelPath):
    # 打开txt文件
    novelfile = open(MergeTextFile, "r+")

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
    novelfile = open(NovelPath, "w")
    novelfile.writelines(new_lines)
    novelfile.close()
    return 0




#定义函数执行行格式调整，参数为最终输出的小说路径
def UpdateFormat(NovelPath):
    PathExist1 = os.path.exists(NovelPath)
    if (PathExist1 == False):
        # 检查路径是否存在
        print('合并后的小说文本文件路径错误，程序将退出。')
        return "Error"

    # 打开txt文件
    file = open(NovelPath, "r")
    # 读取文件中的所有内容，并存储在一个字符串中
    text = file.read()
    # 关闭文件
    file.close()

    # -------------------------第一次替换-----------------------
    # 输入要查找和替换的文本
    # 换行符替换为无，即取消换行
    OldStr1 = "\n"
    NewStr1 = ""

    # 使用replace()函数替换文本，并存储在新的字符串中
    new_text = text.replace(OldStr1, NewStr1)

    # -------------------------第二次替换-----------------------
    # 从空格前换行，即按段落换行
    OldStr2 = "  "
    NewStr2 = "\n  "
    new_text = new_text.replace(OldStr2, NewStr2)

    # 重新打开文件，并用新的字符串覆盖它
    file = open(NovelPath, "w")
    file.write(new_text)
    file.close()

    return 0

def TestFeature():
    MergeTextFile = "E:/个人文件/Desktop/临时文件/ExampleMergeBook.txt"
    Novel="E:/个人文件/Documents/GITHUB/Germen/FinalBooks/example.txt"
    AddSpaceForParagraphs(MergeTextFile,Novel)
    UpdateFormat(Novel)
    return 0

TestFeature()