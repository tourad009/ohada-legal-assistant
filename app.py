import streamlit as st
from rag_pipeline import generate_answer_stream, rag_chain

# Configuration de la page
st.set_page_config(page_title="OHADA Legal Assistant", layout="wide")

# Initialisation de l'historique du chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Style CSS personnalisé
st.markdown("""
    <style>
    .main-container {
        max-width: 800px;
        margin: auto;
        padding: 20px;
    }
    .title {
        text-align: center;
        color: #2c3e50;
        font-size: 2.5em;
        margin-bottom: 20px;
    }
    .suggested-button {
        background-color: #3498db;
        color: white;
        border-radius: 20px;
        padding: 8px 16px;
        margin: 5px;
        font-size: 0.9em;
        transition: background-color 0.3s;
    }
    .suggested-button:hover {
        background-color: #2980b9;
    }
    .chat-input-container {
        position: fixed;
        bottom: 20px;
        width: 800px;
        background: white;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
    }
    .stChatMessage {
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    .stChatMessage.user {
        background-color: #e6f3ff;
    }
    .stChatMessage.assistant {
        background-color: #f0f0f0;
    }
    </style>
""", unsafe_allow_html=True)

# Conteneur principal
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="title">Assistant Juridique OHADA</h1>', unsafe_allow_html=True)

    # Questions suggérées
    st.markdown("### Questions fréquentes")
    suggested_questions = [
        "Quelle est la procédure pour un arbitrage ?",
        "La SARL est-elle une société de personnes ou de capitaux ?",
        "Quels articles de l'AUSCGIE régissent le contrat commercial ?"
    ]
    cols = st.columns(3)
    for i, question in enumerate(suggested_questions):
        with cols[i]:
            if st.button(question, key=f"suggested_{i}", help="Cliquez pour poser cette question"):
                st.session_state.chat_history.append({"role": "user", "content": question})
                with st.chat_message("user"):
                    st.markdown(question)
                with st.chat_message("assistant"):
                    response = ""
                    for chunk in generate_answer_stream(question, rag_chain):
                        response += chunk
                        st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})

    # Affichage de l'historique du chat
    st.markdown("### Conversation")
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrée utilisateur
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    user_question = st.chat_input("Posez votre question juridique ici...")
    if user_question and user_question.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)
        with st.chat_message("assistant"):
            response = ""
            for chunk in generate_answer_stream(user_question, rag_chain):
                response += chunk
                st.markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)