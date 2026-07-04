import json
import logging
import os

from openai import OpenAI

# 设置日志
logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG,
                    filename='./log/ai.log',
                    filemode='a')


def _load_openai_settings():
    with open("config.json", encoding='utf-8-sig') as config:
        config_info = json.load(config)
    openai_url = config_info.get("OpenAIURL", "https://api.openai.com/v1")
    llm_model = config_info.get("LLMmodelName", config_info.get("OpenAIOCRModel", "gpt-4.1-mini"))
    openai_api_key = config_info.get("OpenAIAPIKEY", "") or os.getenv("OPENAI_API_KEY")
    return openai_url, llm_model, openai_api_key

# 函数，用于修饰文本格式
def FormatTextWithAI(OriText):
    OpenAIURL, LLMModel, OpenAIAPIKEY = _load_openai_settings()
    client = OpenAI(
        api_key=OpenAIAPIKEY,
        base_url=OpenAIURL or None,
    )
    logging.info(f"在{OpenAIURL}上使用{LLMModel}处理格式")
    # 组织语言
    send_msg="整理以下文本格式并按照正确分段返回，不得添加、减少任何字或者出现此以外的其他内容："+OriText
    # API请求
    response = client.chat.completions.create(
        model=LLMModel,
        messages=[{"role": "user", "content": send_msg}],
        temperature=0,  # 完全确定性
        top_p=0.01,  # 非常低的值，减少随机性
        frequency_penalty=0,  # 不改变高频词的使用
        presence_penalty=0  # 不改变低频词的使用
    )
    # 返回生成的文本
    return response.choices[0].message.content

