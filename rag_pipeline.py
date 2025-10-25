import os
import zipfile
from huggingface_hub import snapshot_download
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()


# Download and unzip vectorstore
def setup_vectorstore():
    local_dir = "ohada_vectorstore"
    repo_dir = snapshot_download(
        repo_id="TouradAi/ohada-vectorstore", repo_type="dataset"
    )

    zip_path = None
    for f in os.listdir(repo_dir):
        if f.endswith(".zip"):
            zip_path = os.path.join(repo_dir, f)
            break
    if not zip_path:
        raise FileNotFoundError(f"Aucun fichier .zip trouvé dans {repo_dir}")

    os.makedirs(local_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(local_dir)

    print(f"✅ Contenu extrait dans {local_dir}:")
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            print(f"  - {os.path.join(root, file)}")

    return local_dir


def load_vectorstore(local_dir):
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )
    vectorstore = Chroma(
        persist_directory=local_dir, embedding_function=embedding_model
    )
    return vectorstore


def setup_retriever(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    return retriever


def setup_prompt():
    prompt = ChatPromptTemplate.from_template("""
Tu es un assistant juridique spécialisé en droit OHADA. 
Ta mission est de répondre aux questions de manière claire, fiable et pédagogique.

### RÈGLES IMPORTANTES
- Répond uniquement à partir du **CONTEXTE fourni**.
- Si tu cites un article, tu dois le **reproduire mot pour mot**.
- Si le CONTEXTE ne contient pas l’information demandée, répond :
  "Je n'ai pas assez d'informations dans les documents que j'ai pour répondre précisément à cette question."

### STYLE DE RÉPONSE
- Clair, fluide, naturel.
- Adapté à une personne non juriste.
- Pas de langage excessivement technique si non nécessaire.
- Pas besoin d’annoncer "reformulation" ou "synthèse".

### QUESTION
{question}

### CONTEXTE (EXCLUSIF)
{context}
""")
    return prompt


def setup_llm():
    llm = ChatOpenAI(
        api_key=SecretStr(os.environ.get("OPENROUTER_API_KEY") or ""),
        base_url="https://openrouter.ai/api/v1",
        model="qwen/qwen-2.5-72b-instruct",
        temperature=0.1,
        model_kwargs={"max_completion_tokens": 1000},
    )
    return llm


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


# Global Initialization
local_dir = setup_vectorstore()
vectorstore = load_vectorstore(local_dir)
retriever = setup_retriever(vectorstore)
prompt = setup_prompt()
llm = setup_llm()
rag_chain = setup_rag_chain(retriever, prompt, llm)
