import streamlit as st
from rag_pipeline import generate_answer_stream, retriever, rag_chain

# Configuration sobre
st.set_page_config(page_title="OHADA Legal Assistant", page_icon="⚖️", layout="centered")
st.title("Assistant Juridique OHADA")

# Initialisation de l'historique
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Affichage de l'historique (style sobre)
for speaker, message in st.session_state.chat_history:
    if speaker == "User":
        st.write(f"**Vous:** {message}")
    else:
        st.write(f"**Assistant:** {message}")
    st.divider()  # Ligne de séparation discrète

# Zone de saisie utilisateur (style minimaliste)
st.text_input(
    "Posez votre question juridique...",
    key="user_question",
    placeholder="Ex: Quelles sont les étapes pour créer une SARL selon l'OHADA ?",
    label_visibility="collapsed"
)

# Bouton d'envoi sobre
if st.button("Envoyer", type="primary"):
    if st.session_state.user_question.strip():
        user_question = st.session_state.user_question
        st.session_state.chat_history.append(("User", user_question))
        st.rerun()

        # Affichage de la question utilisateur
        st.write(f"**Vous:** {user_question}")

        # Génération de la réponse
        placeholder = st.empty()
        full_response = ""
        for chunk in generate_answer_stream(user_question, retriever, rag_chain):
            full_response = chunk
            placeholder.write(f"**Assistant:** {full_response}")

        # Ajout à l'historique
        st.session_state.chat_history.append(("Assistant", full_response))
        st.rerun()
