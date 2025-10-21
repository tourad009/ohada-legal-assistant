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
# CSS MODERNE ET COLORÉ
# -----------------------------
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    height: 100%;
    overflow: hidden !important;
    background-color: #f5f7fa;
    font-family: "Inter", sans-serif;
    color: #1e1e1e;
}

/* Container principal */
.main {
    display: flex;
    flex-direction: column;
    height: 100vh;
    max-width: 900px;
    margin: auto;
}

/* Header */
.header {
    text-align: center;
    padding: 1rem 0 0.5rem 0;
}
.header h1 {
    font-size: 1.8rem;
    margin: 0;
}
.header p {
    font-size: 0.9rem;
    color: #6c757d;
    margin-top: 0.3rem;
}

/* Bouton effacer */
.clear-btn {
    position: absolute;
    top: 1.2rem;
    right: 1rem;
    background: linear-gradient(135deg, #ff6b6b, #fa5252);
    color: #fff;
    border: none;
    border-radius: 20px;
    padding: 0.35rem 0.9rem;
    cursor: pointer;
    font-size: 0.85rem;
    transition: all 0.25s ease;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.clear-btn:hover {
    background: linear-gradient(135deg, #fa5252, #f03e3e);
    transform: scale(1.05);
}

/* Zone du chat */
.chat {
    position: relative;
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    border-radius: 12px;
    background-color: #f5f7fa;
    scroll-behavior: smooth;
}
.chat::-webkit-scrollbar {
    width: 6px;
}
.chat::-webkit-scrollbar-thumb {
    background: #ccc;
    border-radius: 4px;
}

/* Messages */
.stChatMessage {
    margin-bottom: 0.75rem !important;
}
.stChatMessage .stMarkdown {
    border-radius: 16px;
    padding: 0.8rem 1rem;
    line-height: 1.5;
    max-width: 75%;
    border: none;
    animation: fadeIn 0.25s ease-out;
}

/* Couleurs des bulles */
.stChatMessage.user .stMarkdown {
    background: #d1f7c4; /* Vert pastel clair */
    color: #1e1e1e;
    margin-left: auto;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.stChatMessage.assistant .stMarkdown {
    background: #ffffff;
    color: #1e1e1e;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

/* Animation d'apparition */
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
    background: #ffffff;
    border: 1px solid #dee2e6;
    border-radius: 20px;
    padding: 0.5rem 1.2rem;
    font-size: 0.9rem;
    cursor: pointer;
    color: #333;
    transition: all 0.2s ease;
}
.suggestions button:hover {
    background: #e9ecef;
}

/* Input fixée */
.input-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #ffffff;
    border-top: 1px solid #dee2e6;
    padding: 0.6rem 0.75rem;
}
.input-inner {
    max-width: 900px;
    margin: auto;
}

/* Supprime le footer Streamlit */
footer {visibility: hidden !important;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown('<div class="header"><h1>⚖️ OhadAI</h1><p>Assistant juridique OHADA</p></div>', unsafe_allow_html=True)

# -----------------------------
# SUGGESTIONS (avant premier message)
# -----------------------------
if st.session_state.suggestions_visible:
    st.markdown('<div class="suggestions">', unsafe_allow_html=True)
    suggestions = [
        "Procédure d'arbitrage ?",
        "SARL : société de personnes ou de capitaux ?",
        "Articles AUSCGIE sur contrat commercial ?"
    ]
    for s in suggestions:
        if st.button(s, key=s):
            st.session_state.user_input = s
            st.session_state.suggestions_visible = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# CHAT ZONE
# -----------------------------
st.markdown('<div class="chat" id="chatBox">', unsafe_allow_html=True)

# Bouton effacer (fonctionnel)
if st.button("🗑️ Effacer la conversation", key="clear_chat", help="Réinitialiser le chat", use_container_width=False):
    st.session_state.chat_history = []
    st.session_state.suggestions_visible = True
    st.rerun()

for speaker, msg in st.session_state.chat_history:
    role = "user" if speaker == "User" else "assistant"
    with st.chat_message(role):
        st.markdown(msg)
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# INPUT FIXE
# -----------------------------
st.markdown('<div class="input-bar"><div class="input-inner">', unsafe_allow_html=True)
user_question = st.chat_input("Posez votre question juridique...") or st.session_state.get("user_input", "")
st.markdown('</div></div>', unsafe_allow_html=True)

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

    st.session_state.user_input = ""

# -----------------------------
# SCROLL AUTOMATIQUE
# -----------------------------
st.markdown("""
<script>
const chatBox = window.parent.document.getElementById("chatBox");
if (chatBox) chatBox.scrollTop = chatBox.scrollHeight;
</script>
""", unsafe_allow_html=True)
