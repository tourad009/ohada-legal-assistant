import streamlit as st
from rag_pipeline import generate_answer_stream

st.set_page_config(page_title="OHADA Legal Assistant", layout="wide")

# --- Initialize chat history ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("Assistant juridique OHADA")

# --- Suggested question buttons ---
suggested_questions = [
    "Quelle est la procédure pour un arbitrage ?",
    "La SARL est-elle une société de personnes ou de capitaux ?",
    "Quels articles de l'AUSCGIE régissent le contrat commercial ?"
]

cols = st.columns(len(suggested_questions))
for i, question in enumerate(suggested_questions):
    if cols[i].button(question):
        # Append user question to history
        st.session_state.chat_history.append(("User", question))
        # Placeholder for assistant streaming
        placeholder = st.empty()
        assistant_text = ""
        for chunk in generate_answer_stream(question):
            # chunk = ("Assistant", text)
            assistant_text += chunk[1]
            placeholder.markdown(assistant_text)
        # Append full assistant message
        st.session_state.chat_history.append(("Assistant", assistant_text))

# --- User input ---
with st.form(key="user_input_form", clear_on_submit=True):
    user_question = st.text_input("Pose ta question juridique :", "")
    submit = st.form_submit_button("Répondre")

if submit and user_question.strip():
    st.session_state.chat_history.append(("User", user_question))
    placeholder = st.empty()
    assistant_text = ""
    for chunk in generate_answer_stream(user_question):
        assistant_text += chunk[1]
        placeholder.markdown(assistant_text)
    st.session_state.chat_history.append(("Assistant", assistant_text))

# --- Display chat history ---
for speaker, message in st.session_state.chat_history:
    with st.chat_message(speaker.lower()):
        st.markdown(message)
