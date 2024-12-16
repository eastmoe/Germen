import csv
import opencc



# 示例：CSV文件格式
# 一个简单的CSV文件包含两列，分别表示要查找的内容和要替换的内容：
#
# csv
#
# old_word1,new_word1
# old_word2,new_word2
#

# 加载替换文件列表
csv_file = 'ReplaceWordsLists.csv'
replacements = []
with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) == 2:  # 确保每行有两个元素
            replacements.append({
                'find': row[0],
                'replace': row[1]
            })

# 2. 进行替换操作
# def replace_text(text, replacements):
#     for rule in replacements:
#         text = text.replace(rule['find'], rule['replace'])
#     return text



# 使用opencc进行繁简转换
def ConvertCHT2CHS(input_text_file):
    # 打开原始文件并读取内容
    with open(input_text_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # 创建OpenCC转换器
    cc = opencc.OpenCC('t2s.json')  # 't2s.json'表示从繁体到简体的转换

    # 使用OpenCC进行繁体转简体
    simplified_text = cc.convert(text)

    # 将转换后的文本写入新的文件
    filename = input_text_file + '_简化.txt'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(simplified_text)

    print("小说中的繁体字已转换为简体字并保存为:",filename,"\n")



# 使用自定义列表进行替换
def ReplacewaterMark(input_text_file):

    # 读取文本文件内容
    with open(input_text_file, 'r', encoding='utf-8') as file:
        text = file.read()

    # 执行替换
    for rule in replacements:
        modified_text = text.replace(rule['find'], rule['replace'])

    # 保存替换去水印后的文本
    filename=input_text_file +'_去水印.txt'
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(modified_text)

    #返回最后的文件路径
    print("水印替换操作完成，结果已保存到",filename,"\n")
    return filename

# 调试
if __name__ == "__main__":
    ConvertCHT2CHS('test.txt')