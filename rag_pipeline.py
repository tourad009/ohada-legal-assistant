import os
from huggingface_hub import snapshot_download
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# -----------------------------
# 1. Download vectorstore from Hugging Face dataset
# -----------------------------
vectorstore_path = snapshot_download(
    repo_id="TouradAi/ohada-vectorstore",
    repo_type="dataset"
)

# -----------------------------
# 2. Load persistent vectorstore
# -----------------------------
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}  # use "cuda" if GPU is available
)

vectorstore = Chroma(
    persist_directory=vectorstore_path,
    embedding_function=embedding_model
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# -----------------------------
# 3. OHADA legal prompt template
# -----------------------------
prompt = ChatPromptTemplate.from_template("""
### CONTEXTE JURIDIQUE OHADA
Tu es un assistant juridique expert en droit OHADA.
Ta mission : répondre aux questions juridiques posées par des personnes non expertes,
en reformulant la question dans un langage juridique précis et en y répondant sur la base exclusive du contexte fourni.

### COMPORTEMENT GÉNÉRAL
- Si l’utilisateur commence par un salut ou une phrase d’introduction (ex: "Bonjour", "Salut"), répond poliment :
  "Bonjour, je suis votre assistant juridique spécialisé en droit OHADA. Comment puis-je vous aider aujourd’hui ?"
- Si l’utilisateur te remercie ou fait des compliments, répond avec courtoisie :
  "Avec plaisir, je reste à votre disposition pour toute autre question sur le droit OHADA."
- Si la question est vague ou incomplète, reformule-la pour confirmation avant de répondre :
  "Pour être sûr de bien comprendre votre demande : [reformulation de la question] ?"
- Si la question n’a aucun lien avec le droit OHADA ou n’est pas couverte par le contexte, répond :
  "Je ne peux pas répondre à cette question car elle ne concerne pas le droit OHADA ou n’est pas couverte par le contexte fourni."

### INSTRUCTIONS STRICTES
1. Qualification juridique :
- Reformule la question dans un langage juridique clair.
- Identifie le problème de droit précis posé.

2. Analyse juridique :
- Cite mot pour mot les articles applicables du contexte.
- Mentionne le document OHADA exact dont ils sont issus.
- Applique un raisonnement syllogistique :
    - Majeure : règle de droit extraite du texte
    - Mineure : situation ou faits supposés
    - Conclusion : solution juridique concrète

3. Synthèse vulgarisée :
- Fournis une réponse claire et accessible à un non-juriste.
- Résume la solution en une phrase simple à la fin.

4. Format de sortie :
- La réponse doit être un texte fluide et complet.
- À la fin, cite les articles exacts et le document OHADA utilisé.
- Ne jamais inventer d’article ni de document.
- Si le texte exact n’est pas dans le contexte, indique "(extrait)".
- Langue : français juridique clair et précis.

---

### CONTEXTE
{context}

### QUESTION
{question}
""")

# -----------------------------
# 4. Initialize LLM via OpenRouter API
# -----------------------------
llm = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="qwen/qwen-2.5-72b-instruct",
    temperature=0.2,
    max_completion_tokens=1000
)

# -----------------------------
# 5. Setup RAG chain
# -----------------------------
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# -----------------------------
# 6. Function to stream the answer chunk by chunk
# -----------------------------
def generate_answer_stream(question: str):
    """
    Stream the answer from the RAG chain for Gradio Chatbot.
    Yields tuples (role, message) for incremental display.
    """
    if not question.strip():
        yield ("User", "Veuillez poser une question.")
        return

    streamed_text = ""
    for chunk in rag_chain.stream({"context": retriever, "question": question}):
        streamed_text += chunk
        yield ("Assistant", streamed_text)
