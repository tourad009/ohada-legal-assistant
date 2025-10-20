# app.py
import streamlit as st
from rag_pipeline import generate_answer_stream, rag_chain

# Configuration de la page
st.set_page_config(
    page_title="OHADA Legal Assistant",
    page_icon="⚖️",
    layout="wide"
)

# Initialisation de l'historique du chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# CSS pour styliser les messages de chat
st.markdown("""
<style>
    div.stMarkdown > div {
        padding: 10px;
        border-radius: 10px;
    }
    .stChatMessage.user div {
        background-color: #DCF8C6;
    }
    .stChatMessage.assistant div {
        background-color: #E3F2FD;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("OhadAI ⚖️")
st.subheader("Votre assistant juridique spécialisé en droit OHADA")
st.markdown("Posez vos questions juridiques et obtenez des réponses précises basées sur les textes OHADA.")

# Affichage de l'historique du chat
chat_container = st.container(height=500)
with chat_container:
    for speaker, message in st.session_state.chat_history:
        role = "user" if speaker == "User" else "assistant"
        with st.chat_message(role, avatar="👤" if role == "user" else "🤖"):
            st.markdown(message)

# Entrée utilisateur avec st.chat_input
user_question = st.chat_input(
    placeholder="Posez votre question juridique... Ex: Quelles sont les étapes pour créer une SARL selon l'OHADA ?"
)

# Traitement de la question
if user_question and user_question.strip():
    # Ajouter la question de l'utilisateur à l'historique
    st.session_state.chat_history.append(("User", user_question))
    
    # Afficher le message de l'utilisateur
    with chat_container:
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_question)
    
    # Générer et afficher la réponse en streaming
    with chat_container:
        with st.chat_message("assistant", avatar="🤖"):
            message_placeholder = st.empty()
            full_response = ""
            for chunk in generate_answer_stream(user_question, rag_chain):
                full_response += chunk
                message_placeholder.markdown(full_response)
    
    # Ajouter la réponse complète à l'historique
    st.session_state.chat_history.append(("Assistant", full_response))