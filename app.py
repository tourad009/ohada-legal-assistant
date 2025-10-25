import streamlit as st
import shelve
from rag_pipeline import generate_answer_stream, rag_chain

st.set_page_config(page_title="OHADA AI", page_icon="⚖️", layout="wide")

st.title("⚖️ OHADA AI - Assistant Juridique")

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

# ------------------------
# Chat History Management
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
    st.subheader("Paramètres")
    if st.button("🗑️ Effacer l'historique"):
        st.session_state.messages = []
        save_chat_history([])

# ------------------------
# Display Messages
# ------------------------
for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ------------------------
# Input & Streaming Response
# ------------------------
user_question = st.chat_input("Pose ta question sur l'OHADA...")

if user_question:
    st.session_state.messages.append({"role": "user", "content": user_question})
    save_chat_history(st.session_state.messages)

    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(user_question)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        placeholder = st.empty()
        partial_response = ""

        for chunk in generate_answer_stream(user_question, rag_chain):
            partial_response = chunk
            placeholder.markdown(partial_response)

        final_response = partial_response

    st.session_state.messages.append({"role": "assistant", "content": final_response})
    save_chat_history(st.session_state.messages)

# ------------------------
# Auto-scroll to bottom
# ------------------------
scroll_script = """
<script>
    var chat = parent.document.querySelector('.stChatMessage:last-of-type');
    if (chat) {
        chat.scrollIntoView({behavior: 'smooth', block: 'end'});
    }
</script>
"""
st.markdown(scroll_script, unsafe_allow_html=True)
