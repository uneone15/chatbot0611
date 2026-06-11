import json
import streamlit as st
from openai import OpenAI
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

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
.sticker {
    font-size: 72px;
    line-height: 1.1;
    display: inline-block;
    padding: 6px;
    filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.15));
}
</style>
"""

TYPING_HTML = """
<div class="typing-indicator">
    <span></span><span></span><span></span>
</div>
"""

STICKER_CATEGORIES = {
    "동물 🐾": ["🐶","🐱","🐭","🐹","🐰","🦊","🐻","🐼","🐨","🐯","🦁","🐸","🐙","🦋","🐧","🦆"],
    "표정 😊": ["🥰","😘","🤩","😜","🤪","😴","🥺","😭","🤗","😇","🥳","😤","🫶","🤭","😋","🤓"],
    "음식 🍰": ["🍕","🍔","🍩","🍪","🎂","🍰","🧁","🍓","🍑","🍒","🍦","🧃","🧋","🍜","🥐","🍡"],
    "기타 ✨": ["🌈","⭐","🌸","🌺","🎀","💝","🎈","🎁","✨","💫","🌙","☀️","🍀","🦄","💎","🫧"],
}

STICKER_PREFIX = "__sticker__"


def render_message(message: dict):
    content = message["content"]
    if content.startswith(STICKER_PREFIX):
        sticker = content[len(STICKER_PREFIX):]
        st.markdown(f'<span class="sticker">{sticker}</span>', unsafe_allow_html=True)
    else:
        st.markdown(content)


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

# ── Apply CSS ──────────────────────────────────────────────────────────────────
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
            render_message(message)

    # ── Map ────────────────────────────────────────────────────────────────────
    with st.expander("🗺️ 지도 검색", expanded=False):
        location_query = st.text_input("장소를 입력하세요", placeholder="예: 경복궁, 도쿄 타워, Eiffel Tower", key="map_query")
        search_clicked = st.button("검색", key="map_search")

        if "map_location" not in st.session_state:
            st.session_state.map_location = {"lat": 37.5665, "lon": 126.9780, "name": "서울"}

        if search_clicked and location_query:
            try:
                geolocator = Nominatim(user_agent="streamlit-chatbot")
                geo = geolocator.geocode(location_query, timeout=10)
                if geo:
                    st.session_state.map_location = {
                        "lat": geo.latitude,
                        "lon": geo.longitude,
                        "name": geo.address,
                    }
                else:
                    st.warning("장소를 찾을 수 없습니다. 다른 키워드로 시도해보세요.")
            except GeocoderTimedOut:
                st.error("검색 시간이 초과됐습니다. 다시 시도해주세요.")

        loc = st.session_state.map_location
        m = folium.Map(location=[loc["lat"], loc["lon"]], zoom_start=14)
        folium.Marker(
            location=[loc["lat"], loc["lon"]],
            popup=folium.Popup(loc["name"], max_width=250),
            tooltip=loc["name"],
            icon=folium.Icon(color="red", icon="heart", prefix="fa"),
        ).add_to(m)
        st_folium(m, width="100%", height=400, returned_objects=[])

    # ── Sticker picker ─────────────────────────────────────────────────────────
    with st.expander("🎀 스티커", expanded=False):
        tab_names = list(STICKER_CATEGORIES.keys())
        tabs = st.tabs(tab_names)
        for tab, category in zip(tabs, tab_names):
            with tab:
                stickers = STICKER_CATEGORIES[category]
                cols = st.columns(8)
                for i, sticker in enumerate(stickers):
                    if cols[i % 8].button(sticker, key=f"sticker_{category}_{i}"):
                        st.session_state["pending_sticker"] = sticker

    # ── Chat input ─────────────────────────────────────────────────────────────
    pending_sticker = st.session_state.pop("pending_sticker", None)

    if pending_sticker:
        content = STICKER_PREFIX + pending_sticker
        st.session_state.messages.append({"role": "user", "content": content})
        with st.chat_message("user"):
            st.markdown(f'<span class="sticker">{pending_sticker}</span>', unsafe_allow_html=True)
        st.rerun()

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            api_messages = [
                {"role": m["role"], "content": m["content"].replace(STICKER_PREFIX, "[스티커] ")}
                for m in st.session_state.messages
            ]

            with st.chat_message("assistant"):
                typing_placeholder = st.empty()
                typing_placeholder.markdown(TYPING_HTML, unsafe_allow_html=True)

                stream = client.chat.completions.create(
                    model=model,
                    messages=api_messages,
                    temperature=temperature,
                    stream=True,
                )

                typing_placeholder.empty()
                response = st.write_stream(stream)

            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"Error: {e}", icon="🚨")
