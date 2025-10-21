import streamlit as st
from rag_pipeline import generate_answer_stream, rag_chain

# -----------------------------
# CONFIGURATION
# -----------------------------
st.set_page_config(page_title="OhadAI ⚖️", page_icon="⚖️", layout="wide")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "suggestions_visible" not in st.session_state:
    st.session_state.suggestions_visible = True

# -----------------------------
# CSS OPTIMISÉ
# -----------------------------
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    height: 100%;
    margin: 0;
    padding: 0;
    background-color: #FFFFFF;
    font-family: "Inter", sans-serif;
    color: #000000;
}

/* Conteneur principal */
.main {
    display: flex;
    flex-direction: column;
    height: 100vh;
    max-width: 900px;
    margin: 0 auto;
    padding: 0;
}

/* En-tête */
.header {
    text-align: center;
    padding: 0.8rem 0 0.5rem 0;
    margin-bottom: 0.5rem;
}

.header h1 {
    font-size: 1.7rem;
    margin: 0;
    color: #000000;
}

.header p {
    font-size: 0.9rem;
    color: #555555;
    margin: 0.3rem 0 0 0;
}

/* Bouton effacer */
.clear-btn {
    position: fixed;
    top: 0.8rem;
    right: 1rem;
    z-index: 1000;
    background: #FFFFFF;
    color: #2D3748;
    border: 1px solid #2D3748;
    border-radius: 20px;
    padding: 0.3rem 0.7rem;
    cursor: pointer;
    font-size: 0.8rem;
    transition: all 0.2s ease;
}

.clear-btn:hover {
    background: #2D3748;
    color: #FFFFFF;
}

/* Zone du chat (marges optimisées) */
.chat {
    flex: 1;
    overflow-y: auto;
    padding: 0.5rem;
    margin: 0 0.5rem;
    border-radius: 8px;
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    margin-bottom: 3.5rem; /* Espace pour le footer */
}

/* Messages */
.stChatMessage {
    margin-bottom: 0.6rem !important;
}

.stChatMessage .stMarkdown {
    border-radius: 12px;
    padding: 0.6rem 0.8rem;
    line-height: 1.45;
    max-width: 80%;
    border: 1px solid #E2E8F0;
    background: #FFFFFF;
    color: #000000;
    box-shadow: 0 1px 1px rgba(0, 0, 0, 0.03);
}

.stChatMessage.user .stMarkdown {
    background: #F7FAFC;
    margin-left: auto;
    color: #000000;
}

/* Footer sombre (zone d'entrée) */
.input-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #2D3748;
    padding: 0.6rem;
    z-index: 100;
}

.input-bar .stTextInput {
    background: #4A5568 !important;
    border: none !important;
    border-radius: 6px !important;
    color: white !important;
}

.input-bar .stTextInput input {
    color: white !important;
    font-size: 0.9rem !important;
}

.input-bar .stTextInput input::placeholder {
    color: rgba(255, 255, 255, 0.7) !important;
}

/* Suggestions */
.suggestions-container {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 0.6rem;
    margin: 0.5rem 0;
    padding: 0 0.5rem;
}

.suggestion-btn {
    background: #FFFFFF;
    border: 1px solid #2D3748;
    border-radius: 18px;
    padding: 0.4rem 1rem;
    font-size: 0.85rem;
    cursor: pointer;
    color: #2D3748;
    transition: all 0.2s ease;
}

.suggestion-btn:hover {
    background: #2D3748;
    color: #FFFFFF;
}

/* Supprime le footer Streamlit */
footer {visibility: hidden !important;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER + BOUTON EFFACER
# -----------------------------
st.markdown('''
<div class="header">
    <h1>⚖️ OhadAI</h1>
    <p>Assistant juridique OHADA</p>
</div>
''', unsafe_allow_html=True)

# Bouton effacer
st.markdown('''
<button class="clear-btn" onclick="if(confirm('Voulez-vous vraiment effacer l\\'historique ?')){window.location.reload();}">
    🗑️ Effacer
</button>
''', unsafe_allow_html=True)

# -----------------------------
# SUGGESTIONS
# -----------------------------
if st.session_state.suggestions_visible and not st.session_state.chat_history:
    st.markdown('<div class="suggestions-container">', unsafe_allow_html=True)
    suggestions = [
        "Procédure d'arbitrage ?",
        "SARL : société de personnes ou de capitaux ?",
        "Articles AUSCGIE sur contrat commercial ?"
    ]
    for s in suggestions:
        if st.button(s, key=f"sugg_{s}", help="Poser cette question"):
            st.session_state.user_input = s
            st.session_state.suggestions_visible = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# CHAT ZONE
# -----------------------------
st.markdown('<div class="chat" id="chatBox">', unsafe_allow_html=True)
for speaker, msg in st.session_state.chat_history:
    role = "user" if speaker == "User" else "assistant"
    with st.chat_message(role):
        st.markdown(msg)
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# FOOTER SOMBRE (INPUT)
# -----------------------------
st.markdown('<div class="input-bar">', unsafe_allow_html=True)
user_question = st.chat_input("Posez votre question juridique...")
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# TRAITEMENT MESSAGE
# -----------------------------
if user_question and user_question.strip():
    st.session_state.suggestions_visible = False
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

# -----------------------------
# SCROLL AUTOMATIQUE
# -----------------------------
st.markdown("""
<script>
const chatBox = window.parent.document.getElementById("chatBox");
if (chatBox) chatBox.scrollTop = chatBox.scrollHeight;
</script>
""", unsafe_allow_html=True)
