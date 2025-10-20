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
def setup_vectorstore():
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

    # Debug : afficher le contenu extrait
    print(f"✅ Contenu extrait dans {local_dir}:")
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            print(f"  - {os.path.join(root, file)}")

    return local_dir

# -----------------------------
# 2. Charger la base vectorielle
# -----------------------------
def load_vectorstore(local_dir):
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )
    vectorstore = Chroma(
        persist_directory=local_dir,
        embedding_function=embedding_model
    )
    # Debug : vérifier le nombre de documents
    print(f"🔍 Nombre de documents dans Chroma : {vectorstore._collection.count()}")
    return vectorstore

# -----------------------------
# 3. Initialisation du retriever
# -----------------------------
def setup_retriever(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    return retriever

# -----------------------------
# 4. Prompt OHADA
# -----------------------------
def setup_prompt():
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
    return prompt

# -----------------------------
# 5. LLM via OpenRouter
# -----------------------------
def setup_llm():
    llm = ChatOpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        model="qwen/qwen-2.5-72b-instruct",
        temperature=0.2,
        max_tokens=1000  # Utilisation de max_tokens au lieu de max_completion_tokens (selon la doc OpenAI-compatible)
    )
    return llm

# -----------------------------
# 6. Construire la chaîne RAG
# -----------------------------
def setup_rag_chain(retriever, prompt, llm):
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain

# -----------------------------
# 7. Fonction de génération (streaming)
# -----------------------------
def generate_answer_stream(question: str, rag_chain):
    """
    Génère une réponse au format streaming depuis la chaîne RAG.
    Yields: texte progressif (string)
    """
    if not question.strip():
        yield "Veuillez poser une question."
        return

    try:
        streamed_text = ""
        for chunk in rag_chain.stream(question):
            streamed_text += chunk
            yield streamed_text
    except Exception as e:
        yield f"Erreur lors de la génération de la réponse : {str(e)}"

# -----------------------------
# Initialisation globale
# -----------------------------
local_dir = setup_vectorstore()
vectorstore = load_vectorstore(local_dir)
retriever = setup_retriever(vectorstore)
prompt = setup_prompt()
llm = setup_llm()
rag_chain = setup_rag_chain(retriever, prompt, llm)