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
# CSS AMÉLIORÉ
# -----------------------------
st.markdown("""
<style>
:root {
    --primary: #2D3748;
    --primary-dark: #1A202C;
    --primary-light: #4A5568;
    --background: #FFFFFF;
    --text: #1A202C;
    --text-light: #4A5568;
    --border: #E2E8F0;
    --hover: #F7FAFC;
    --user-bg: #F7FAFC;
    --assistant-bg: #FFFFFF;
}

html, body, [data-testid="stAppViewContainer"] {
    height: 100%;
    margin: 0;
    padding: 0;
    background-color: var(--background);
    font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text);
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

/* En-tête amélioré */
.header {
    text-align: center;
    padding: 1rem 0 0.8rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0.5rem;
}

.header h1 {
    font-size: 1.7rem;
    margin: 0;
    color: var(--text);
    font-weight: 600;
}

.header p {
    font-size: 0.9rem;
    color: var(--text-light);
    margin: 0.3rem 0 0 0;
}

/* Bouton effacer redessiné */
.clear-btn {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 1000;
    display: flex;
    align-items: center;
    gap: 0.3rem;
    background: var(--background);
    color: var(--primary);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.4rem 0.8rem;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 500;
    transition: all 0.2s ease;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.clear-btn:hover {
    background: var(--primary);
    color: white;
    border-color: var(--primary);
}

/* Zone du chat optimisée */
.chat-container {
    flex: 1;
    overflow-y: auto;
    padding: 0.5rem;
    margin: 0 0.5rem;
    border-radius: 8px;
    background-color: var(--background);
    margin-bottom: 4.5rem;
}

.chat-container::-webkit-scrollbar {
    width: 6px;
}

.chat-container::-webkit-scrollbar-thumb {
    background: var(--primary-light);
    border-radius: 3px;
}

/* Messages améliorés */
.stChatMessage {
    margin-bottom: 0.7rem !important;
    animation: fadeIn 0.3s ease-out;
}

.stChatMessage .stMarkdown {
    border-radius: 12px;
    padding: 0.7rem 1rem;
    line-height: 1.5;
    max-width: 85%;
    border: 1px solid var(--border);
    background: var(--assistant-bg);
    color: var(--text);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.stChatMessage.user .stMarkdown {
    background: var(--user-bg);
    margin-left: auto;
    border-color: var(--primary-light);
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(5px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Footer professionnel */
.footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--primary-dark);
    padding: 0.7rem 1rem;
    z-index: 100;
    border-top: 1px solid var(--primary);
}

.footer .stTextInput {
    background: var(--primary-light) !important;
    border: none !important;
    border-radius: 8px !important;
}

.footer .stTextInput input {
    color: white !important;
    font-size: 0.95rem !important;
    padding: 0.5rem !important;
}

.footer .stTextInput input::placeholder {
    color: rgba(255, 255, 255, 0.8) !important;
}

/* Suggestions modernisées */
.suggestions-container {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 0.7rem;
    margin: 1rem 0;
    padding: 0 0.5rem;
}

.suggestion-btn {
    background: var(--background);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 0.5rem 1.2rem;
    font-size: 0.9rem;
    cursor: pointer;
    color: var(--primary);
    transition: all 0.2s ease;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    font-weight: 500;
}

.suggestion-btn:hover {
    background: var(--primary);
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}

/* Supprime le footer Streamlit */
footer {visibility: hidden !important;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown('''
<div class="header">
    <h1>⚖️ OhadAI</h1>
    <p>Assistant juridique OHADA</p>
</div>
''', unsafe_allow_html=True)

# -----------------------------
# BOUTON EFFACER
# -----------------------------
st.markdown('''
<button class="clear-btn">
    🗑️ Effacer l'historique
</button>

<script>
document.querySelector('.clear-btn').addEventListener('click', function() {
    if (confirm('Voulez-vous vraiment effacer l\'historique ?')) {
        window.location.reload();
    }
});
</script>
''', unsafe_allow_html=True)

# -----------------------------
# CHAT CONTAINER
# -----------------------------
st.markdown('<div class="chat-container" id="chatBox">', unsafe_allow_html=True)

# -----------------------------
# SUGGESTIONS
# -----------------------------
if st.session_state.suggestions_visible and not st.session_state.chat_history:
    st.markdown('<div class="suggestions-container">', unsafe_allow_html=True)
    suggestions = [
        ("Procédure d'arbitrage OHADA", "arbitrage"),
        ("SARL : société de personnes ou de capitaux ?", "sarl"),
        ("Articles AUSCGIE sur les contrats commerciaux", "contrats")
    ]
    for text, key in suggestions:
        if st.button(text, key=f"sugg_{key}", help=f"Poser cette question sur {key}"):
            st.session_state.user_input = text
            st.session_state.suggestions_visible = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# AFFICHAGE DES MESSAGES
# -----------------------------
for speaker, msg in st.session_state.chat_history:
    role = "user" if speaker == "User" else "assistant"
    with st.chat_message(role):
        st.markdown(msg)

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# FOOTER PROFESSIONNEL
# -----------------------------
st.markdown('<div class="footer">', unsafe_allow_html=True)
user_question = st.chat_input("Posez votre question juridique ici...")
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# TRAITEMENT DES MESSAGES
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
if (chatBox) {
    chatBox.scrollTop = chatBox.scrollHeight;
}
</script>
""", unsafe_allow_html=True)
