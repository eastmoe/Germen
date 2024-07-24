#查询内训占用的程序
import psutil
import inspect
import sys
from pympler import asizeof, muppy,summary
import logging

# 设置日志
logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.INFO,
                    filename='./log/performance.log',
                    filemode='a')


def ShowMemoryUse():
    # 获取当前进程的内存信息
    p = psutil.Process()
    m = p.memory_info()
    print("进程内存信息：")
    logging.info(f"内存信息:常驻内存集：{m.rss / 1024 / 1024} MB\n虚拟内存集：{m.vms / 1024 / 1024} MB")
    print(f"常驻内存集：{m.rss / 1024 / 1024} MB")
    print(f"虚拟内存集：{m.vms / 1024 / 1024} MB")
    #print(f"共享内存：{m.shared / 1024 / 1024} MB")
    #print(f"文本内存：{m.text / 1024 / 1024} MB")
    #print(f"库内存：{m.lib / 1024 / 1024} MB")
    #print(f"数据内存：{m.data / 1024 / 1024} MB")
    #print(f"脏内存：{m.dirty / 1024 / 1024} MB")

    # 获取系统的虚拟内存信息
    v = psutil.virtual_memory()
    logging.info(f"虚拟内存信息:总内存：{v.total / 1024 / 1024} MB\n可用内存：{v.available / 1024 / 1024} MB\n内存使用率：{v.percent} %\n已用内存：{v.used / 1024 / 1024} MB\n空闲内存：{v.free / 1024 / 1024} MB")
    print("虚拟内存信息：")
    print(f"总内存：{v.total / 1024 / 1024} MB")
    print(f"可用内存：{v.available / 1024 / 1024} MB")
    print(f"内存使用率：{v.percent} %")
    print(f"已用内存：{v.used / 1024 / 1024} MB")
    print(f"空闲内存：{v.free / 1024 / 1024} MB")
    #print(f"活跃内存：{v.active / 1024 / 1024} MB")
    #print(f"非活跃内存：{v.inactive / 1024 / 1024} MB")
    #print(f"有线内存：{v.wired / 1024 / 1024} MB")

    # 获取系统的交换内存信息
    s = psutil.swap_memory()
    logging.info(f"交换内存信息:总交换内存：{s.total / 1024 / 1024} MB\n已用交换内存：{s.used / 1024 / 1024} MB\n空闲交换内存：{s.free / 1024 / 1024} MB\n交换内存使用率：{s.percent} %")
    print("交换内存信息：")
    print(f"总交换内存：{s.total / 1024 / 1024} MB")
    print(f"已用交换内存：{s.used / 1024 / 1024} MB")
    print(f"空闲交换内存：{s.free / 1024 / 1024} MB")
    print(f"交换内存使用率：{s.percent} %")
    #print(f"交换内存输入：{s.sin / 1024 / 1024} MB")
    #print(f"交换内存输出：{s.sout / 1024 / 1024} MB")
    return 0

# 输出list对象的名称和大小
def PrintListMemory():
    # 获取当前模块的所有成员
    all_members = inspect.getmembers(sys.modules[__name__])
    # 遍历每个成员
    for name, obj in all_members:
        # 判断是否是list类型
        if isinstance(obj, list):
            # 打印出名称和大小
            print(name, asizeof.asizeof(obj))


# 显示各种类型对象的内存占用
def ShowMemoryType():
    # 使用muppy.get_objects()来获取所有活跃的Python对象
    object = muppy.get_objects()
    # 使用summary.summarize(objects)来对对象进行分类和统计，返回一个列表，每个元素包含了类型、数量和总大小4
    summary_list = summary.summarize(object)
    # 使用summary.print_(summary_list)来打印出统计结果
    logging.debug(f"内存使用情况:{summary_list}")
    summary.print_(summary_list)

ShowMemoryType()
#ShowMemoryUse()
