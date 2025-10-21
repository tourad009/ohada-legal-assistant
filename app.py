import streamlit as st
from rag_pipeline import generate_answer_stream, rag_chain

# -----------------------------
# CONFIGURATION
# -----------------------------
st.set_page_config(page_title="OhadAI ⚖️", page_icon="⚖️", layout="wide")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# -----------------------------
# CSS ÉPURÉ ET MODERNE
# -----------------------------
st.markdown("""
<style>
/* Reset Streamlit layout */
html, body, [data-testid="stAppViewContainer"] {
    height: 100%;
    overflow: hidden !important;
    background-color: var(--bg);
}

/* Thème clair et sombre */
:root {
    --bg: #f8f9fa;
    --text: #1e1e1e;
    --border: #dee2e6;
    --user-bubble: #e9ecef;
    --assistant-bubble: #ffffff;
}
[data-theme="dark"] {
    --bg: #1e1e1e;
    --text: #f1f1f1;
    --border: #333;
    --user-bubble: #2a2a2a;
    --assistant-bubble: #3a3a3a;
}

/* Container principal */
.main {
    display: flex;
    flex-direction: column;
    height: 100vh;
    max-width: 900px;
    margin: auto;
    padding: 0;
}

/* Header */
.header {
    text-align: center;
    padding: 0.8rem 1rem;
    margin-bottom: 0.5rem;
}
.header h1 {
    font-size: 1.6rem;
    margin: 0;
    color: var(--text);
}
.header p {
    color: #6c757d;
    font-size: 0.9rem;
    margin: 0.25rem 0 0 0;
}

/* Zone de chat */
.chat {
    flex: 1;
    overflow-y: auto;
    padding: 1rem 0.75rem;
    border-radius: 12px;
    border: 1px solid var(--border);
    background-color: var(--bg);
    scroll-behavior: smooth;
}
.chat::-webkit-scrollbar {
    width: 6px;
}
.chat::-webkit-scrollbar-thumb {
    background: #bbb;
    border-radius: 4px;
}

/* Messages */
.stChatMessage {
    margin-bottom: 0.75rem !important;
}
.stChatMessage .stMarkdown {
    border-radius: 12px;
    padding: 0.75rem 1rem;
    line-height: 1.4;
    max-width: 75%;
    border: 1px solid var(--border);
    background: var(--assistant-bubble);
    color: var(--text);
    animation: fadeIn 0.25s ease-out;
}
.stChatMessage.user .stMarkdown {
    background: var(--user-bubble);
    margin-left: auto;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(5px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Suggestions */
.suggestions {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}
.suggestions button {
    background: transparent;
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 0.4rem 1rem;
    font-size: 0.85rem;
    cursor: pointer;
    color: var(--text);
    transition: all 0.2s ease;
}
.suggestions button:hover {
    background: var(--border);
}

/* Input fixée */
.input-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--bg);
    border-top: 1px solid var(--border);
    padding: 0.6rem 0.5rem;
}
.input-inner {
    max-width: 900px;
    margin: auto;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Bouton clear */
button[data-testid="clear_button"] {
    background: #dc3545;
    color: white;
    border: none;
    border-radius: 20px;
    padding: 0.4rem 0.8rem;
}
button[data-testid="clear_button"]:hover {
    background: #c82333;
}

/* Supprime le footer Streamlit */
footer {visibility: hidden !important;}
</style>
""", unsafe_allow_html=True)

# Appliquer thème
st.markdown(f'<body data-theme={"dark" if st.session_state.dark_mode else "light"}>', unsafe_allow_html=True)

# -----------------------------
# HEADER & TOGGLE MODE
# -----------------------------
col1, col2 = st.columns([8, 1])
with col1:
    st.markdown('<div class="header"><h1>⚖️ OhadAI</h1><p>Assistant juridique OHADA</p></div>', unsafe_allow_html=True)
with col2:
    if st.button("🌙" if not st.session_state.dark_mode else "☀️", help="Changer de thème"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# -----------------------------
# SUGGESTIONS
# -----------------------------
st.markdown('<div class="suggestions">', unsafe_allow_html=True)
suggestions = [
    "Procédure d'arbitrage ?",
    "SARL : société de personnes ou de capitaux ?",
    "Articles AUSCGIE sur contrat commercial ?"
]
for s in suggestions:
    if st.button(s, key=s):
        st.session_state.user_input = s
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# ZONE DE CHAT
# -----------------------------
st.markdown('<div class="chat" id="chatBox">', unsafe_allow_html=True)
for speaker, msg in st.session_state.chat_history:
    role = "user" if speaker == "User" else "assistant"
    with st.chat_message(role):
        st.markdown(msg)
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# BARRE D'INPUT FIXE
# -----------------------------
st.markdown('<div class="input-bar"><div class="input-inner">', unsafe_allow_html=True)
user_question = st.chat_input("Posez votre question...") or st.session_state.get("user_input", "")
if st.button("🗑️ Effacer", key="clear_button"):
    st.session_state.chat_history = []
    st.rerun()
st.markdown('</div></div>', unsafe_allow_html=True)

# -----------------------------
# TRAITEMENT MESSAGE
# -----------------------------
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

# -----------------------------
# SCROLL AUTO DANS LE CHAT SEULEMENT
# -----------------------------
st.markdown("""
<script>
const chatBox = window.parent.document.getElementById("chatBox");
if (chatBox) chatBox.scrollTop = chatBox.scrollHeight;
</script>
""", unsafe_allow_html=True)
