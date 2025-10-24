import streamlit as st
import shelve
from rag_pipeline import generate_answer_stream, rag_chain

st.set_page_config(page_title="OHADA AI", page_icon="⚖️", layout="wide")

st.markdown(
    """
    <style>
    /* Chat container style */
    .chat-container {
        max-width: 900px;
        margin: auto;
    }

    /* Message bubbles */
    .user-msg {
        background-color: #DCF8C6;
        color: #000;
        padding: 10px 15px;
        border-radius: 20px 20px 0 20px;
        display: inline-block;
        margin-bottom: 5px;
        font-size: 16px;
        max-width: 80%;
    }

    .bot-msg {
        background-color: #E8EAF6;
        color: #222;
        padding: 10px 15px;
        border-radius: 20px 20px 20px 0;
        display: inline-block;
        margin-bottom: 5px;
        font-size: 16px;
        max-width: 80%;
    }

    /* Chat message container */
    .chat-message {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        margin-bottom: 5px;
    }

    .chat-message.user {
        justify-content: flex-end;
    }

    .chat-avatar {
        font-size: 24px;
    }

    /* Sidebar customization */
    .sidebar .block-container {
        padding-top: 2rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("## ⚖️ Ohada AI - Assistant Juridique", unsafe_allow_html=True)

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

# ------------------------
# History functions
# ------------------------
def load_chat_history():
    with shelve.open("chat_history") as db:
        return db.get("messages", [])


def save_chat_history(messages):
    with shelve.open("chat_history") as db:
        db["messages"] = messages


if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()


# ------------------------
# Sidebar
# ------------------------
with st.sidebar:
    st.markdown("## ⚙️ Paramètres")
    if st.button("🗑️ Effacer l'historique"):
        st.session_state.messages = []
        save_chat_history([])

# ------------------------
# Chat container
# ------------------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for message in st.session_state.messages:
    role_class = "user" if message["role"] == "user" else "bot"
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    st.markdown(
        f'<div class="chat-message {role_class}"><div class="chat-avatar">{avatar}</div>'
        f'<div class="{role_class}-msg">{message["content"]}</div></div>',
        unsafe_allow_html=True,
    )

# ------------------------
# Chat input
# ------------------------
user_question = st.chat_input("Pose ta question sur l'OHADA...")

if user_question:
    st.session_state.messages.append({"role": "user", "content": user_question})
    save_chat_history(st.session_state.messages)

    # Display user message immediately
    st.markdown(
        f'<div class="chat-message user"><div class="chat-avatar">{USER_AVATAR}</div>'
        f'<div class="user-msg">{user_question}</div></div>',
        unsafe_allow_html=True,
    )

    # Assistant response
    placeholder = st.empty()
    full_response = ""

    for chunk in generate_answer_stream(user_question, rag_chain):
        full_response = chunk
        placeholder.markdown(
            f'<div class="chat-message bot"><div class="chat-avatar">{BOT_AVATAR}</div>'
            f'<div class="bot-msg">{full_response}</div></div>',
            unsafe_allow_html=True,
        )

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    save_chat_history(st.session_state.messages)

st.markdown("</div>", unsafe_allow_html=True)

# ------------------------
# Auto-scroll
# ------------------------
scroll_script = """
<script>
    var chat = parent.document.querySelector('.chat-container');
    if (chat) {
        chat.scrollTop = chat.scrollHeight;
    }
</script>
"""
st.markdown(scroll_script, unsafe_allow_html=True)
