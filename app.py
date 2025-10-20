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

# CSS pour un design moderne : messages alignés, bulles colorées
st.markdown("""
<style>
    .stChatMessage {
        display: flex;
        margin-bottom: 10px;
    }
    .stChatMessage.user {
        flex-direction: row-reverse;
        text-align: right;
    }
    .stChatMessage.assistant {
        flex-direction: row;
        text-align: left;
    }
    .stChatMessage .stMarkdown {
        padding: 12px;
        border-radius: 12px;
        max-width: 70%;
    }
    .stChatMessage.user .stMarkdown {
        background-color: #DCF8C6;
        color: black;
    }
    .stChatMessage.assistant .stMarkdown {
        background-color: #E3F2FD;
        color: black;
    }
    .suggested-button {
        background-color: #f0f0f0;
        border: 1px solid #ddd;
        border-radius: 20px;
        padding: 8px 16px;
        margin: 5px;
        cursor: pointer;
    }
    .suggested-button:hover {
        background-color: #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("OhadAI ⚖️")
st.subheader("Votre assistant juridique spécialisé en droit OHADA")
st.markdown("Posez vos questions juridiques et obtenez des réponses précises basées sur les textes OHADA.")

# Boutons de questions suggérées
suggested_questions = [
    "Quelle est la procédure pour un arbitrage ?",
    "La SARL est-elle une société de personnes ou de capitaux ?",
    "Quels articles de l'AUSCGIE régissent le contrat commercial ?"
]
cols = st.columns(3)
for i, question in enumerate(suggested_questions):
    with cols[i]:
        if st.button(question, key=f"sugg_{i}"):
            user_question = question  # Traiter comme une entrée utilisateur
            # Le traitement se fera dans le bloc if ci-dessous

# Conteneur pour le chat avec scroll (hauteur réduite à 400px)
chat_container = st.container(height=400)

# Affichage de l'historique du chat
with chat_container:
    for speaker, message in st.session_state.chat_history:
        role = "user" if speaker == "User" else "assistant"
        with st.chat_message(role, avatar="👤" if role == "user" else "🤖"):
            st.markdown(message)

# JavaScript pour auto-scroll avec MutationObserver
st.markdown("""
<script>
    const targetNode = window.parent.document.querySelector('section[data-testid="stContainerWithHeight"]');
    if (targetNode) {
        const config = { attributes: true, childList: true, subtree: true };
        const callback = function(mutationsList, observer) {
            targetNode.scrollTop = targetNode.scrollHeight;
        };
        const observer = new MutationObserver(callback);
        observer.observe(targetNode, config);
    }
</script>
""", unsafe_allow_html=True)

# Entrée utilisateur avec st.chat_input
user_question = st.chat_input(
    placeholder="Posez votre question juridique... Ex: Quelles sont les étapes pour créer une SARL selon l'OHADA ?"
)

# Traitement de la question (y compris des suggestions)
if user_question and user_question.strip():
    # Ajouter la question de l'utilisateur à l'historique
    st.session_state.chat_history.append(("User", user_question))
    
    # Afficher le message de l'utilisateur dans le conteneur
    with chat_container:
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_question)
    
    # Générer et afficher la réponse en streaming
    with chat_container:
        with st.chat_message("assistant", avatar="🤖"):
            full_response = st.write_stream(generate_answer_stream(user_question, rag_chain))
    
    # Ajouter la réponse complète à l'historique
    st.session_state.chat_history.append(("Assistant", full_response))