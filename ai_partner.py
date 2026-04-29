"""
AI 智能伴侣应用
当前进度：第104集 - 界面基本布局
最后更新：2026/4/12 21:30

本次完成功能:
1. 导入streamlit库，完成基础环境验证
2. 调用`st.set_page_config()`配置页面：标题、图标、宽屏布局
3. 用`st.title()`添加大标题，`st.logo()`添加项目Logo
4. st.chat_input() 实现用户聊天输入框
5. st.chat_message() 实现用户/大模型消息气泡展示
"""

import os

import streamlit as st
from openai import OpenAI


st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="👹",
    #布局：layout ("centered", "wide", or None)
    layout="wide",
    #侧边栏
    initial_sidebar_state="expanded",
    #配置此页面右上角三个点显示的菜单
    menu_items={
        'Get Help': 'https://www.bilibili.com/',
        'Report a bug': "https://sports.qq.com/nba/",
        'About': "# 这是一个AI智能问答app~👹"
    }
)

# 大标题
st.title("AI智能伴侣")
# logo
st.logo("resources/AI_logo.png", size="large")

#调用大模型回答问题
#1.创建与AI大模型交互的客户端对象
client = OpenAI(
    api_key = os.environ.get("DEEPSEEK_API_KEY"),
    base_url = "https://api.deepseek.com"
)

system_prompt = "你是一个助手，你的名字叫智能丫鬟，你的回答风格幽默搞笑、简洁、条理分明"
# 用户输入问题
user_prompt = st.chat_input("请输入你的问题")
if user_prompt:
    # name ("user", "assistant", "ai", "human", or str)
    st.chat_message("user").write(user_prompt)
    print("------>调用AI大模型。提示词：",user_prompt)


    #2.与AI大模型进行交互
    response = client.chat.completions.create(
        model = "deepseek-chat",
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        stream=False
    )
    #3.输出大模型的返回结果
    ai_answer = response.choices[0].message.content
    print(f"<------大模型返回结果：{ai_answer}")

    st.chat_message("assistant").write(ai_answer)



