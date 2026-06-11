import json
import streamlit as st
from openai import OpenAI

# ── Season themes ──────────────────────────────────────────────────────────────
# btn_bg 대비비 (vs #ffffff) 검증:
#   봄  #be185d  L≈0.130  → 5.83:1 ✓
#   여름 #0369a1  L≈0.130  → 5.83:1 ✓
#   가을 #9a3412  L≈0.099  → 7.07:1 ✓
#   겨울 #4338ca  L≈0.108  → 6.56:1 ✓
#   밤  #6d28d9  L≈0.113  → 6.28:1 ✓
#   숲  #166534  L≈0.095  → 7.24:1 ✓
THEMES = {
    "🌸 봄": {
        "bg":        "#fff0f5",
        "sidebar":   "#ffe4ef",
        "msg_user":  "#ffd6e7",
        "msg_ai":    "#fff9fb",
        "text":      "#3d0a22",   # 배경 대비 15:1+
        "text_msg":  "#3d0a22",
        "border":    "#f9a8c9",
        "input_bg":  "#fff0f5",
        "btn_bg":    "#be185d",   # 5.83:1 vs white
        "btn_text":  "#ffffff",
        "dot":       "#be185d",
        "placeholder": "#a05070",
    },
    "☀️ 여름": {
        "bg":        "#e8f8ff",
        "sidebar":   "#b3ecff",
        "msg_user":  "#7dd3fc",
        "msg_ai":    "#f0faff",
        "text":      "#082535",   # 배경 대비 13:1+
        "text_msg":  "#082535",
        "border":    "#38bdf8",
        "input_bg":  "#e8f8ff",
        "btn_bg":    "#0369a1",   # 5.83:1 vs white
        "btn_text":  "#ffffff",
        "dot":       "#0369a1",
        "placeholder": "#2a6a8a",
    },
    "🍂 가을": {
        "bg":        "#fff7ed",
        "sidebar":   "#fde8cc",
        "msg_user":  "#fdba74",
        "msg_ai":    "#fffbf5",
        "text":      "#341007",   # 배경 대비 14:1+
        "text_msg":  "#341007",
        "border":    "#fb923c",
        "input_bg":  "#fff7ed",
        "btn_bg":    "#9a3412",   # 7.07:1 vs white
        "btn_text":  "#ffffff",
        "dot":       "#9a3412",
        "placeholder": "#7a4020",
    },
    "❄️ 겨울": {
        "bg":        "#f0f4ff",
        "sidebar":   "#dbe4ff",
        "msg_user":  "#a5b4fc",
        "msg_ai":    "#f8f9ff",
        "text":      "#1a1740",   # 배경 대비 13:1+
        "text_msg":  "#1a1740",
        "border":    "#818cf8",
        "input_bg":  "#f0f4ff",
        "btn_bg":    "#4338ca",   # 6.56:1 vs white
        "btn_text":  "#ffffff",
        "dot":       "#4338ca",
        "placeholder": "#4a47a0",
    },
    "🌙 밤": {
        "bg":        "#0f0f1a",
        "sidebar":   "#1a1a2e",
        "msg_user":  "#2d2b55",
        "msg_ai":    "#16213e",
        "text":      "#e2e8f0",   # 배경 대비 13:1+
        "text_msg":  "#e2e8f0",
        "border":    "#6d28d9",
        "input_bg":  "#1a1a2e",
        "btn_bg":    "#6d28d9",   # 6.28:1 vs white
        "btn_text":  "#ffffff",
        "dot":       "#a78bfa",
        "placeholder": "#94a3b8",
    },
    "🌿 숲": {
        "bg":        "#f0fdf4",
        "sidebar":   "#dcfce7",
        "msg_user":  "#86efac",
        "msg_ai":    "#f7fef9",
        "text":      "#032b14",   # 배경 대비 15:1+
        "text_msg":  "#032b14",
        "border":    "#4ade80",
        "input_bg":  "#f0fdf4",
        "btn_bg":    "#166534",   # 7.24:1 vs white
        "btn_text":  "#ffffff",
        "dot":       "#166534",
        "placeholder": "#2a6645",
    },
}

BASE_CSS = """
<style>
/* 전체 배경 · 기본 텍스트 */
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {{
    background-color: {bg} !important;
    color: {text} !important;
}}
/* 제목 · 본문 텍스트 */
[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] span:not(.typing-indicator span) {{
    color: {text} !important;
}}

/* 사이드바 */
[data-testid="stSidebar"] {{
    background-color: {sidebar} !important;
}}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {{
    color: {text} !important;
}}
[data-testid="stSidebar"] h2 {{
    color: #ffffff !important;
}}

/* 채팅 버블 — 사용자 */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
    background-color: {msg_user} !important;
    border: 1px solid {border};
    border-radius: 16px;
}}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) div {{
    color: {text_msg} !important;
}}

/* 채팅 버블 — AI */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {{
    background-color: {msg_ai} !important;
    border: 1px solid {border};
    border-radius: 16px;
}}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) p,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) div {{
    color: {text_msg} !important;
}}

/* 입력창 */
[data-testid="stTextInput"] input,
[data-testid="stChatInput"] textarea {{
    background-color: {input_bg} !important;
    color: {text} !important;
    border-color: {border} !important;
}}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stChatInput"] textarea::placeholder {{
    color: {placeholder} !important;
    opacity: 1 !important;
}}

/* 버튼 — WCAG AA 충족 */
[data-testid="stButton"] > button,
[data-testid="stDownloadButton"] > button {{
    background-color: {btn_bg} !important;
    color: {btn_text} !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}}
[data-testid="stButton"] > button:hover,
[data-testid="stDownloadButton"] > button:hover {{
    filter: brightness(1.12) !important;
}}

/* 타이핑 인디케이터 */
.typing-indicator span {{ background: {dot} !important; }}

/* 구분선 */
hr {{ border-color: {border} !important; opacity: 0.5; }}
</style>
"""

TYPING_CSS = """
<style>
.typing-indicator {
    display: flex; align-items: center; gap: 4px; padding: 8px 4px;
}
.typing-indicator span {
    width: 8px; height: 8px; border-radius: 50%; background: #888;
    animation: bounce 1.2s infinite ease-in-out;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
    0%, 80%, 100% { transform: scale(0.7); opacity: 0.5; }
    40%            { transform: scale(1.1); opacity: 1;   }
}
</style>
"""

TYPING_HTML = """
<div class="typing-indicator">
    <span></span><span></span><span></span>
</div>
"""

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="💬 Chatbot", layout="centered")

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    openai_api_key = st.text_input("OpenAI API Key", type="password")

    st.divider()
    st.subheader("🎨 테마")
    theme_name = st.selectbox(
        "채팅 테마 선택",
        options=list(THEMES.keys()),
        index=list(THEMES.keys()).index("🌙 밤"),
        label_visibility="collapsed",
    )

    st.divider()
    st.subheader("🤖 모델")
    model = st.selectbox(
        "Model",
        options=["gpt-5.5", "gpt-5.5-instant", "gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        index=0,
        label_visibility="collapsed",
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="낮을수록 일관된 답변, 높을수록 창의적인 답변",
    )

    st.divider()

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.subheader("💾 Export chat")

    messages = st.session_state.get("messages", [])

    txt_content = "\n\n".join(
        f"[{m['role'].upper()}]\n{m['content']}" for m in messages
    )
    st.download_button(
        label="Download .txt",
        data=txt_content,
        file_name="chat_history.txt",
        mime="text/plain",
        disabled=not messages,
        use_container_width=True,
    )

    json_content = json.dumps(messages, ensure_ascii=False, indent=2)
    st.download_button(
        label="Download .json",
        data=json_content,
        file_name="chat_history.json",
        mime="application/json",
        disabled=not messages,
        use_container_width=True,
    )

# ── Apply CSS ──────────────────────────────────────────────────────────────────
theme = THEMES[theme_name]
st.markdown(TYPING_CSS, unsafe_allow_html=True)
st.markdown(BASE_CSS.format(**theme), unsafe_allow_html=True)

# ── Main ───────────────────────────────────────────────────────────────────────
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot using OpenAI's models. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys)."
)

if not openai_api_key:
    st.info("Please add your OpenAI API key in the sidebar to continue.", icon="🗝️")
else:
    client = OpenAI(api_key=openai_api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            with st.chat_message("assistant"):
                typing_placeholder = st.empty()
                typing_placeholder.markdown(TYPING_HTML, unsafe_allow_html=True)

                stream = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    temperature=temperature,
                    stream=True,
                )

                typing_placeholder.empty()
                response = st.write_stream(stream)

            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"Error: {e}", icon="🚨")
