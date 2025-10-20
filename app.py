import streamlit as st
from rag_pipeline import generate_answer_stream, retriever, rag_chain

# Configuration de la page
st.set_page_config(
    page_title="OHADA Legal Assistant",
    page_icon="⚖️",
    layout="centered"
)

# Initialisation de l'historique
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- CSS pour style moderne ---
st.markdown("""
<style>
/* Style général */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Zone chat */
.chat-message {
    padding: 10px 15px;
    border-radius: 12px;
    margin-bottom: 8px;
    max-width: 80%;
    display: inline-block;
}

/* User */
.chat-user {
    background-color: #E0F7FA;
    text-align: left;
}

/* Bot */
.chat-bot {
    background-color: #FFF9C4;
    text-align: left;
}

/* Icons */
.icon {
    margin-right: 8px;
    font-size: 18px;
}

/* Scroll automatique */
#chat-container {
    max-height: 500px;
    overflow-y: auto;
    padding-right: 10px;
}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div style="text-align: center; margin-bottom: 40px;">
    <h1 style="font-size: 2.5em; margin-bottom: 10px;">OhadAI ⚖️</h1>
    <p style="font-size: 1.2em; color: #666;">Votre assistant juridique spécialisé dans le droit OHADA</p>
    <p style="font-size: 0.9em; color: #888; margin-top: 20px;">
        Posez vos questions juridiques et obtenez des réponses précises basées sur les textes OHADA.
    </p>
</div>
""", unsafe_allow_html=True)

# --- Affichage de l'historique avec scroll ---
chat_container = st.container()
with chat_container:
    st.markdown('<div id="chat-container">', unsafe_allow_html=True)
    for speaker, message in st.session_state.chat_history:
        if speaker == "User":
            st.markdown(f'<div class="chat-message chat-user"><span class="icon">👤</span>{message}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message chat-bot"><span class="icon">🤖</span>{message}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Zone de saisie utilisateur ---
def submit_question():
    question = st.session_state.user_input.strip()
    if question:
        # Ajouter la question à l'historique
        st.session_state.chat_history.append(("User", question))
        st.session_state.user_input = ""  # reset input
        st.experimental_rerun()

st.text_input(
    "Posez votre question juridique...",
    placeholder="Ex: Quelles sont les étapes pour créer une SARL selon l'OHADA ?",
    key="user_input",
    on_change=submit_question
)

# --- Traitement des réponses ---
if st.session_state.chat_history:
    last_speaker, last_message = st.session_state.chat_history[-1]
    if last_speaker == "User":
        placeholder = st.empty()
        full_response = ""
        for chunk in generate_answer_stream(last_message, retriever, rag_chain):
            full_response = chunk
            placeholder.markdown(f'<div class="chat-message chat-bot"><span class="icon">🤖</span>{full_response}</div>', unsafe_allow_html=True)
        st.session_state.chat_history.append(("Assistant", full_response))
        st.experimental_rerun()
