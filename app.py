import gradio as gr
from rag_pipeline import generate_answer_stream

# --- Gradio UI ---
with gr.Blocks(theme=gr.themes.Default()) as demo:
    # Title
    gr.Markdown(
        "<h1 style='color:#1E3A8A; font-family:Inter; font-weight:bold'>Assistant juridique OHADA</h1>"
    )
    
    # Chatbot with modern message format
    chatbot = gr.Chatbot(
        label="OHADA Legal Assistant",
        elem_id="chatbot",
        type="messages"  # ✅ OpenAI-style format
    )
    
    # Suggested question buttons
    suggested_questions = [
        "Quelle est la procédure pour un arbitrage ?",
        "La SARL est-elle une société de personnes ou de capitaux ?",
        "Quels articles de l'AUSCGIE régissent le contrat commercial ?"
    ]

    # Create buttons in a row
    with gr.Row():
        for q in suggested_questions:
            gr.Button(q).click(
                fn=lambda question=q: list(generate_answer_stream(question)),
                outputs=chatbot
            )

    # Textbox for user question
    msg = gr.Textbox(
        label="Pose ta question juridique :",
        placeholder="Ex : Quelle est la procédure pour un arbitrage ?",
    )

    # Submit button
    submit = gr.Button("Répondre")

    # Events: Enter or click
    submit.click(fn=generate_answer_stream, inputs=msg, outputs=chatbot)
    msg.submit(fn=generate_answer_stream, inputs=msg, outputs=chatbot)

demo.launch()
