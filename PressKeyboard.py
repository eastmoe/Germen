#模拟按键盘的程序
#因为众多模拟器都推出了可以用键盘模拟点击的操作，所以添加以按键来控制模拟器点按某个区域达到翻页的效果

import keyboard

#函数，作用是获取用户设置的自定义按键
def GetKey():
    key= input("请输入在模拟器中设置的按键，然后回车：")
    #使用keyboard.parse_hotkey()函数来将用户输入的字符串转换为按键列表
    UserSettingKey = keyboard.parse_hotkey(key)
    return UserSettingKey


