"""
AI 智能伴侣应用
当前进度：第105集 - 展示会话列表（缓存聊天记录）
上一版本：第104集 - 界面基本布局
最后更新：2026/4/12 23:51

核心知识点：
    1. st.session_state 初始化会话消息列表，缓存用户与AI的对话历史
上版遗留问题：
    1. 每一次提问或刷新页面都会重新执行脚本，会话记录会被清除/覆盖
本次完成功能：
    1. 初始化st.session_state.messages，缓存对话历史
不足之处：
    1.页面刷新会重新执行脚本，会话记录会被清除，会话无法持久化存储
    2.会话没有记忆功能。大模型无法根据之前的聊天记录回答用户的问题

Git提交：[feat] 105. 展示会话列表
"""

import os
import streamlit as st
from openai import OpenAI

# 每一次重新执行py文件都会清楚或【覆盖】之前用户与大模型的问答
# print("------>每一次提问或刷新页面都会重新执行此文件，重新渲染展示页面！")

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

# 初始化聊天消息（初始化一次会话的所有聊天记录，聊天记录初始为空列表）
# st.session_state的每一个元素是字典类型的， messages是字典的key，聊天记录列表是字典的value
# 举例："messages": [{},{},{}...] --> "AI对人类利弊的讨论": [{用户,问题1}, {助手, 回答1}, {用户,问题2}, {助手, 回答2}, {},{}...]）
if "messages" not in st.session_state:
    # 所有 用户或大模型的消息 存储在st.session_state.messages列表中
    # 列表元素是一个字典[{"role":"user", "content":"..."}, {"role":"assistant", "content":"..."}, {}...}
    st.session_state["messages"] = []

#展示会话内容（遍历展示当前会话的聊天消息）
for message in st.session_state.messages: #message形式：{"role":"user", "content":user_prompt}
    st.chat_message(message["role"]).write(message["content"])


# 用户输入问题
user_prompt = st.chat_input("请输入你的问题")
if user_prompt:
    # name ("user", "assistant", "ai", "human", or str)
    st.chat_message("user").write(user_prompt)
    print("------>调用AI大模型。提示词：",user_prompt)
    #将用户问题追加到会话列表
    st.session_state.messages.append({"role":"user", "content":user_prompt})


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

    # 将大模型的回答追加到会话列表
    st.session_state.messages.append({"role": "assistant", "content": ai_answer})



