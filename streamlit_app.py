import base64
import io
import json
import streamlit as st
from openai import OpenAI
from audio_recorder_streamlit import audio_recorder

# ── SVG background patterns (opacity baked into shapes) ────────────────────────
def _uri(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

_SVG = {
    "🌸 봄": _uri("""<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300">
  <g transform="translate(65,65)">
    <ellipse rx="18" ry="8" fill="#f9a8c9" opacity="0.22" transform="rotate(0)"/>
    <ellipse rx="18" ry="8" fill="#fda4af" opacity="0.22" transform="rotate(72)"/>
    <ellipse rx="18" ry="8" fill="#f9a8c9" opacity="0.22" transform="rotate(144)"/>
    <ellipse rx="18" ry="8" fill="#fda4af" opacity="0.22" transform="rotate(216)"/>
    <ellipse rx="18" ry="8" fill="#f9a8c9" opacity="0.22" transform="rotate(288)"/>
    <circle r="6" fill="#f472b6" opacity="0.28"/>
  </g>
  <g transform="translate(220,210)">
    <ellipse rx="14" ry="6" fill="#fda4af" opacity="0.18" transform="rotate(0)"/>
    <ellipse rx="14" ry="6" fill="#f9a8c9" opacity="0.18" transform="rotate(72)"/>
    <ellipse rx="14" ry="6" fill="#fda4af" opacity="0.18" transform="rotate(144)"/>
    <ellipse rx="14" ry="6" fill="#f9a8c9" opacity="0.18" transform="rotate(216)"/>
    <ellipse rx="14" ry="6" fill="#fda4af" opacity="0.18" transform="rotate(288)"/>
    <circle r="5" fill="#f472b6" opacity="0.22"/>
  </g>
  <ellipse cx="170" cy="60"  rx="11" ry="5" fill="#f9a8c9" opacity="0.14" transform="rotate(40 170 60)"/>
  <ellipse cx="90"  cy="190" rx="11" ry="5" fill="#fda4af" opacity="0.14" transform="rotate(-25 90 190)"/>
  <ellipse cx="240" cy="110" rx="9"  ry="4" fill="#f9a8c9" opacity="0.12" transform="rotate(60 240 110)"/>
  <ellipse cx="40"  cy="260" rx="9"  ry="4" fill="#fda4af" opacity="0.12" transform="rotate(-50 40 260)"/>
  <ellipse cx="260" cy="270" rx="9"  ry="4" fill="#f9a8c9" opacity="0.12" transform="rotate(15 260 270)"/>
</svg>"""),

    "☀️ 여름": _uri("""<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300">
  <path d="M0 60 C40 40,80 80,120 60 C160 40,200 80,240 60 C270 45,290 65,300 60"
        fill="none" stroke="#38bdf8" stroke-width="3" opacity="0.18"/>
  <path d="M0 120 C40 100,80 140,120 120 C160 100,200 140,240 120 C270 105,290 125,300 120"
        fill="none" stroke="#7dd3fc" stroke-width="3" opacity="0.16"/>
  <path d="M0 180 C40 160,80 200,120 180 C160 160,200 200,240 180 C270 165,290 185,300 180"
        fill="none" stroke="#38bdf8" stroke-width="3" opacity="0.14"/>
  <path d="M0 240 C40 220,80 260,120 240 C160 220,200 260,240 240 C270 225,290 245,300 240"
        fill="none" stroke="#7dd3fc" stroke-width="3" opacity="0.12"/>
  <circle cx="240" cy="55"  r="28" fill="#fde68a" opacity="0.13"/>
  <circle cx="240" cy="55"  r="20" fill="#fde68a" opacity="0.10"/>
  <circle cx="75"  cy="220" r="10" fill="#7dd3fc" opacity="0.18"/>
  <circle cx="200" cy="250" r="7"  fill="#38bdf8" opacity="0.15"/>
  <circle cx="150" cy="100" r="5"  fill="#7dd3fc" opacity="0.14"/>
</svg>"""),

    "🍂 가을": _uri("""<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300">
  <ellipse cx="60"  cy="70"  rx="22" ry="11" fill="#fdba74" opacity="0.22" transform="rotate(-35 60 70)"/>
  <ellipse cx="58"  cy="68"  rx="10" ry="20" fill="#fb923c" opacity="0.16" transform="rotate(-35 58 68)"/>
  <ellipse cx="200" cy="180" rx="20" ry="10" fill="#f97316" opacity="0.20" transform="rotate(20 200 180)"/>
  <ellipse cx="198" cy="178" rx="9"  ry="18" fill="#fdba74" opacity="0.14" transform="rotate(20 198 178)"/>
  <ellipse cx="240" cy="60"  rx="16" ry="8"  fill="#ef4444" opacity="0.18" transform="rotate(55 240 60)"/>
  <ellipse cx="80"  cy="230" rx="18" ry="9"  fill="#fb923c" opacity="0.18" transform="rotate(-15 80 230)"/>
  <ellipse cx="160" cy="120" rx="12" ry="6"  fill="#fdba74" opacity="0.14" transform="rotate(40 160 120)"/>
  <ellipse cx="270" cy="250" rx="14" ry="7"  fill="#f97316" opacity="0.16" transform="rotate(-30 270 250)"/>
  <ellipse cx="130" cy="270" rx="10" ry="5"  fill="#ef4444" opacity="0.14" transform="rotate(10 130 270)"/>
</svg>"""),

    "❄️ 겨울": _uri("""<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300">
  <g transform="translate(60,70)" stroke="#a5b4fc" stroke-width="2.5" opacity="0.22">
    <line x1="0" y1="-26" x2="0" y2="26"/><line x1="-26" y1="0" x2="26" y2="0"/>
    <line x1="-18" y1="-18" x2="18" y2="18"/><line x1="18" y1="-18" x2="-18" y2="18"/>
    <circle r="4" fill="#a5b4fc" stroke="none"/>
  </g>
  <g transform="translate(220,180)" stroke="#818cf8" stroke-width="2" opacity="0.18">
    <line x1="0" y1="-20" x2="0" y2="20"/><line x1="-20" y1="0" x2="20" y2="0"/>
    <line x1="-14" y1="-14" x2="14" y2="14"/><line x1="14" y1="-14" x2="-14" y2="14"/>
    <circle r="3" fill="#818cf8" stroke="none"/>
  </g>
  <g transform="translate(240,60)" stroke="#c7d2fe" stroke-width="1.5" opacity="0.16">
    <line x1="0" y1="-15" x2="0" y2="15"/><line x1="-15" y1="0" x2="15" y2="0"/>
    <line x1="-10" y1="-10" x2="10" y2="10"/><line x1="10" y1="-10" x2="-10" y2="10"/>
  </g>
  <g transform="translate(80,230)" stroke="#a5b4fc" stroke-width="1.5" opacity="0.15">
    <line x1="0" y1="-16" x2="0" y2="16"/><line x1="-16" y1="0" x2="16" y2="0"/>
    <line x1="-11" y1="-11" x2="11" y2="11"/><line x1="11" y1="-11" x2="-11" y2="11"/>
  </g>
  <circle cx="160" cy="150" r="3" fill="#818cf8" opacity="0.20"/>
  <circle cx="270" cy="270" r="3" fill="#a5b4fc" opacity="0.18"/>
  <circle cx="30"  cy="140" r="2" fill="#c7d2fe" opacity="0.18"/>
  <circle cx="200" cy="40"  r="2" fill="#a5b4fc" opacity="0.16"/>
</svg>"""),

    "🌙 밤": _uri("""<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300">
  <circle cx="60"  cy="50"  r="2.5" fill="#ffffff" opacity="0.35"/>
  <circle cx="140" cy="30"  r="1.5" fill="#e2e8f0" opacity="0.28"/>
  <circle cx="230" cy="70"  r="3"   fill="#ffffff" opacity="0.32"/>
  <circle cx="280" cy="40"  r="1.5" fill="#c7d2fe" opacity="0.28"/>
  <circle cx="30"  cy="130" r="2"   fill="#e2e8f0" opacity="0.25"/>
  <circle cx="110" cy="110" r="1.5" fill="#ffffff" opacity="0.30"/>
  <circle cx="190" cy="140" r="2.5" fill="#c7d2fe" opacity="0.28"/>
  <circle cx="260" cy="160" r="1.5" fill="#ffffff" opacity="0.25"/>
  <circle cx="70"  cy="200" r="2"   fill="#e2e8f0" opacity="0.28"/>
  <circle cx="160" cy="220" r="1.5" fill="#ffffff" opacity="0.25"/>
  <circle cx="240" cy="240" r="2.5" fill="#c7d2fe" opacity="0.30"/>
  <circle cx="100" cy="270" r="1.5" fill="#ffffff" opacity="0.25"/>
  <circle cx="290" cy="210" r="2"   fill="#e2e8f0" opacity="0.28"/>
  <circle cx="40"  cy="280" r="2.5" fill="#ffffff" opacity="0.28"/>
  <!-- sparkles -->
  <g transform="translate(200,90)" stroke="#ffffff" stroke-width="1" opacity="0.28">
    <line x1="0" y1="-6" x2="0" y2="6"/><line x1="-6" y1="0" x2="6" y2="0"/>
  </g>
  <g transform="translate(80,160)" stroke="#c7d2fe" stroke-width="1" opacity="0.22">
    <line x1="0" y1="-5" x2="0" y2="5"/><line x1="-5" y1="0" x2="5" y2="0"/>
  </g>
  <!-- crescent moon hint -->
  <path d="M258 20 A18 18 0 1 1 258 56 A12 12 0 1 0 258 20"
        fill="#fde68a" opacity="0.14"/>
</svg>"""),

    "🌿 숲": _uri("""<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300">
  <ellipse cx="60"  cy="80"  rx="24" ry="12" fill="#4ade80" opacity="0.20" transform="rotate(-30 60 80)"/>
  <ellipse cx="58"  cy="78"  rx="8"  ry="20" fill="#86efac" opacity="0.14" transform="rotate(-30 58 78)"/>
  <ellipse cx="220" cy="160" rx="22" ry="11" fill="#22c55e" opacity="0.18" transform="rotate(25 220 160)"/>
  <ellipse cx="218" cy="158" rx="7"  ry="19" fill="#4ade80" opacity="0.12" transform="rotate(25 218 158)"/>
  <ellipse cx="150" cy="55"  rx="18" ry="9"  fill="#86efac" opacity="0.18" transform="rotate(-10 150 55)"/>
  <ellipse cx="260" cy="230" rx="20" ry="10" fill="#4ade80" opacity="0.17" transform="rotate(40 260 230)"/>
  <ellipse cx="80"  cy="240" rx="16" ry="8"  fill="#22c55e" opacity="0.16" transform="rotate(-20 80 240)"/>
  <ellipse cx="180" cy="260" rx="14" ry="7"  fill="#86efac" opacity="0.15" transform="rotate(15 180 260)"/>
  <ellipse cx="40"  cy="160" rx="12" ry="6"  fill="#4ade80" opacity="0.14" transform="rotate(-45 40 160)"/>
  <ellipse cx="270" cy="100" rx="12" ry="6"  fill="#22c55e" opacity="0.14" transform="rotate(35 270 100)"/>
</svg>"""),
}

# ── Season themes ──────────────────────────────────────────────────────────────
THEMES = {
    "🌸 봄": {
        "bg":          "#fff0f5",
        "sidebar":     "#ffe4ef",
        "msg_user":    "#ffd6e7",
        "msg_ai":      "#fff9fb",
        "text":        "#3d0a22",
        "text_msg":    "#3d0a22",
        "border":      "#f9a8c9",
        "input_bg":    "#fff0f5",
        "btn_bg":      "#be185d",
        "btn_text":    "#ffffff",
        "dot":         "#be185d",
        "placeholder": "#a05070",
    },
    "☀️ 여름": {
        "bg":          "#e8f8ff",
        "sidebar":     "#b3ecff",
        "msg_user":    "#7dd3fc",
        "msg_ai":      "#f0faff",
        "text":        "#082535",
        "text_msg":    "#082535",
        "border":      "#38bdf8",
        "input_bg":    "#e8f8ff",
        "btn_bg":      "#0369a1",
        "btn_text":    "#ffffff",
        "dot":         "#0369a1",
        "placeholder": "#2a6a8a",
    },
    "🍂 가을": {
        "bg":          "#fff7ed",
        "sidebar":     "#fde8cc",
        "msg_user":    "#fdba74",
        "msg_ai":      "#fffbf5",
        "text":        "#341007",
        "text_msg":    "#341007",
        "border":      "#fb923c",
        "input_bg":    "#fff7ed",
        "btn_bg":      "#9a3412",
        "btn_text":    "#ffffff",
        "dot":         "#9a3412",
        "placeholder": "#7a4020",
    },
    "❄️ 겨울": {
        "bg":          "#f0f4ff",
        "sidebar":     "#dbe4ff",
        "msg_user":    "#a5b4fc",
        "msg_ai":      "#f8f9ff",
        "text":        "#1a1740",
        "text_msg":    "#1a1740",
        "border":      "#818cf8",
        "input_bg":    "#f0f4ff",
        "btn_bg":      "#4338ca",
        "btn_text":    "#ffffff",
        "dot":         "#4338ca",
        "placeholder": "#4a47a0",
    },
    "🌙 밤": {
        "bg":          "#0f0f1a",
        "sidebar":     "#1a1a2e",
        "msg_user":    "#2d2b55",
        "msg_ai":      "#16213e",
        "text":        "#e2e8f0",
        "text_msg":    "#e2e8f0",
        "border":      "#6d28d9",
        "input_bg":    "#1a1a2e",
        "btn_bg":      "#6d28d9",
        "btn_text":    "#ffffff",
        "dot":         "#a78bfa",
        "placeholder": "#94a3b8",
    },
    "🌿 숲": {
        "bg":          "#f0fdf4",
        "sidebar":     "#dcfce7",
        "msg_user":    "#86efac",
        "msg_ai":      "#f7fef9",
        "text":        "#032b14",
        "text_msg":    "#032b14",
        "border":      "#4ade80",
        "input_bg":    "#f0fdf4",
        "btn_bg":      "#166534",
        "btn_text":    "#ffffff",
        "dot":         "#166534",
        "placeholder": "#2a6645",
    },
}

BASE_CSS = """
<style>
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {{
    background-color: {bg} !important;
    background-image: url("{bg_uri}") !important;
    background-repeat: repeat !important;
    background-size: 300px 300px !important;
    color: {text} !important;
}}
[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] span:not(.typing-indicator span) {{
    color: {text} !important;
}}
[data-testid="stSidebar"] {{
    background-color: {sidebar} !important;
}}
[data-testid="stSidebar"] * {{
    color: #ffffff !important;
}}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
    background-color: {msg_user} !important;
    border: 1px solid {border};
    border-radius: 16px;
}}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) div {{
    color: {text_msg} !important;
}}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {{
    background-color: {msg_ai} !important;
    border: 1px solid {border};
    border-radius: 16px;
}}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) p,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) div {{
    color: {text_msg} !important;
}}
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
.typing-indicator span {{ background: {dot} !important; }}
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
        options=["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
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
st.markdown(
    BASE_CSS.format(**theme, bg_uri=_SVG[theme_name]),
    unsafe_allow_html=True,
)

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
    if "last_audio" not in st.session_state:
        st.session_state.last_audio = None

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ── Voice input ────────────────────────────────────────────────────────────
    col_mic, col_label = st.columns([1, 11])
    with col_mic:
        audio_bytes = audio_recorder(
            text="",
            recording_color=theme["btn_bg"],
            neutral_color=theme["border"],
            icon_size="2x",
            pause_threshold=2.0,
        )
    with col_label:
        st.caption("🎤 마이크 버튼을 눌러 음성 입력")

    voice_prompt = None
    if audio_bytes and audio_bytes != st.session_state.last_audio:
        st.session_state.last_audio = audio_bytes
        with st.spinner("음성 인식 중..."):
            try:
                audio_file = io.BytesIO(audio_bytes)
                audio_file.name = "voice.wav"
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ko",
                )
                voice_prompt = transcript.text.strip()
                if voice_prompt:
                    st.info(f"인식된 텍스트: **{voice_prompt}**", icon="🎤")
            except Exception as e:
                st.error(f"음성 인식 오류: {e}", icon="🚨")

    text_prompt = st.chat_input("What is up?")
    prompt = voice_prompt or text_prompt or None

    if prompt:
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
