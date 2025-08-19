import os
import logging
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import MarkdownTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate


# --- Settings ---
class Settings(BaseSettings):
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    chunk_size: int = 600
    chunk_overlap: int = 175
    retrieval_k: int = 3
    fetch_k: int = 10
    lambda_mult: float = 0.9
    data_dir: str = "./data"
    chroma_dir: str = "./chroma_db"
    model_name: str = "gpt-4o"
    max_tokens: int = 350

    class Config:
        env_file = ".env"


settings = Settings()

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI App ---
app = FastAPI(title="Oxylabs RAG QA System")


# --- Pydantic Models ---
class QueryRequest(BaseModel):
    question: str = Field(..., max_length=500,
                          description="Your question.")

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        text = v.strip()
        if len(text) < 5:
            raise HTTPException(
                status_code=422, detail="Please write a longer question."
            )
        return v


class QueryResponse(BaseModel):
    answer: str
    sources: List[str]


# --- Document Loader ---
def load_documents() -> List:
    if not os.path.isdir(settings.data_dir):
        raise FileNotFoundError(f"Data directory {settings.data_dir} not found.")

    docs = []
    for file in os.listdir(settings.data_dir):
        if file.endswith(".txt"):
            path = os.path.join(settings.data_dir, file)
            docs.extend(TextLoader(path).load())

    if not docs:
        raise RuntimeError("No documents loaded. Make sure .txt files exist in /data.")

    logger.info(f"Loaded {len(docs)} documents.")
    return docs


documents = load_documents()

# --- Text Chunking ---
text_splitter = MarkdownTextSplitter(
    chunk_size=settings.chunk_size,
    chunk_overlap=settings.chunk_overlap,
    add_start_index=True,
)
docs = text_splitter.split_documents(documents)
logger.info(f"Split into {len(docs)} chunks.")

# --- Embeddings & Vector DB ---
embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)

if os.path.exists(settings.chroma_dir):
    vectordb = Chroma(
        persist_directory=settings.chroma_dir, embedding_function=embeddings
    )
    logger.info("Loaded existing Chroma vector store.")
else:
    vectordb = Chroma.from_documents(
        docs, embedding=embeddings, persist_directory=settings.chroma_dir
    )
    logger.info("Created and auto-persisted new Chroma vector store.")


# --- Retriever with MMR Search ---
retriever = vectordb.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": settings.retrieval_k,
        "fetch_k": settings.fetch_k,
        "lambda_mult": settings.lambda_mult,
    },
)

# --- LLM & Prompt ---
system_prompt = (
    "You are an assistant for question-answering tasks about Oxylabs developer documentation. "
    "Use the following pieces of retrieved context to answer the question. "
    "If you don't know the answer, say that you don't know. "
    "Use five sentences maximum and keep the answer concise.\n\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

llm = ChatOpenAI(
    model=settings.model_name,
    temperature=0,
    max_tokens=settings.max_tokens,
    openai_api_key=settings.openai_api_key,
)

question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)


# --- API Routes ---
@app.get("/health")
def health():
    """Simple health check."""
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    """
    Answer a question using the RAG chain.
    Returns the generated answer and the list of source documents.
    """
    if not documents:
        logger.error("No documents available for retrieval.")
        raise HTTPException(status_code=500, detail="Document index is empty.")

    try:
        result = rag_chain.invoke({"input": request.question})
        answer = result.get("answer", "")
        context_docs = result.get("context", [])

        sources = [doc.metadata.get("source", "") for doc in context_docs]
        unique_sources = list(dict.fromkeys(sources))

        return QueryResponse(answer=answer, sources=unique_sources)

    except Exception:
        logger.exception("Unhandled exception during RAG chain invocation.")
        raise HTTPException(
            status_code=500, detail="Internal server error during RAG query."
        )
