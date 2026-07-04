#模拟按键盘的程序
#因为众多模拟器都推出了可以用键盘模拟点击的操作，所以添加以按键来控制模拟器点按某个区域达到翻页的效果

import logging

from .log_utils import LOG_DIR

# 设置日志
logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.INFO,
                    filename=LOG_DIR / 'input.log',
                    filemode='a')

#函数，作用是获取用户设置的自定义按键
def GetKey():
    key= input("请输入在模拟器中设置的按键，然后回车：")
    UserSettingKey = key.strip()
    logging.info(f"获取到的用户自定义翻页按键是：{UserSettingKey}")
    return UserSettingKey

def TestFeature():
    while True:
        GetKey()
    return 0

