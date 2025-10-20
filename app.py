import streamlit as st
from rag_pipeline import generate_answer_stream, retriever, rag_chain

# Configuration sobre et moderne
st.set_page_config(
    page_title="OHADA Legal Assistant",
    page_icon="⚖️",
    layout="centered"
)

# Message d'accueil si aucun historique
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.markdown("""
    <div style="text-align: center; margin-bottom: 40px;">
        <h1 style="font-size: 2.5em; margin-bottom: 10px;">OhadAI</h1>
        <p style="font-size: 1.2em; color: #666;">Votre assistant juridique spécialisé dans le droit OHADA</p>
        <p style="font-size: 0.9em; color: #888; margin-top: 20px;">
            Posez vos questions juridiques et obtenez des réponses précises basées sur les textes OHADA.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Affichage de l'historique (si existant)
if st.session_state.chat_history:
    for speaker, message in st.session_state.chat_history:
        if speaker == "User":
            st.markdown(f"**Vous:** {message}")
        else:
            st.markdown(f"**OhadAI:** {message}")
        st.divider()

# Zone de saisie utilisateur (style minimaliste)
user_question = st.text_input(
    "Posez votre question juridique...",
    placeholder="Ex: Quelles sont les étapes pour créer une SARL selon l'OHADA ?",
    label_visibility="collapsed"
)

# Bouton d'envoi sobre
if st.button("Envoyer", type="primary"):
    if user_question.strip():
        st.session_state.chat_history.append(("User", user_question))
        st.rerun()

        # Affichage de la question utilisateur
        st.markdown(f"**Vous:** {user_question}")

        # Génération de la réponse
        placeholder = st.empty()
        full_response = ""
        for chunk in generate_answer_stream(user_question, retriever, rag_chain):
            full_response = chunk
            placeholder.markdown(f"**OhadAI:** {full_response}")

        # Ajout à l'historique
        st.session_state.chat_history.append(("Assistant", full_response))
        st.rerun()
