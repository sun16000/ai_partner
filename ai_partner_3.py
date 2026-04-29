"""
AI 智能伴侣应用
📌 当前进度：第108集 - 侧边栏制作
🔄 上一版本：第107集 - 流式输出
📅 最后更新：2026/4/14 22:38
💡 核心知识点：
  1. st.sidebar 实现侧边栏布局，用于会话列表/功能入口
  2. 侧边栏组件与主页面的交互逻辑
⚠️ 上版遗留问题：
  1. 无专门的会话管理入口，无法快速切换/管理对话
  2. *页面刷新会重新执行脚本，会话记录会被清除，会话无法持久化存储*
✅ 本次完成功能：
  1. 用st.sidebar制作应用侧边栏
  2. 搭建会话列表入口，为后续会话管理做准备
📦 Git提交：[feat] 108. 侧边栏制作
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

# system_prompt = "你是一个助手，你的名字叫智能丫鬟，你的回答风格幽默搞笑、简洁、条理分明"
system_prompt = """
        你叫%s，现在是用户的真实伴侣，请完全代入伴侣角色。：
        规则：
            1. 每次只回1条消息
            2. 禁止任何场景或状态描述性文字
            3. 匹配用户的语言
            4. 回复简短，像微信聊天一样
            5. 有需要的话可以用❤️🌸等emoji表情
            6. 用符合伴侣性格的方式对话
            7. 回复的内容, 要充分体现伴侣的性格特征
        伴侣性格：
            - %s
        你必须严格遵守上述规则来回复用户。
    """

# 初始化当前会话
# 1.初始化聊天消息（初始化一次会话的所有聊天记录，聊天记录初始为空列表）
# st.session_state的每一个元素是字典类型的， messages是字典的key，聊天记录列表是字典的value
# 举例："messages": [{},{},{}...] --> "AI对人类利弊的讨论": [{用户,问题1}, {助手, 回答1}, {用户,问题2}, {助手, 回答2}, {},{}...]）
if "messages" not in st.session_state:
    # 所有 用户或大模型的消息 存储在st.session_state.messages列表中
    # 列表元素是一个字典[{"role":"user", "content":"..."}, {"role":"assistant", "content":"..."}, {}...}
    st.session_state["messages"] = []
# 2.初始化昵称
if "nick_name" not in st.session_state:
    st.session_state["nick_name"] = "东北雨姐"
# 3.初始化性格
if "nature" not in st.session_state:
    st.session_state["nature"] = "活泼开朗的东北姑娘"

# 在页面展示会话内容（遍历展示当前会话的聊天消息）
for message in st.session_state.messages: #message形式：{"role":"user", "content":user_prompt}
    st.chat_message(message["role"]).write(message["content"])

# 左侧侧边栏（with语句是sidebar的上下文管理器）
with st.sidebar:
    st.subheader("伴侣信息")  #!!! 昵称和性格多次修改后，提示词的昵称和性格会失效！！！
    # 昵称输入框，同时将用户昵称保存到当前会话
    nick_name = st.text_input("昵称", placeholder="请输入伴侣昵称", value=st.session_state.nick_name) #文本框：单行文字；placeholder：提示信息；value: 默认值
    if nick_name:
        st.session_state.nick_name = nick_name

    # 性格输入框，同时将性格保存到当前会话
    nature = st.text_area("性格", placeholder="请输入伴侣性格", value=st.session_state.nature) #文本域：可以输入多行文字
    if nature:
        st.session_state.nature = nature



# (消息输入框)用户输入问题
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
        messages = [    #昵称，性格变动之后及时更新提示词
            {"role": "system", "content": system_prompt % (st.session_state.nick_name, st.session_state.nature)},
            # {"role": "user", "content": user_prompt},
            # 关键操作！
            # 调用大模型之前，将当前会话的所有聊天记录一起发给大模型（会话的消息列表 [解包] 追加到messages中）
            *st.session_state.messages
        ],
        stream=True #流式输出
    )


    # 3.输出大模型的返回结果(非流式输出的解析方式)
    # ai_answer = response.choices[0].message.content
    # print(f"<------大模型返回结果：{ai_answer}")
    # st.chat_message("assistant").write(ai_answer)

    # 创建一个空组件，用于存储大模型返回的结果。st.empty () = 先占一个位置，后面可以反复替换 / 刷新里面的内容
    response_message = st.empty()
    full_response = ""
    # 3.输出大模型的返回结果(流式输出的解析方式) --> 流式输出导致response对象由多个数据包对象（chunk）组成，每个数据包对象的内容是一个字或词
    for chunk in response:  #每个chunk是一个数据包对象
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            # 每一次循环都会覆盖上一次输出的内容
            response_message.chat_message("assistant").write(full_response)

    # 将大模型的回答追加到会话列表
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# 总结：
# 代码逻辑没有问题。但是在侧边栏多次修改伴侣信息（昵称、性格）后，会出现修改成功但未生效的情况。
# 原因：
#   历史对话消息（st.session_state.messages）中保存了之前基于旧伴侣信息生成的回复。大模型在生成新回复时，会同时参考：
#   当前的 system_prompt（已经更新为新性格）& 整个对话历史（包含旧性格下的问答）
#   由于历史消息中 assistant 的回复风格是旧的，模型会倾向于延续上下文中的风格，导致即使 system prompt 变了，实际回复依然“顽固”地保持旧样。
#   尤其是连续问“你是谁”这种问题，模型更容易直接重复历史中的答案。










