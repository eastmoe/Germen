#截图程序
from PIL import ImageGrab
import numpy as np
import time
import os
import logging

# 设置日志
logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG,
                    filename='./log/grab.log',
                    filemode='a')



#截图函数，参数是截图保存路径
def GrabReadImage(ImageSaveDir):

    pathExist1 = os.path.exists(ImageSaveDir)
    if (pathExist1 == False):
        # 检查路径是否存在
        logging.error('截图保存路径错误，程序将退出。')
        return "Error"

    xyplot = np.load('.//data/ImagePlot.npy', allow_pickle=True).item()
    # 从文件加载坐标

    print(xyplot)

    xstart = xyplot.get("xstart")
    ystart = xyplot.get("ystart")
    xend = xyplot.get("xend")
    yend = xyplot.get("yend")
    # 将坐标赋予变量

    # 参数说明
    # 第一个参数 开始截图的x坐标
    # 第二个参数 开始截图的y坐标
    # 第三个参数 结束截图的x坐标
    # 第四个参数 结束截图的y坐标
    bbox = (xstart, ystart, xend, yend)
    logging.info(f"获取截图坐标成功，xstart:{xstart}，ystart:{ystart}，xend:{xend}，yend:{yend}")
    im = ImageGrab.grab(bbox)
    # 截图

    # 文件名格式：年-月-日 时:分:秒
    filetime = time.strftime('%Y-%m-%d-%H-%M-%S')
    #Folderpath = os.getcwd()  # 获取当前工作目录路径
    # 拼接时间和文件后缀作为完整文件名
    new_name = str(filetime) + ".png"
    # 拼接文件夹路径和文件名作为完整文件名
    #imgpath = os.path.join(Folderpath, "NovelPictures", new_name)
    imgpath=os.path.join(ImageSaveDir, new_name)

    # 保存截图文件
    im.save(imgpath)
    logging.info(f"截图成功，文件位于{imgpath}")

    return 0


def TestFeature():
    while True:
        ImageSaveDir = "./temp/"
        GrabReadImage(ImageSaveDir)
        import Memory
        Memory.ShowMemoryType()
    return 0
#TestFeature()