import streamlit as st
# 新的基于streamlit的Germen web客户端
import json
import os
import shutil
import logging

# 设置日志
logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG,
                    filename='./log/config.log',
                    filemode='a')

# 读取 config.json 文件
config_path = os.path.join(os.getcwd(), 'config.json')
print(config_path)
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
else:
    st.error("config.json 文件不存在")
    st.stop()

# 创建 Streamlit 应用程序
st.title('配置编辑器')

# 显示当前配置
st.subheader('当前配置')
st.write(config)

# 为每个参数设置文本标签和文本输入框
# 为每个参数设置文本标签和文本输入框，并添加注释
edited_config = {}

st.subheader('图片文件夹路径')
st.markdown('**PictureDir**: 截图图片保存路径')
edited_config['PictureDir'] = st.text_input('修改 PictureDir', config['PictureDir'])

st.subheader('OCR 输出文本文件夹路径')
st.markdown('**OCROutPaDir**: 将图片OCR处理后输出的文本文件保存路径')
edited_config['OCROutPaDir'] = st.text_input('修改 OCROutPaDir', config['OCROutPaDir'])

st.subheader('合并路径')
st.markdown('**MergeBookDir**: 将所有文本文件片段合并之后的文本文件输出路径')
edited_config['MergeBookDir'] = st.text_input('修改 MergeBookDir', config['MergeBookDir'])

st.subheader('最终输出路径')
st.markdown('**FinalNovelDir**: 最终生成的小说文件所在的路径')
edited_config['FinalNovelDir'] = st.text_input('修改 FinalNovelDir', config['FinalNovelDir'])

st.subheader('周期')
st.markdown('**Cycle**: 自动翻页/截图的等待时间周期')
edited_config['Cycle'] = st.text_input('修改 Cycle', config['Cycle'])

st.subheader('OpenAI URL')
st.markdown('**OpenAIURL**: 用于格式处理的与OpenAI兼容的API的URL地址')
edited_config['OpenAIURL'] = st.text_input('修改 OpenAIURL', config['OpenAIURL'])

st.subheader('OpenAI API KEY')
st.markdown('**OpenAIAPIKEY**: 用于格式处理的与OpenAI兼容的API密钥')
edited_config['OpenAIAPIKEY'] = st.text_input('修改 OpenAIAPIKEY', config['OpenAIAPIKEY'])

st.subheader('LLM 模型名称')
st.markdown('**LLMmodelName**: 用于格式处理的大语言模型名')
edited_config['LLMmodelName'] = st.text_input('修改 LLMmodelName', config['LLMmodelName'])

#---------------------按钮区---------------------------

# 保存按钮
if st.button('保存修改'):
    with open(config_path, 'w') as f:
        json.dump(edited_config, f, indent=4)
    logging.info("配置已保存")
    st.success('配置已保存')

# 清理缓存按钮
if st.button('清理缓存', key='clean_cache_button', help='清空指定目录下的所有文件'):
    # st.warning('你确定要清空以下目录下的所有文件吗？\n\n'
    #            f'- {config["PictureDir"]}\n'
    #            f'- {config["OCROutPaDir"]}\n'
    #            f'- {config["MergeBookDir"]}\n')
    # if st.button('确认', key='confirm_clean_cache_button'):
        directories = [config['PictureDir'], config['OCROutPaDir'], config['MergeBookDir']]
        # 建立文件列表
        filelists = []
        # 遍历指定目录下的所有文件和子目录，使用 os.unlink 删除文件，使用 shutil.rmtree 删除目录。
        for directory in directories:
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    filelists.append(file_path)
                    print(filelists)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.remove(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        st.error(f'Failed to delete {file_path}. Reason: {e}')
                st.success(f'{directory} 目录已清空')
                logging.info(f"{directory} 目录已清空，以下文件已删除：{filelists}")
                filelists = []
            else:
                logging.error("缓存目录不正确或不存在。")
                st.error(f'{directory} 目录不存在')
