import streamlit as st
from rag_pipeline import generate_answer_stream, rag_chain

# -----------------------------------------
# CONFIGURATION DE LA PAGE
# -----------------------------------------
st.set_page_config(
    page_title="OhadAI ⚖️",
    page_icon="⚖️",
    layout="wide"
)

# -----------------------------------------
# INITIALISATION
# -----------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -----------------------------------------
# CSS : DESIGN PREMIUM ET FLUIDE
# -----------------------------------------
st.markdown("""
<style>
/* Supprime le scroll global */
html, body, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {
    height: 100%;
    overflow: hidden !important;
    background-color: #f7f9fc !important;
    font-family: "Inter", sans-serif !important;
}

/* Container principal */
.main-container {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100vh;
    max-width: 850px;
    margin: auto;
    padding: 1rem 1.5rem;
}

/* Header */
.header {
    text-align: center;
    padding-bottom: 0.5rem;
}
.header h1 {
    font-size: 2rem;
    color: #1f2937;
    margin-bottom: 0.3rem;
}
.header p {
    color: #4b5563;
    font-size: 1rem;
}

/* Zone du chat */
.chat-container {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 16px;
    background: #ffffff;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    scrollbar-width: thin;
    scrollbar-color: #cbd5e1 transparent;
}

/* Messages */
.stChatMessage {
    margin-bottom: 14px !important;
    display: flex !important;
}
.stChatMessage.user {
    justify-content: flex-end;
}
.stChatMessage.assistant {
    justify-content: flex-start;
}
.stChatMessage .stMarkdown {
    border-radius: 18px;
    padding: 12px 16px;
    max-width: 75%;
    line-height: 1.5;
    animation: fadeIn 0.25s ease-in-out;
}
.stChatMessage.user .stMarkdown {
    background-color: #d1fae5;
    color: #064e3b;
}
.stChatMessage.assistant .stMarkdown {
    background-color: #e0f2fe;
    color: #0c4a6e;
}

/* Input fixée */
.input-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #ffffffcc;
    backdrop-filter: blur(8px);
    border-top: 1px solid #e5e7eb;
    padding: 12px 0;
    box-shadow: 0 -2px 6px rgba(0,0,0,0.04);
}
.input-container {
    max-width: 850px;
    margin: auto;
    padding: 0 1.5rem;
}

/* Boutons suggérés */
.suggestions {
    text-align: center;
    margin-top: 0.5rem;
}
.suggested-button {
    display: inline-block;
    background-color: #f3f4f6;
    border: 1px solid #e5e7eb;
    border-radius: 20px;
    padding: 8px 16px;
    margin: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    color: #374151;
    transition: all 0.2s ease-in-out;
}
.suggested-button:hover {
    background-color: #e5e7eb;
    transform: translateY(-1px);
}

/* Effets */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(5px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Supprime le footer Streamlit */
footer {visibility: hidden !important;}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------
# LAYOUT PRINCIPAL
# -----------------------------------------
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# En-tête
st.markdown("""
<div class="header">
    <h1>⚖️ OhadAI</h1>
    <p>Votre assistant juridique intelligent basé sur le droit OHADA</p>
</div>
""", unsafe_allow_html=True)

# Suggestions rapides
st.markdown('<div class="suggestions">', unsafe_allow_html=True)
for q in [
    "Quelle est la procédure pour un arbitrage ?",
    "La SARL est-elle une société de personnes ou de capitaux ?",
    "Quels articles de l'AUSCGIE régissent le contrat commercial ?"
]:
    if st.button(q, key=q, help="Cliquez pour poser cette question"):
        st.session_state.user_input = q
st.markdown('</div>', unsafe_allow_html=True)

# Zone de chat
st.markdown('<div class="chat-container" id="chatBox">', unsafe_allow_html=True)
for speaker, message in st.session_state.chat_history:
    role = "user" if speaker == "User" else "assistant"
    with st.chat_message(role, avatar="👤" if role == "user" else "🤖"):
        st.markdown(message)
st.markdown('</div>', unsafe_allow_html=True)

# Effacer la conversation
if st.button("🗑️ Effacer la conversation", key="clear_chat", use_container_width=True):
    st.session_state.chat_history = []
    st.rerun()

# Barre d'input fixée
st.markdown('<div class="input-bar"><div class="input-container">', unsafe_allow_html=True)
user_question = st.chat_input(
    placeholder="Posez votre question ici..."
) or st.session_state.get("user_input", "")
st.markdown('</div></div>', unsafe_allow_html=True)

# Traitement du message
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

# Scroll automatique fluide
st.markdown("""
<script>
const chatBox = window.parent.document.getElementById('chatBox');
if (chatBox) {
    chatBox.scrollTo({
        top: chatBox.scrollHeight,
        behavior: 'smooth'
    });
}
</script>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
