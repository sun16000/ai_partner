"""
AI 智能伴侣应用
会话管理（解决: 仅支持单一会话，无法实现多会话的创建、保存、切换）
>>功能模块：文件操作、新建会话、保存会话、加载历史会话、删除历史会话

📌 当前进度：第113&114集 - 会话管理-保存会话&新建会话
📅 最后更新：2026/4/19 16:48
💡 核心知识点：
  1. 将st.session_state中的会话数据保存到本地JSON文件
  2. 会话保存的触发逻辑与数据完整性校验
  3. 会话ID生成规则与新会话的状态初始化
  4. 新建会话时的界面状态同步逻辑
⚠️ 上版遗留问题：
  1. 仅掌握JSON操作，未实现实际的会话保存功能&创建新会话功能
✅ 本次完成功能：
  1. 实现会话数据保存到本地JSON文件的功能
  2. 完成对话历史的持久化存储，关闭应用后数据不丢失
  3. 实现新建会话功能，支持多对话并行
  4. 完成新建会话时的状态重置与界面刷新
📦 Git提交：[feat] 113&114. 会话管理-保存会话&新建会话
"""

import os
import streamlit as st
from openai import OpenAI
from datetime import datetime
import json

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

# 生成会话标识函数
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# 保存会话函数
def save_session():
    if st.session_state.current_session:
        # 构建新的会话对象
        session_data = {
            "messages": st.session_state.messages,
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session
        }
        # 如果sessions目录不存在则创建目录
        if not os.path.exists('sessions'):
            os.mkdir('sessions')
        # 保存会话数据
        with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

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

# 4.初始化会话标识（2026-04-16_23-13-14）
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()

# 在页面展示会话内容（遍历展示当前会话的聊天消息）
for message in st.session_state.messages: #message形式：{"role":"user", "content":user_prompt}
    st.chat_message(message["role"]).write(message["content"])

# 左侧侧边栏（with是sidebar的上下文管理器）
with st.sidebar:
    # 会话信息
    st.subheader("AI控制面板")
    # 新建会话（先保存当前会话再新建会话）
    if st.button("新建会话", width="stretch", icon="🖊️"):
        # 创建新会话
        # 设计逻辑：只有当当前会话已经存在聊天消息时，点击按钮才会真正创建一个新会话；否则按钮无效。注意：只修改性格和昵称不会触发创建新会话。
        # 目的：避免产生大量无聊天记录的空会话文件
        if st.session_state.messages:   #流程：有消息时才执行 → 保存旧会话 → 清空消息 → 生成新ID → 保存空会话 → 刷新页面
            # 保存当前会话（旧会话）
            save_session()
            # 新建空会话：将聊天消息列表置空，生成新的会话标识
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
            # 保存空会话（新会话）
            save_session()
            # 刷新会话消息列表
            st.rerun()

    # 伴侣信息
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

    # 作用：每次对话完成后自动保存到json文件
    # 缺陷：最后一次用户提问后，刷新页面，大模型回答不会被保存。
    # 解决方法：等待大模型回答之后再保存会话的效果更好
    # save_session()

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

    # 每次对话完成后立即保存当前会话到json文件（持久化到磁盘）
    save_session()


# 总结：
# 问题1：在侧边栏多次修改伴侣信息（昵称、性格）后，会出现修改成功但未生效的情况（代码逻辑没有问题）
# 原因：
#   历史对话消息（st.session_state.messages）中保存了之前基于旧伴侣信息生成的回复。大模型在生成新回复时，会同时参考：
#   当前的 system_prompt（已经更新为新性格）& 整个对话历史（包含旧性格下的问答）
#   由于历史消息中 assistant 的回复风格是旧的，模型会倾向于延续上下文中的风格，导致即使 system prompt 变了，实际回复依然“顽固”地保持旧样。
#   尤其是连续问“你是谁”这种问题，模型更容易直接重复历史中的答案。
#
# 问题2：点击新建会话后，聊天过程中刷新页面或关掉页面导致聊天记录丢失
# 解决方法：
#   在每次对话后(用户提问&大模型回答)，保存对话 --> 在大模型回答后调用save_session()

# 新建会话的设计逻辑：
# ①点击“新建会话”	            旧会话被保存，新会话的空 JSON 文件被创建
# ②在新会话中发送第一条消息	    助手回复后，自动调用 save_session()，会话文件被更新为包含完整对话
# ③继续发送多条消息	        每次问答结束后都会自动保存，刷新页面不会丢失任何聊天记录
# ④关闭应用再重新打开	        所有已保存的会话仍然存在（需要实现加载功能才能恢复）










