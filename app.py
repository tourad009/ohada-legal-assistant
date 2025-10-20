import streamlit as st
from rag_pipeline import generate_answer_stream, retriever, rag_chain

# Configuration basique
st.set_page_config(
    page_title="OHADA Legal Assistant",
    layout="wide"
)

st.title("Assistant Juridique OHADA")

# Initialisation de l'historique
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Affichage de l'historique du chat
for speaker, message in st.session_state.chat_history:
    with st.chat_message(speaker.lower()):
        st.markdown(message)

# Questions suggérées (boutons simples)
st.subheader("Questions fréquentes")
suggested_questions = [
    "Quelle est la procédure pour un arbitrage ?",
    "La SARL est-elle une société de personnes ou de capitaux ?",
    "Quels articles de l'AUSCGIE régissent le contrat commercial ?"
]

cols = st.columns(len(suggested_questions))
for i, question in enumerate(suggested_questions):
    if cols[i].button(question, use_container_width=True):
        st.session_state.chat_history.append(("User", question))
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            for chunk in generate_answer_stream(question, retriever, rag_chain):
                full_response = chunk
                placeholder.markdown(full_response)
            st.session_state.chat_history.append(("Assistant", full_response))
        st.rerun()

# Zone de saisie utilisateur
st.subheader("Posez votre question")
with st.form(key="user_input_form", clear_on_submit=True):
    user_question = st.text_input(
        "Votre question juridique :",
        placeholder="Ex: Quelles sont les étapes pour créer une SARL ?",
        label_visibility="collapsed"
    )
    submit = st.form_submit_button("Envoyer")

if submit and user_question.strip():
        st.session_state.chat_history.append(("User", user_question))
        with st.chat_message("user"):
            st.markdown(user_question)
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            for chunk in generate_answer_stream(user_question, retriever, rag_chain):
                full_response = chunk
                placeholder.markdown(full_response)
            st.session_state.chat_history.append(("Assistant", full_response))
        st.rerun()
