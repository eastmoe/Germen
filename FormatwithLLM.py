import openai
import json
import logging

# 设置日志
logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG,
                    filename='./log/ai.log',
                    filemode='a')


# 加载配置文件里的URL以及key和模型的配置信息
with open("config.json", encoding='gb18030') as config:
    ConfigInfo = json.load(config)
    OpenAIURL=ConfigInfo["OpenAIURL"]
    LLMModel=ConfigInfo["LLMmodelName"]
    OpenAIAPIKEY=ConfigInfo["OpenAIAPIKEY"]

# 设置OpenAI API key
openai.api_key = OpenAIAPIKEY

# 指定API端点
openai.api_endpoint = OpenAIURL

# 函数，用于修饰文本格式
def FormatTextWithAI(OriText):
    logging.info(f"在{OpenAIURL}上使用{LLMModel}处理格式")
    # 组织语言
    send_msg="整理以下文本格式并按照正确分段返回，不得添加、减少任何字或者出现此以外的其他内容："+OriText
    # API请求
    response = openai.Completion.create(
        model=LLMModel,
        prompt=send_msg,
        temperature=0,  # 完全确定性
        top_p=0.01,  # 非常低的值，减少随机性
        frequency_penalty=0,  # 不改变高频词的使用
        presence_penalty=0  # 不改变低频词的使用
    )
    # 返回生成的文本
    return response.choices[0].text

