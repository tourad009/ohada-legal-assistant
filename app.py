import streamlit as st
from rag_pipeline import generate_answer_stream, rag_chain

# Configuration de la page
st.set_page_config(
    page_title="OHADA Legal Assistant",
    page_icon="⚖️",
    layout="centered"
)

# Initialisation de l'historique
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# CSS pour un style moderne et épuré
st.markdown("""
<style>
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.chat-message {
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 10px;
    max-width: 80%;
}
.chat-user {
    background-color: #E0F7FA;
}
.chat-bot {
    background-color: #F5F5F5;
}
.icon {
    margin-right: 8px;
}
.chat-container {
    max-height: 500px;
    overflow-y: auto;
    margin-bottom: 20px;
}
.stTextInput input {
    border-radius: 8px;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h1 style="font-size: 2.2em;">OhadAI ⚖️</h1>
    <p style="color: #666;">Votre assistant juridique spécialisé en droit OHADA</p>
</div>
""", unsafe_allow_html=True)

# Affichage de l'historique avec scroll
with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for message in st.session_state.chat_history:
        role, content = message["role"], message["content"]
        icon = "👤" if role == "user" else "🤖"
        style = "chat-user" if role == "user" else "chat-bot"
        st.markdown(f'<div class="chat-message {style}"><span class="icon">{icon}</span>{content}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Entrée utilisateur
user_input = st.text_input(
    "Posez votre question juridique...",
    placeholder="Ex: Quelles sont les étapes pour créer une SARL selon l'OHADA ?",
    key="user_input"
)

# Traitement de la question
if user_input and user_input.strip():
    # Ajouter la question à l'historique
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("assistant"):
        response = ""
        for chunk in generate_answer_stream(user_input, rag_chain):
            response += chunk
            st.markdown(f'<div class="chat-message chat-bot"><span class="icon">🤖</span>{response}</div>', unsafe_allow_html=True)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    # Reset input et rafraîchir
    st.session_state.user_input = ""
    st.rerun()