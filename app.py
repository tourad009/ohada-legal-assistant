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
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False  # Mode clair par défaut pour sobriété

# -----------------------------------------
# CSS : DESIGN SOBRE ET MODERNE
# -----------------------------------------
dark_mode_css = """
<style>
/* Mode clair (sobriété par défaut) */
:root {
    --bg-color: #f8f9fa;
    --text-color: #212529;
    --accent-color: #495057;
    --bubble-user: #e9ecef;
    --bubble-assistant: #ffffff;
    --border-color: #dee2e6;
}

/* Mode sombre (moderne et optionnel) */
[data-theme="dark"] {
    --bg-color: #212529;
    --text-color: #f8f9fa;
    --accent-color: #ced4da;
    --bubble-user: #343a40;
    --bubble-assistant: #495057;
    --border-color: #6c757d;
}

/* Global */
html, body, [data-testid="stAppViewContainer"] {
    height: 100%;
    overflow: hidden !important;
    background-color: var(--bg-color) !important;
    color: var(--text-color) !important;
    font-family: "Inter", sans-serif !important;
}

/* Container principal */
.main-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    max-width: 900px;
    margin: auto;
    padding: 1rem;
}

/* Header */
.header {
    text-align: center;
    padding: 1rem 0;
}
.header h1 {
    font-size: 1.8rem;
    color: var(--text-color);
    margin: 0;
}
.header p {
    color: var(--accent-color);
    font-size: 0.95rem;
    margin-top: 0.25rem;
}

/* Toggle dark mode (moderne, discret) */
.dark-toggle {
    position: absolute;
    top: 1rem;
    right: 1rem;
    font-size: 0.85rem;
}

/* Zone du chat */
.chat-container {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    border-radius: 12px;
    background: var(--bg-color);
    border: 1px solid var(--border-color);
    scrollbar-width: thin;
    scrollbar-color: var(--accent-color) transparent;
}

/* Messages */
.stChatMessage {
    margin-bottom: 1rem !important;
    display: flex !important;
}
.stChatMessage.user {
    justify-content: flex-end;
}
.stChatMessage.assistant {
    justify-content: flex-start;
}
.stChatMessage .stMarkdown {
    border-radius: 12px;
    padding: 0.75rem 1rem;
    max-width: 80%;
    line-height: 1.4;
    animation: fadeIn 0.3s ease-out;
    border: 1px solid var(--border-color);
}
.stChatMessage.user .stMarkdown {
    background-color: var(--bubble-user);
    color: var(--text-color);
}
.stChatMessage.assistant .stMarkdown {
    background-color: var(--bubble-assistant);
    color: var(--text-color);
}

/* Suggestions */
.suggestions {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    margin: 0.5rem 0;
}
.suggested-button {
    background-color: transparent;
    border: 1px solid var(--border-color);
    border-radius: 20px;
    padding: 0.5rem 1rem;
    margin: 0.25rem;
    cursor: pointer;
    font-size: 0.9rem;
    color: var(--accent-color);
    transition: background-color 0.2s ease;
}
.suggested-button:hover {
    background-color: var(--border-color);
}

/* Input fixée */
.input-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--bg-color);
    border-top: 1px solid var(--border-color);
    padding: 0.75rem 0;
}
.input-container {
    max-width: 900px;
    margin: auto;
    padding: 0 1rem;
    display: flex;
    align-items: center;
}

/* Effets */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Supprime le footer Streamlit */
footer {visibility: hidden !important;}
</style>
"""
st.markdown(dark_mode_css, unsafe_allow_html=True)

# Appliquer le thème
if st.session_state.dark_mode:
    st.markdown('<body data-theme="dark">', unsafe_allow_html=True)
else:
    st.markdown('<body data-theme="light">', unsafe_allow_html=True)

# -----------------------------------------
# LAYOUT PRINCIPAL
# -----------------------------------------
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Toggle dark mode (moderne et discret)
with st.container():
    if st.button("🌙 Mode sombre" if not st.session_state.dark_mode else "☀️ Mode clair", key="toggle_theme", help="Changer le thème"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# En-tête minimal
st.markdown("""
<div class="header">
    <h1>⚖️ OhadAI</h1>
    <p>Assistant juridique OHADA</p>
</div>
""", unsafe_allow_html=True)

# Suggestions rapides (minimalistes)
st.markdown('<div class="suggestions">', unsafe_allow_html=True)
for q in [
    "Procédure d'arbitrage ?",
    "SARL : société de personnes ou capitaux ?",
    "Articles AUSCGIE sur contrat commercial ?"
]:
    if st.button(q, key=q, help="Poser cette question"):
        st.session_state.user_input = q
st.markdown('</div>', unsafe_allow_html=True)

# Zone de chat
st.markdown('<div class="chat-container" id="chatBox">', unsafe_allow_html=True)
for speaker, message in st.session_state.chat_history:
    role = "user" if speaker == "User" else "assistant"
    with st.chat_message(role):
        st.markdown(message)
st.markdown('</div>', unsafe_allow_html=True)

# Barre d'input fixée avec bouton effacer intégré
st.markdown('<div class="input-bar"><div class="input-container">', unsafe_allow_html=True)
col1, col2 = st.columns([8, 2])
with col1:
    user_question = st.chat_input(placeholder="Posez votre question...") or st.session_state.get("user_input", "")
with col2:
    if st.button("🗑️ Effacer", key="clear_chat"):
        st.session_state.chat_history = []
        st.rerun()
st.markdown('</div></div>', unsafe_allow_html=True)

# Traitement du message
if user_question and user_question.strip():
    st.session_state.chat_history.append(("User", user_question))
    with st.chat_message("user"):
        st.markdown(user_question)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        for chunk in generate_answer_stream(user_question, rag_chain):
            full_response = chunk
            placeholder.markdown(full_response)
        st.session_state.chat_history.append(("Assistant", full_response))

    st.session_state.user_input = ""

# Scroll automatique
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