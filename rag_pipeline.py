# rag_pipeline.py
import os
import zipfile
from huggingface_hub import snapshot_download
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# -----------------------------
# 1. Télécharger et dézipper la base vectorielle
# -----------------------------
local_dir = "ohada_vectorstore"
repo_dir = snapshot_download(
    repo_id="TouradAi/ohada-vectorstore",
    repo_type="dataset"
)

# Recherche du zip
zip_path = None
for f in os.listdir(repo_dir):
    if f.endswith(".zip"):
        zip_path = os.path.join(repo_dir, f)
        break

if not zip_path:
    raise FileNotFoundError(f"Aucun fichier .zip trouvé dans {repo_dir}")

# Décompression
os.makedirs(local_dir, exist_ok=True)
with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall(local_dir)

print(f"✅ Base vectorielle extraite dans : {local_dir}")

# -----------------------------
# 2. Charger la base vectorielle
# -----------------------------
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)

vectorstore = Chroma(
    persist_directory=local_dir,
    embedding_function=embedding_model
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# -----------------------------
# 3. Prompt OHADA
# -----------------------------
prompt = ChatPromptTemplate.from_template("""
### CONTEXTE JURIDIQUE OHADA
Tu es un assistant juridique expert en droit OHADA.
Ta mission : répondre aux questions juridiques posées par des personnes non expertes,
en reformulant la question dans un langage juridique précis et en y répondant sur la base exclusive du contexte fourni.

### QUESTION
{question}

### CONTEXTE
{context}
""")

# -----------------------------
# 4. LLM via OpenRouter
# -----------------------------
llm = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="qwen/qwen-2.5-72b-instruct",
    temperature=0.2,
    max_completion_tokens=1000
)

# -----------------------------
# 5. Construire la chaîne RAG
# -----------------------------
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# -----------------------------
# 6. Fonction de génération (streaming)
# -----------------------------
def generate_answer_stream(question: str):
    """
    Génère une réponse au format streaming depuis la chaîne RAG.
    Yields: texte progressif (string)
    """
    if not question.strip():
        yield "Veuillez poser une question."
        return

    # Préparer le contexte via le retriever
    docs = retriever.get_relevant_documents(question)
    context_text = "\n".join([doc.page_content for doc in docs])

    # Combiner question et contexte pour le prompt
    prompt_input = {"question": question, "context": context_text}

    streamed_text = ""
    for chunk in rag_chain.stream(prompt_input):
        streamed_text += chunk
        yield streamed_text
