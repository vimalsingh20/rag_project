from ingestion.loader import load_pdf
from ingestion.chunking import split_text
from services.embedding import get_embedding
from services.generator import generate_answer
from db.vector_store import VectorStore
from db.faiss_retrieval import faiss_retrieve
from db.runtime_store import store
from services.reranker import rerank_chunks

def ask_rag(question):
    query_embedding = get_embedding([question])[0]
     
    results = faiss_retrieve(
    query_embedding,
    top_k=3
)
    results = rerank_chunks(
    question,
    results
)
    
    # generate final answer 
    
    answer = generate_answer(question,results)
    
    return answer
    
    