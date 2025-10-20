import streamlit as st
from rag_pipeline import generate_answer_stream, retriever, rag_chain

# Configuration de la page
st.set_page_config(
    page_title="OHADA Legal Assistant",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Style moderne
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .stTextInput>div>div>input {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 10px;
    }
    .stButton>button {
        background-color: #4e73df;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #2e59d9;
    }
    .chat-container {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .user-message {
        background-color: #e3f2fd;
        padding: 12px;
        border-radius: 10px 10px 0 10px;
        margin-bottom: 10px;
    }
    .assistant-message {
        background-color: #f1f1f1;
        padding: 12px;
        border-radius: 10px 10px 10px 0;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Titre centré
st.markdown("<h1 style='text-align: center;'>Assistant Juridique OHADA</h1>", unsafe_allow_html=True)

# Initialisation de l'historique
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Affichage de l'historique du chat
chat_container = st.container()
with chat_container:
    for speaker, message in st.session_state.chat_history:
        if speaker == "User":
            st.markdown(f"<div class='user-message'><b>Vous:</b> {message}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='assistant-message'><b>Assistant:</b> {message}</div>", unsafe_allow_html=True)

# Questions suggérées (boutons modernes)
st.markdown("<h3 style='margin-top: 30px;'>Questions fréquentes</h3>", unsafe_allow_html=True)
suggested_questions = [
    "Quelle est la procédure pour un arbitrage ?",
    "La SARL est-elle une société de personnes ou de capitaux ?",
    "Quels articles de l'AUSCGIE régissent le contrat commercial ?"
]

cols = st.columns(len(suggested_questions))
for i, question in enumerate(suggested_questions):
    if cols[i].button(question, use_container_width=True):
        st.session_state.chat_history.append(("User", question))
        with st.spinner("Réflexion en cours..."):
            placeholder = st.empty()
            full_response = ""
            for chunk in generate_answer_stream(question, retriever, rag_chain):
                full_response = chunk
                placeholder.markdown(f"<div class='assistant-message'><b>Assistant:</b> {full_response}</div>", unsafe_allow_html=True)
            st.session_state.chat_history.append(("Assistant", full_response))
        st.rerun()

# Zone de saisie utilisateur
st.markdown("<h3 style='margin-top: 30px;'>Posez votre question</h3>", unsafe_allow_html=True)
with st.form(key="user_input_form", clear_on_submit=True):
    user_question = st.text_input("", placeholder="Ex: Quelles sont les étapes pour créer une SARL ?", label_visibility="collapsed")
    submit = st.form_submit_button("Envoyer")

if submit and user_question.strip():
    st.session_state.chat_history.append(("User", user_question))
    with st.spinner("Réflexion en cours..."):
        placeholder = st.empty()
        full_response = ""
        for chunk in generate_answer_stream(user_question, retriever, rag_chain):
            full_response = chunk
            placeholder.markdown(f"<div class='assistant-message'><b>Assistant:</b> {full_response}</div>", unsafe_allow_html=True)
        st.session_state.chat_history.append(("Assistant", full_response))
    st.rerun()
