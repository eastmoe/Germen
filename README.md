# Germen

一款实验性质的个人向通用安卓移动端在线阅读app小说提取工具。“Germen”源于拉丁语“幼苗”。

## 设计思路

![mind.PNG](https://s2.loli.net/2023/03/05/SwvrBoVMe1ThK7D.png)

## 开发进度

*开发截图与模拟点击的部分。*（已完成）

*开发OCR部分*（已完成）

*开发文本处理部分*（已完成）

*正在开发主程序*（已完成）

**调试程序与修复Bug**（进行中）

## 配置文件（config.json）说明

1. PictureDir ：保存截图的路径
2. OCROutPaDir：保存OCR生成的文本的路径
3. MergeBookDir：保存经过了合并，但是未处理格式的文本文件的路径
4. FinalNovelDir：保存经过格式处理的文本文件的路径
5. Cycle：每一轮截图-翻页-文字识别的间隔时间，默认为30秒


## 使用说明

1. 请先安装Python，并添加到PATH（开发环境为Python 3.10）。
2. 将下载好的Release压缩包解压（或者git clone），在项目根目录运行`pip install -r requirements.txt`安装依赖。
3. 运行`pip install shapely pyclipper`安装PaddleOCR所需要的依赖。
4. 运行`hub install chinese_ocr_db_crnn_server`安装PaddleOCR，可参考[官网说明](https://www.paddlepaddle.org.cn/hubdetail?name=chinese_ocr_db_crnn_server&en_category=TextRecognition)。
5. 在项目根目录运行`python MainProgram.py`启动主程序。
6. 按照流程执行操作。

## 小贴士

1. 在安装依赖中的Paddle(飞浆)时，有可能会因为网络原因而导致安装失败。推荐按照官方的[说明](https://www.paddlepaddle.org.cn/install/quick?docurl=/documentation/docs/zh/install/pip/windows-pip.html)手动安装相关的组件。
2. 在每次运行采集时，务必清空**OCROutPaDir**里残留的OCR文本，以免合成的文本混杂上一次的内容。
3. 推荐提高阅读界面的对比度，使用常规字体以获得更高的识别准确率。调整字体大小以提高获取文本的效率。
4. 确认设置的模拟点击位置在现在和未来的截屏中不会遮挡文字，否则可能造成OCR识别错误、缺字等。
5. 在程序运作时，请不要遮挡窗口，也尽量不要做拖拽操作，以免模拟点击被用户操作覆盖。
6. 目前加入了按键模拟翻页，使用之前请在模拟器中设置好按键和点按位置。
7. 如果你的模拟器使用了管理员权限运行，那么建议也使用管理员权限运行python执行本程序。
8. 如果运行OCR过程中提示缺少cudnn文件，可以参考[这篇文章](https://blog.csdn.net/weixin_44906810/article/details/128176194#:~:text=%E6%89%93%E5%BC%80%E9%87%8C%E9%9D%A2%E7%A1%AE%E5%AE%9E%E6%B2%A1%E6%9C%89cudnn64_8.dll%E6%96%87%E4%BB%B6%E3%80%82,%E7%84%B6%E5%90%8E%E6%88%91%E4%BB%AC%E9%9C%80%E8%A6%81%E5%8E%BB%E4%B8%8B%E8%BD%BD%E7%9A%84cudnn%E5%8E%8B%E7%BC%A9%E5%8C%85%E9%87%8C%E9%9D%A2%E6%89%BE%E8%BF%99%E4%B8%AA%E6%96%87%E4%BB%B6%EF%BC%8C%E5%B0%86%E5%8E%8B%E7%BC%A9%E5%8C%85%E8%A7%A3%E5%8E%8B%E6%89%93%E5%BC%80%EF%BC%8C%E5%90%8C%E6%A0%B7%E4%BC%9A%E6%9C%89bin%E6%96%87%E4%BB%B6%EF%BC%8C%E6%89%93%E5%BC%80bin%EF%BC%8C%E9%87%8C%E9%9D%A2%E5%B0%B1%E6%9C%89%E6%88%91%E4%BB%AC%E6%89%80%E9%9C%80%E7%9A%84cudnn64_8.dll%E6%96%87%E4%BB%B6)来解决。
