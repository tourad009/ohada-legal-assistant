import streamlit as st
from streamlit.components.v1 import html

# ---------------------------------------
# CONFIGURATION DE BASE
# ---------------------------------------
st.set_page_config(page_title="Assistant OHADA", page_icon="⚖️", layout="wide")

# CSS inspiré de ChatGPT
st.markdown("""
<style>
/* Conteneur global */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1rem 0;
}

/* Bulle de message */
.message {
    padding: 1rem;
    border-radius: 1rem;
    max-width: 85%;
    word-wrap: break-word;
    font-size: 1rem;
    line-height: 1.5;
}

/* Message utilisateur */
.user-message {
    align-self: flex-end;
    background-color: #007bff20;
    border: 1px solid #007bff40;
}

/* Message bot */
.bot-message {
    align-self: flex-start;
    background-color: #f5f5f5;
    border: 1px solid #e0e0e0;
}

/* Effet machine à écrire */
@keyframes blink {
  0% { opacity: 0; }
  50% { opacity: 1; }
  100% { opacity: 0; }
}
.cursor {
  display: inline-block;
  width: 8px;
  background-color: #888;
  margin-left: 3px;
  animation: blink 1s infinite;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------
# ÉTAT DE SESSION
# ---------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------
# AFFICHAGE DES MESSAGES
# ---------------------------------------
def render_messages():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        role_class = "user-message" if msg["role"] == "user" else "bot-message"
        st.markdown(f'<div class="message {role_class}">{msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------
# SOUMISSION DE LA QUESTION
# ---------------------------------------
def handle_query(question):
    st.session_state.messages.append({"role": "user", "content": question})
    render_messages()
    st.markdown('<div class="message bot-message">', unsafe_allow_html=True)
    placeholder = st.empty()
    streamed_text = ""

    # ⚙️ STREAMING DE LA RÉPONSE
    for partial in generate_answer_stream(question, rag_chain):
        streamed_text = partial
        placeholder.markdown(streamed_text + '<span class="cursor"></span>', unsafe_allow_html=True)
        # Défilement automatique vers le bas
        html("<script>window.scrollTo(0, document.body.scrollHeight);</script>")

    st.markdown('</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "bot", "content": streamed_text})

# ---------------------------------------
# AFFICHAGE PRINCIPAL
# ---------------------------------------
st.title("⚖️ Assistant juridique OHADA")

render_messages()

# Zone d'entrée utilisateur (préserve ton style actuel)
question = st.chat_input("Posez votre question juridique ici...")

if question:
    handle_query(question)
