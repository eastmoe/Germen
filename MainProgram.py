#主程序
import json

#加载配置，返回各个函数所需的路径
def LoadConfig():
    with open("config.json") as f:
        data = json.load(f)
    PictureDir = data["PictureDir"]
    OCROutPaDir = data["OCROutPaDir"]
    MergeBookDir = data["MergeBookDir"]
    return PictureDir,OCROutPaDir,MergeBookDir
