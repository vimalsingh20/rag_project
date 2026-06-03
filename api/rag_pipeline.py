from ingestion.loader import load_pdf
from ingestion.chunking import split_text

from services.embedding import get_embedding
from services.generator import generate_answer
from services.reranker import rerank_chunks

from db.vector_store import VectorStore
from db.faiss_retrieval import faiss_retrieve
from db.bm25_retrieval import bm25_retrieve
from db.runtime_store import store
from services.query_preprocessor import preprocess_query

import time
def ask_rag(question):
    question = preprocess_query(question)
    start_time = time.time()
    query_embedding = get_embedding(
        [question]
    )[0]
    semantic_results = faiss_retrieve(
        query_embedding,
        top_k=3
    )
    bm25_results = bm25_retrieve(
    question,
    store.records,
    top_k=3
)
    combined_results = (
        semantic_results +
        bm25_results
    )
    print(f"Semantic Results: {len(semantic_results)}")
    print(f"BM25 Results: {len(bm25_results)}")
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
        "answer": answer,
        "processing_time": processing_time,
        "sources": sources
    }