import gradio as gr
from rag_pipeline import generate_answer_stream

# --- Gradio UI ---
with gr.Blocks(theme=gr.themes.Default()) as demo:
    # Title
    gr.Markdown(
        "<h1 style='color:#1E3A8A; font-family:Inter; font-weight:bold'>Assistant juridique OHADA</h1>"
    )
    
    chatbot = gr.Chatbot(elem_id="chatbot", label="OHADA Legal Assistant")
    
    # Suggested prompt buttons
    suggested_questions = [
        "Quelle est la procédure pour un arbitrage ?",
        "La SARL est-elle une société de personnes ou de capitaux ?",
        "Quels articles de l'AUSCGIE régissent le contrat commercial ?"
    ]
    
    with gr.Row():
        for question in suggested_questions:
            gr.Button(question).click(
                generate_answer_stream,
                inputs=gr.Textbox.update(value=question),
                outputs=chatbot
            )
    
    msg = gr.Textbox(
        label="Pose ta question juridique :",
        placeholder="Ex : Quelle est la procédure pour un arbitrage ?"
    )
    
    submit = gr.Button("Répondre")
    
    submit.click(generate_answer_stream, inputs=msg, outputs=chatbot)
    msg.submit(generate_answer_stream, inputs=msg, outputs=chatbot)

demo.launch()
