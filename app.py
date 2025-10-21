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
# CSS OPTIMISÉ POUR HAUTEUR PARFAITE
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

/* Conteneur principal - hauteur 100vh */
.main {
    display: flex;
    flex-direction: column;
    height: 100vh;
    max-width: 900px;
    margin: 0 auto;
    padding: 0;
    overflow: hidden;
}

/* En-tête ultra-compact */
.header {
    text-align: center;
    padding: 0.6rem 0 0.4rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0.2rem;
}

.header h1 {
    font-size: 1.5rem;
    margin: 0;
    color: var(--text);
    font-weight: 600;
}

.header p {
    font-size: 0.8rem;
    color: var(--text-light);
    margin: 0.2rem 0 0 0;
}

/* Bouton effacer miniaturisé */
.clear-btn {
    position: fixed;
    top: 0.6rem;
    right: 1rem;
    z-index: 1000;
    background: var(--background);
    color: var(--primary);
    border: 1px solid var(--border);
    border-radius: 5px;
    padding: 0.25rem 0.6rem;
    cursor: pointer;
    font-size: 0.75rem;
    transition: all 0.2s ease;
}

.clear-btn:hover {
    background: var(--primary);
    color: white;
}

/* Zone de chat - hauteur calculée précisément */
.chat-container {
    flex: 1;
    overflow-y: auto;
    padding: 0.4rem 0.3rem;
    margin: 0 0.4rem;
    border-radius: 6px;
    background-color: var(--background);
    margin-bottom: 3.2rem; /* Espace exact pour le footer */
    max-height: calc(100vh - 110px); /* Ajustement pixel-perfect */
}

/* Scrollbar minimaliste */
.chat-container::-webkit-scrollbar {
    width: 5px;
}

.chat-container::-webkit-scrollbar-thumb {
    background: var(--primary-light);
    border-radius: 2px;
}

/* Messages (inchangés) */
.stChatMessage {
    margin-bottom: 0.5rem !important;
    animation: fadeIn 0.2s ease-out;
}

.stChatMessage .stMarkdown {
    border-radius: 10px;
    padding: 0.5rem 0.7rem;
    line-height: 1.4;
    max-width: 85%;
    border: 1px solid var(--border);
    background: var(--assistant-bg);
    color: var(--text);
    box-shadow: 0 1px 1px rgba(0, 0, 0, 0.02);
}

.stChatMessage.user .stMarkdown {
    background: var(--user-bg);
    margin-left: auto;
}

/* Footer ultra-compact */
.footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--primary-dark);
    padding: 0.4rem 0.8rem;
    z-index: 100;
    border-top: 1px solid var(--primary);
    height: 45px; /* Hauteur réduite */
    display: flex;
    align-items: center;
}

.footer .stTextInput {
    background: var(--primary-light) !important;
    border: none !important;
    border-radius: 6px !important;
    margin: 0 !important;
    height: 36px !important;
}

.footer .stTextInput input {
    color: white !important;
    font-size: 0.9rem !important;
    padding: 0.4rem 0.6rem !important;
}

.footer .stTextInput input::placeholder {
    color: rgba(255, 255, 255, 0.7) !important;
}

/* SUGGESTIONS - VERSION ORIGINALE CONSERVÉE */
.suggestions-container {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin: 0.3rem 0 0.4rem 0;
    padding: 0;
}

.suggestion-btn {
    background: var(--background);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 0.4rem 1rem;
    font-size: 0.8rem;
    cursor: pointer;
    color: var(--primary); /* Texte sombre sur fond clair */
    transition: all 0.15s ease;
    box-shadow: 0 1px 1px rgba(0, 0, 0, 0.02);
}

.suggestion-btn:hover {
    background: var(--primary);
    color: white; /* Texte clair sur fond sombre */
}

/* Animation */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(3px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Supprime le footer Streamlit */
footer {visibility: hidden !important;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# STRUCTURE PARFAITEMENT AJUSTÉE
# -----------------------------
# 1. En-tête
st.markdown('''
<div class="header">
    <h1>⚖️ OhadAI</h1>
    <p>Assistant juridique OHADA</p>
</div>
''', unsafe_allow_html=True)

# 2. Bouton effacer
st.markdown('''
<button class="clear-btn">
    🗑️ Effacer
</button>
<script>
document.querySelector('.clear-btn').addEventListener('click', function() {
    if(confirm('Voulez-vous vraiment effacer l\'historique ?')) {
        window.location.reload();
    }
});
</script>
''', unsafe_allow_html=True)

# 3. Conteneur de chat avec hauteur parfaite
st.markdown('<div class="chat-container" id="chatBox">', unsafe_allow_html=True)

# 4. Suggestions (version originale conservée)
if st.session_state.suggestions_visible and not st.session_state.chat_history:
    st.markdown('<div class="suggestions-container">', unsafe_allow_html=True)
    suggestions = [
        ("Procédure d'arbitrage OHADA", "arbitrage"),
        ("SARL : société de personnes ou de capitaux ?", "sarl"),
        ("Articles AUSCGIE sur contrats", "contrats")
    ]
    for text, key in suggestions:
        st.markdown(f'''
        <button class="suggestion-btn" onclick="{
            f"window.streamlitSetComponentValue('{text}')"
        }">{text}</button>
        ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 5. Affichage des messages
for speaker, msg in st.session_state.chat_history:
    role = "user" if speaker == "User" else "assistant"
    with st.chat_message(role):
        st.markdown(msg)

st.markdown('</div>', unsafe_allow_html=True)

# 6. Footer compact
st.markdown('<div class="footer">', unsafe_allow_html=True)
user_question = st.chat_input("Posez votre question juridique...")
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
const chatBox = document.getElementById("chatBox");
if (chatBox) {
    chatBox.scrollTop = chatBox.scrollHeight;
}
</script>
""", unsafe_allow_html=True)
