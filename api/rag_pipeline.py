
from services.embedding import get_embedding
from services.generator import generate_answer
from services.reranker import rerank_chunks
from db.faiss_index import FaissIndex
from db.mysql_store import (get_active_document,
    get_active_chunks
)
from db.bm25_retrieval import bm25_retrieve
from services.query_preprocessor import preprocess_query
import time
from db.mysql_store import has_documents


from utils.logger import get_logger

from config.settings import TOP_K

logger = get_logger(__name__)

def ask_rag(question):
    
    if not has_documents():
        return {
        "success": False,
        "message": "Please upload a PDF before asking a question.",
        "answer": "",
        "processing_time": 0,
        "sources": [] }
    
    
    question = preprocess_query(question)
    start_time = time.time()
    query_embedding = get_embedding(
        [question]
    )[0]
    active_document = get_active_document()

    faiss_db = FaissIndex(
        active_document["id"]
    )

    faiss_db.load_or_create_index()

    active_chunks = get_active_chunks()

    semantic_results = faiss_db.retrieve(
        query_embedding,
        active_chunks,
        top_k=TOP_K
    )
    all_chunks = get_active_chunks()
    bm25_results = bm25_retrieve(
    question,
    all_chunks,
    top_k=TOP_K
)
    combined_results = (
        semantic_results +
        bm25_results
    )
    logger.info(f"Semantic Results: {len(semantic_results)}")
    logger.info(f"BM25 Results: {len(bm25_results)}")
    unique_results = []
    seen_chunks = set()
    for chunk in combined_results:
        chunk_text = chunk["chunk"]

        if chunk_text not in seen_chunks:

            unique_results.append(chunk)

            seen_chunks.add(chunk_text)

    results = rerank_chunks(
        question,
        unique_results
    )

    sources = list(
        set(
            [
                chunk["source"]
                for chunk in results
                if "source" in chunk
            ]
        )
    )
    answer = generate_answer(
        question,
        results)
    processing_time = round(
        time.time() - start_time,
        2
    )
    return {
        "success":True,
        "answer": answer,
        "processing_time": processing_time,
        "sources": sources
    }