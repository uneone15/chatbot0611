import json
import streamlit as st
from openai import OpenAI

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
    40% { transform: scale(1.1); opacity: 1; }
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

# ── Apply theme CSS ────────────────────────────────────────────────────────────
st.markdown(TYPING_CSS, unsafe_allow_html=True)

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

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            # Typing indicator
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
