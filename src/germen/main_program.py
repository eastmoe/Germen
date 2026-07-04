from . import workflow
from .app_config import load_config


def print_event(message, payload):
    print(message)


def main():
    config = load_config()
    print("Germen 命令行模式将使用 config.json 中的配置执行采集、合并与格式化。")
    print("更完整的配置与控制请运行: germen ui")
    input("确认截图区域和翻页方式已配置后按回车开始。")
    workflow.run_capture(config, callback=print_event, pin_window=True)
    merged_file = workflow.merge_book(config, print_event)
    final_file = workflow.format_book(merged_file, config, print_event)
    print(f"完成，最终文件位于: {final_file}")


if __name__ == "__main__":
    main()

