"""
AI 智能伴侣应用
📌 当前进度：第118集 - 功能优化与小结
🔄 上一版本：第117集 - 会话管理-删除会话
📅 最后更新：2026/4/XX HH:MM
💡 核心知识点：
  1. 代码重构：抽离重复逻辑为工具函数，优化代码结构
  2. 性能优化：提升流式输出、会话加载的运行效率
⚠️ 上版遗留问题：
  1. 代码存在重复逻辑，结构不够清晰，部分功能有优化空间
✅ 本次完成功能：
  1. 重构代码结构，抽离工具函数，提升可维护性
  2. 优化全流程功能，修复已知bug，完善用户体验
  3. 完成项目全流程总结，梳理核心知识点
📦 Git提交：[refactor] 118. 功能优化与小结
"""

import os
import streamlit as st
from openai import OpenAI
from datetime import datetime
import json

# 每一次重新执行py文件都会清楚或【覆盖】之前用户与大模型的问答
# print("------>每一次提问或刷新页面都会重新执行此文件，重新渲染展示页面！")

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

# 加载会话列表函数
def load_sessions():
    session_list = []
    # 加载sessions目录下的json文件
    if os.path.exists('sessions'):
        file_list = os.listdir('sessions')
        for filename in file_list:
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
        # 会话列表降序排序
        session_list.sort(reverse=True)
    return session_list

# 加载指定会话信息函数
def load_session(session_name):
    try:
        if os.path.exists('sessions'):  #健壮性判断
            with open(f"sessions/{session_name}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.messages = session_data["messages"]
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
                # 其他写法：st.session_state.current_session = session_name
                # 错误写法：st.session_state.current_session = session_data.current_session
                st.session_state.current_session = session_data["current_session"]
    except Exception:
        st.error("加载会话信息失败！")

# 删除指定会话函数
def delete_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):  #健壮性判断
            os.remove(f"sessions/{session_name}.json")
            # 如果删除的是当前会话，需要更新消息列表为空列表、更新会话名称为当前空会话的名称(如果删除的不是当前会话，消息列表无变化)
            if session_name == st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = generate_session_name()
                # 新增：保存空会话
                # 一个小缺陷：删除当前会话后，新生成的 current_session 没有立即保存为空会话文件，导致侧边栏会话列表暂时不显示它（但页面顶部显示它）
                # 如果删除的是当前会话，在生成新会话ID后调用一次 save_session() 来创建空会话文件，这样新会话会立即出现在列表中
                # save_session()
    except Exception:
        st.error("删除会话信息失败！")

# Streamlit页面全局配置
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

# 4.初始化会话标识（2026-04-16_23-13-14）
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()

# 展示会话名称
st.text(f"当前会话：{st.session_state.current_session}")
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

    st.text("会话历史")
    with st.container(height=270):  # 滚动条（固定高度，超出滚动）
        session_list = load_sessions()
        for session in session_list:
            col1, col2 = st.columns([4,1])
            # 历史会话
            with col1:  #三元运算符：值1 if 条件 else 值2 --> 在会话列表中高亮显示当前会话按钮
                if st.button(session, width="stretch", icon="🗒️", key=f"load_{session}", type="primary" if session == st.session_state.current_session else "secondary"):
                    load_session(session)
                    st.rerun()  # 只有加载会话信息完成后刷新页面才能将会话展示出来
            # 删除会话
            with col2:
                if st.button("", width="stretch", icon="❌", key=f"delete_{session}"):
                    delete_session(session)
                    st.rerun()

    # 分割线
    st.divider()

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
# 1. st.divider()   分割线
# 2. session_list.sort(reverse=True)    会话列表降序排序
# 3. st.container(height=270)   滚动条
# 4. 原始字符串 r"": 绝对路径在字符串前加 r（raw string），告诉 Python 不要对反斜杠进行转义，原样保留
#    举例：path = r"D:\Code\Python-Project\py-project01"













