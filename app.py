import streamlit as st
from rag_pipeline import generate_answer_stream

# =========================
# Configuration de la page
# =========================
st.set_page_config(page_title="Assistant juridique OHADA", layout="wide")

st.title("⚖️ Assistant juridique OHADA")

# =========================
# Initialisation de l’historique
# =========================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# =========================
# Suggestions de questions
# =========================
st.subheader("💬 Suggestions de questions")
suggested_questions = [
    "Quelle est la procédure pour un arbitrage ?",
    "La SARL est-elle une société de personnes ou de capitaux ?",
    "Quels articles de l'AUSCGIE régissent le contrat commercial ?"
]

cols = st.columns(len(suggested_questions))
for i, question in enumerate(suggested_questions):
    if cols[i].button(question):
        st.session_state.chat_history.append(("user", question))
        placeholder = st.empty()
        response_text = ""
        for chunk in generate_answer_stream(question):
            response_text = chunk 
            placeholder.markdown(response_text)
        st.session_state.chat_history.append(("assistant", response_text))

# =========================
# Zone d’entrée utilisateur
# =========================
st.subheader("🧾 Pose ta question juridique :")
user_question = st.text_input(
    "Ta question :", placeholder="Ex : Quelle est la procédure pour un arbitrage ?"
)

if st.button("Répondre") and user_question.strip():
    st.session_state.chat_history.append(("user", user_question))
    placeholder = st.empty()
    response_text = ""
    for chunk in generate_answer_stream(user_question):
        response_text = chunk
        placeholder.markdown(response_text)
    st.session_state.chat_history.append(("assistant", response_text))

# =========================
# Affichage de l’historique complet
# =========================
st.divider()
st.subheader("🗂️ Historique de la conversation")

for role, content in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(content)
