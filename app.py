import streamlit as st
import shelve
from rag_pipeline import generate_answer_stream, rag_chain

st.set_page_config(page_title="OHADA AI", page_icon="⚖️", layout="wide")

# ------------------------
# Style Global (sobre & pro)
# ------------------------
st.markdown("""
<style>

body {
    background-color: #fafafa;
    font-family: "Inter", sans-serif;
}

/* Chat Container */
.chat-container {
    max-width: 900px;
    margin: auto;
    padding-top: 1rem;
}

/* Message Blocks */
.chat-message {
    display: flex;
    gap: 12px;
    margin-bottom: 12px;
    line-height: 1.5;
}

/* Avatars */
.chat-avatar {
    font-size: 22px;
    padding-top: 4px;
}

/* Bubble Style */
.msg-bubble {
    padding: 12px 16px;
    border-radius: 10px;
    max-width: 80%;
    font-size: 16px;
}

/* User Message Bubble */
.user-msg {
    background-color: #ffffff;
    border: 1px solid #dcdcdc;
    margin-left: auto;
}

/* Assistant Message Bubble */
.bot-msg {
    background-color: #F1F3F8;
    border: 1px solid #E0E3E9;
}

/* Sidebar spacing */
.sidebar .block-container {
    margin-top: 2rem;
}

</style>
""", unsafe_allow_html=True)

# ------------------------
# Title
# ------------------------
st.markdown("<h2 style='text-align:center;'>⚖️ OHADA AI — Assistant Juridique</h2>", unsafe_allow_html=True)

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"


# ------------------------
# History (Shelve)
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
    st.subheader("⚙️ Paramètres")
    if st.button("🗑️ Effacer l'historique"):
        st.session_state.messages = []
        save_chat_history([])

# ------------------------
# Display Chat
# ------------------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    role = msg["role"]
    avatar = USER_AVATAR if role == "user" else BOT_AVATAR
    bubble_class = "user-msg" if role == "user" else "bot-msg"

    st.markdown(
        f"""
        <div class="chat-message">
            <div class="chat-avatar">{avatar}</div>
            <div class="msg-bubble {bubble_class}">{msg["content"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ------------------------
# Input
# ------------------------
user_question = st.chat_input("Pose ta question sur le droit OHADA...")

if user_question:
    st.session_state.messages.append({"role": "user", "content": user_question})
    save_chat_history(st.session_state.messages)

    # Streaming response
    placeholder = st.empty()
    full_response = ""

    for chunk in generate_answer_stream(user_question, rag_chain):
        full_response = chunk
        placeholder.markdown(
            f"""
            <div class="chat-message">
                <div class="chat-avatar">{BOT_AVATAR}</div>
                <div class="msg-bubble bot-msg">{full_response}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    save_chat_history(st.session_state.messages)

st.markdown("</div>", unsafe_allow_html=True)

# Auto-scroll
st.markdown("""
<script>
var chat = parent.document.querySelector('.chat-container');
if(chat){ chat.scrollTop = chat.scrollHeight; }
</script>
""", unsafe_allow_html=True)
