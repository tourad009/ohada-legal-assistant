import streamlit as st
import shelve
from rag_pipeline import generate_answer_stream, rag_chain

st.set_page_config(page_title="OHADA AI", page_icon="⚖️", layout="wide")

# ------------------------
# Style minimal & adaptatif
# ------------------------
st.markdown("""
<style>
.chat-container {
    max-width: 900px;
    margin: auto;
    padding-top: 1rem;
}

.chat-message {
    display: flex;
    gap: 10px;
    margin-bottom: 10px;
}

.msg-bubble {
    padding: 10px 14px;
    border-radius: 12px;
    max-width: 80%;
    font-size: 15px;
}

/* Let Streamlit handle colors based on theme */
.user-msg {
    align-self: flex-end;
    border: 1px solid var(--border-color);
}

.bot-msg {
    border: 1px solid var(--border-color);
}

.chat-avatar {
    font-size: 20px;
    padding-top: 2px;
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
# History
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
# Display chat
# ------------------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    avatar = USER_AVATAR if msg["role"] == "user" else BOT_AVATAR
    bubble_class = "user-msg" if msg["role"] == "user" else "bot-msg"
    
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
# Input + streaming
# ------------------------
user_question = st.chat_input("Pose ta question sur le droit OHADA...")

if user_question:
    st.session_state.messages.append({"role": "user", "content": user_question})
    save_chat_history(st.session_state.messages)

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
