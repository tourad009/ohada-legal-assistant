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

# CSS pour un design moderne et conversationnel
st.markdown("""
<style>
    .main-container {
        max-width: 900px;
        margin: auto;
        padding: 20px;
    }
    .stChatMessage {
        margin-bottom: 12px;
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
        max-width: 75%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
        transition: background-color 0.2s;
        display: inline-block;
        text-align: center;
    }
    .suggested-button:hover {
        background-color: #e0e0e0;
    }
    .chat-container {
        max-height: 450px;
        overflow-y: auto;
        margin-bottom: 20px;
        padding: 10px;
        border: 1px solid #eee;
        border-radius: 10px;
        background-color: #fafafa;
    }
    .stChatInput input {
        border-radius: 8px;
        padding: 10px;
    }
    .clear-button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 20px;
        padding: 8px 16px;
        margin-top: 10px;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# Conteneur principal
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # Header
    st.title("OhadAI ⚖️")
    st.subheader("Assistant Juridique OHADA")
    st.markdown("Posez vos questions juridiques et obtenez des réponses précises basées sur les textes OHADA.")

    # Boutons de questions suggérées
    st.markdown("### Questions fréquentes")
    suggested_questions = [
        "Quelle est la procédure pour un arbitrage ?",
        "La SARL est-elle une société de personnes ou de capitaux ?",
        "Quels articles de l'AUSCGIE régissent le contrat commercial ?"
    ]
    cols = st.columns(3)
    for i, question in enumerate(suggested_questions):
        with cols[i]:
            if st.button(question, key=f"sugg_{i}", help="Cliquez pour poser cette question"):
                st.session_state.user_input = question  # Stocke la question pour traitement

    # Conteneur pour le chat avec scroll
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for speaker, message in st.session_state.chat_history:
            role = "user" if speaker == "User" else "assistant"
            with st.chat_message(role, avatar="👤" if role == "user" else "🤖"):
                st.markdown(message)
        st.markdown('</div>', unsafe_allow_html=True)

    # Bouton pour effacer l'historique
    if st.button("Effacer la conversation", key="clear_chat"):
        st.session_state.chat_history = []
        st.rerun()

    # Entrée utilisateur
    user_question = st.chat_input(
        placeholder="Posez votre question juridique... Ex: Quelles sont les étapes pour créer une SARL selon l'OHADA ?"
    ) or st.session_state.get("user_input", "")

    # Traitement de la question
    if user_question and user_question.strip():
        # Ajouter la question à l'historique
        st.session_state.chat_history.append(("User", user_question))
        with chat_container:
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_question)
            with st.chat_message("assistant", avatar="🤖"):
                placeholder = st.empty()
                full_response = ""
                for chunk in generate_answer_stream(user_question, rag_chain):
                    full_response = chunk  # Remplacez, car le générateur envoie le texte cumulé
                    placeholder.markdown(full_response)
                st.session_state.chat_history.append(("Assistant", full_response))

        # Réinitialiser l'entrée utilisateur
        st.session_state.user_input = ""

    # JavaScript pour auto-scroll
    st.markdown("""
    <script>
        const targetNode = window.parent.document.querySelector('section[data-testid="stContainerWithHeight"]');
        if (targetNode) {
            targetNode.scrollTop = targetNode.scrollHeight;
        }
    </script>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)