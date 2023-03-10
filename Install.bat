@echo off
rem 在当前目录下的env目录创建一个Python虚拟环境
python -m venv env
rem 激活虚拟环境
env\Scripts\activate.bat
rem 在虚拟环境里使用清华源安装paddlepaddle 2.4.2
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple paddlepaddle==2.4.2
rem 在虚拟环境里使用清华源安装requirements.txt里的依赖
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
rem 在虚拟环境里使用清华源安装shapely和pyclipper
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple shapely pyclipper
rem 执行hub install chinese_ocr_db_crnn_server
hub install chinese_ocr_db_crnn_server
