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
    Tu es un assistant juridique expert en droit OHADA.

    ### RÈGLES À APPLIQUER
    1. **Questions juridiques OHADA** :
       - Répondre uniquement à partir du CONTEXTE fourni.
       - Reformuler la question dans un langage juridique précis (1 phrase).
       - Citer **mot pour mot** tout article ou extrait utilisé.
       - Ne rien inventer en dehors du CONTEXTE.
       - Si le CONTEXTE ne permet pas de répondre, dire :
         > "Les informations disponibles dans les extraits fournis ne permettent pas de répondre entièrement à cette question."
       - Réponse claire, concise, structurée, adaptée à un non-juriste.

    2. **Questions ou messages hors contexte juridique** :
       - Répondre de manière polie, naturelle et humaine.
       - Tu peux inclure un salut ou un mot amical.
       - Inviter subtilement l’utilisateur à poser une question sur le droit OHADA.
       - Ne jamais inventer d’information juridique.

    ### QUESTION POSÉE
    {question}

    ### CONTEXTE À UTILISER (EXCLUSIF POUR LES QUESTIONS OHADA)
    {context}

    ### FORMAT DE LA RÉPONSE
    - Si question OHADA :
        1. Reformulation juridique de la question
        2. Réponse synthétique
        3. Citation directe d’articles si nécessaire
    - Si question hors contexte :
        1. Réponse polie, naturelle et humaine
        2. Inviter subtilement à poser une question sur le droit OHADA
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
