import streamlit as st
from rag_pipeline import generate_answer_stream, rag_chain

# ----------------------------
# CONFIGURATION DE LA PAGE
# ----------------------------
st.set_page_config(
    page_title="OhadAI ⚖️",
    page_icon="⚖️",
    layout="wide"
)

# ----------------------------
# INITIALISATION
# ----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ----------------------------
# STYLES CSS MODERNES
# ----------------------------
st.markdown("""
<style>
    /* Supprime le scroll global de Streamlit */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {
        height: 100%;
        overflow: hidden !important;
    }

    /* Structure principale */
    .main-container {
        display: flex;
        flex-direction: column;
        height: 100vh;
        max-width: 800px;
        margin: auto;
        padding: 0 1rem;
    }

    /* Zone de chat */
    .chat-container {
        flex: 1;
        overflow-y: auto;
        overflow-x: hidden;
        padding: 1rem 0;
        margin-bottom: 70px; /* pour ne pas cacher les messages derrière l'input */
        scrollbar-width: thin;
        scrollbar-color: #ccc transparent;
    }

    /* Messages */
    .stChatMessage {
        margin-bottom: 10px !important;
        display: flex !important;
    }

    .stChatMessage.user {
        justify-content: flex-end;
    }

    .stChatMessage.assistant {
        justify-content: flex-start;
    }

    .stChatMessage .stMarkdown {
        border-radius: 16px;
        padding: 12px 16px;
        max-width: 75%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        font-size: 0.95rem;
        line-height: 1.4;
    }

    .stChatMessage.user .stMarkdown {
        background-color: #DCF8C6;
        color: #000;
    }

    .stChatMessage.assistant .stMarkdown {
        background-color: #F1F0F0;
        color: #111;
    }

    /* Barre d'input fixée en bas */
    .input-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #fff;
        border-top: 1px solid #ddd;
        padding: 10px 0;
        box-shadow: 0 -1px 4px rgba(0,0,0,0.05);
    }

    .input-container {
        max-width: 800px;
        margin: auto;
        padding: 0 1rem;
    }

    /* Boutons suggérés */
    .suggested-button {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 20px;
        padding: 8px 16px;
        margin: 5px;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.2s ease-in-out;
    }
    .suggested-button:hover {
        background-color: #ececec;
    }

    /* Bouton de reset */
    .clear-button {
        background-color: #ff4b4b;
        color: white;
        border: none;
        border-radius: 20px;
        padding: 8px 16px;
        margin-top: 5px;
        cursor: pointer;
        font-size: 0.9rem;
    }

</style>
""", unsafe_allow_html=True)

# ----------------------------
# CONTENU PRINCIPAL
# ----------------------------
st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.title("⚖️ OhadAI – Assistant Juridique OHADA")
st.markdown("Posez vos questions juridiques et obtenez des réponses basées sur les textes de l’OHADA.")

# Boutons de questions suggérées
st.markdown("#### Questions fréquentes :")
suggested_questions = [
    "Quelle est la procédure pour un arbitrage ?",
    "La SARL est-elle une société de personnes ou de capitaux ?",
    "Quels articles de l'AUSCGIE régissent le contrat commercial ?"
]
cols = st.columns(3)
for i, question in enumerate(suggested_questions):
    with cols[i]:
        if st.button(question, key=f"sugg_{i}"):
            st.session_state.user_input = question

# Zone de chat avec scroll uniquement ici
st.markdown('<div class="chat-container" id="chat-container">', unsafe_allow_html=True)
for speaker, message in st.session_state.chat_history:
    role = "user" if speaker == "User" else "assistant"
    with st.chat_message(role, avatar="👤" if role == "user" else "🤖"):
        st.markdown(message)
st.markdown('</div>', unsafe_allow_html=True)

# Bouton clear
if st.button("🗑️ Effacer la conversation", key="clear_chat", use_container_width=True):
    st.session_state.chat_history = []
    st.rerun()

# ----------------------------
# BARRE D'INPUT FIXE
# ----------------------------
st.markdown('<div class="input-bar"><div class="input-container">', unsafe_allow_html=True)
user_question = st.chat_input(
    placeholder="Posez votre question juridique ici..."
) or st.session_state.get("user_input", "")
st.markdown('</div></div>', unsafe_allow_html=True)

# ----------------------------
# TRAITEMENT DU MESSAGE
# ----------------------------
if user_question and user_question.strip():
    st.session_state.chat_history.append(("User", user_question))
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_question)
    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full_response = ""
        for chunk in generate_answer_stream(user_question, rag_chain):
            full_response = chunk
            placeholder.markdown(full_response)
        st.session_state.chat_history.append(("Assistant", full_response))

    st.session_state.user_input = ""

# ----------------------------
# SCROLL AUTOMATIQUE (dans la zone chat uniquement)
# ----------------------------
st.markdown("""
<script>
const chatBox = window.parent.document.getElementById('chat-container');
if (chatBox) {
    chatBox.scrollTop = chatBox.scrollHeight;
}
</script>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
