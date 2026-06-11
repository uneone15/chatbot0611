import json
import streamlit as st
from openai import OpenAI

# ── Season themes ──────────────────────────────────────────────────────────────
THEMES = {
    "🌸 봄": {
        "bg":       "#fff0f5",
        "sidebar":  "#ffe4ef",
        "msg_user": "#ffd6e7",
        "msg_ai":   "#fff9fb",
        "text":     "#4a1030",
        "border":   "#f9a8c9",
        "input_bg": "#fff0f5",
        "btn_bg":   "#f472b6",
        "btn_text": "#ffffff",
        "dot":      "#e75480",
    },
    "☀️ 여름": {
        "bg":       "#e8f8ff",
        "sidebar":  "#b3ecff",
        "msg_user": "#7dd3fc",
        "msg_ai":   "#f0faff",
        "text":     "#0c3547",
        "border":   "#38bdf8",
        "input_bg": "#e8f8ff",
        "btn_bg":   "#0ea5e9",
        "btn_text": "#ffffff",
        "dot":      "#0284c7",
    },
    "🍂 가을": {
        "bg":       "#fff7ed",
        "sidebar":  "#fde8cc",
        "msg_user": "#fdba74",
        "msg_ai":   "#fffbf5",
        "text":     "#431407",
        "border":   "#fb923c",
        "input_bg": "#fff7ed",
        "btn_bg":   "#ea580c",
        "btn_text": "#ffffff",
        "dot":      "#c2410c",
    },
    "❄️ 겨울": {
        "bg":       "#f0f4ff",
        "sidebar":  "#dbe4ff",
        "msg_user": "#a5b4fc",
        "msg_ai":   "#f8f9ff",
        "text":     "#1e1b4b",
        "border":   "#818cf8",
        "input_bg": "#f0f4ff",
        "btn_bg":   "#4f46e5",
        "btn_text": "#ffffff",
        "dot":      "#3730a3",
    },
    "🌙 밤": {
        "bg":       "#0f0f1a",
        "sidebar":  "#1a1a2e",
        "msg_user": "#2d2b55",
        "msg_ai":   "#16213e",
        "text":     "#e2e8f0",
        "border":   "#4c1d95",
        "input_bg": "#1a1a2e",
        "btn_bg":   "#7c3aed",
        "btn_text": "#ffffff",
        "dot":      "#a78bfa",
    },
    "🌿 숲": {
        "bg":       "#f0fdf4",
        "sidebar":  "#dcfce7",
        "msg_user": "#86efac",
        "msg_ai":   "#f7fef9",
        "text":     "#052e16",
        "border":   "#4ade80",
        "input_bg": "#f0fdf4",
        "btn_bg":   "#16a34a",
        "btn_text": "#ffffff",
        "dot":      "#166534",
    },
}

BASE_CSS = """
<style>
[data-testid="stAppViewContainer"] {{
    background-color: {bg} !important;
    color: {text} !important;
}}
[data-testid="stSidebar"] {{
    background-color: {sidebar} !important;
}}
[data-testid="stSidebar"] * {{ color: {text} !important; }}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
    background-color: {msg_user} !important;
    border: 1px solid {border};
    border-radius: 16px;
}}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {{
    background-color: {msg_ai} !important;
    border: 1px solid {border};
    border-radius: 16px;
}}
[data-testid="stTextInput"] input,
[data-testid="stChatInput"] textarea {{
    background-color: {input_bg} !important;
    color: {text} !important;
    border-color: {border} !important;
}}
[data-testid="stButton"] > button {{
    background-color: {btn_bg} !important;
    color: {btn_text} !important;
    border: none !important;
    border-radius: 8px !important;
}}
.typing-indicator span {{ background: {dot} !important; }}
hr {{ border-color: {border} !important; }}
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
    st.header("Settings")

    openai_api_key = st.text_input("OpenAI API Key", type="password")

    model = st.selectbox(
        "Model",
        options=["gpt-5.5", "gpt-5.5-instant", "gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        index=0,
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

    theme_name = st.selectbox("테마", options=list(THEMES.keys()), index=0)

    st.divider()

    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.subheader("Export chat")

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
