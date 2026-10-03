from services.embedding import get_embedding
from services.generator import generate_answer
from services.reranker import rerank_chunks

from db.faiss_index import FaissIndex

from db.mysql_store import (
    get_document_by_id,
    get_chunks_by_document_id
)

from db.bm25_retrieval import bm25_retrieve
from services.query_preprocessor import preprocess_query

import time

from utils.logger import get_logger

from config.settings import TOP_K


logger = get_logger(__name__)


# =========================================
# RAG Question Answering
# =========================================

def ask_rag(
    question,
    user_id,
    document_id
):

    start_time = time.time()

    # =========================================
    # Get EXACT Document
    # =========================================

    document = get_document_by_id(
        document_id,
        user_id
    )

    if document is None:

        return {
            "success": False,
            "message": (
                "Selected document was not found."
            ),
            "answer": "",
            "processing_time": 0,
            "sources": []
        }

    document_filename = document.get(
        "filename",
        "Unknown"
    )

    logger.info(
        f"RAG request | user_id={user_id} "
        f"| document_id={document_id} "
        f"| filename={document_filename}"
    )

    # =========================================
    # Preprocess Question
    # =========================================

    original_question = (
        question.strip()
        if question
        else ""
    )

    processed_question = preprocess_query(
        original_question
    )

    # =========================================
    # Safety Fallback
    # =========================================

    if not processed_question.strip():

        processed_question = (
            original_question
        )

    logger.info(
        f"Original question: "
        f"{original_question}"
    )

    logger.info(
        f"Processed question: "
        f"{processed_question}"
    )

    # =========================================
    # Get ONLY Selected Document Chunks
    # =========================================

    active_chunks = get_chunks_by_document_id(
        document_id,
        user_id
    )

    if not active_chunks:

        return {
            "success": False,
            "message": (
                "No processed content found "
                "for the selected PDF."
            ),
            "answer": "",
            "processing_time": round(
                time.time() - start_time,
                2
            ),
            "sources": []
        }

    logger.info(
        f"Document {document_id} chunks: "
        f"{len(active_chunks)}"
    )

    # =========================================
    # Create Query Embedding
    # =========================================

    query_embedding = get_embedding(
        [processed_question]
    )[0]

    # =========================================
    # FAISS Semantic Retrieval
    # =========================================

    faiss_db = FaissIndex(
        document_id
    )

    faiss_db.load_or_create_index()

    semantic_results = faiss_db.retrieve(
        query_embedding,
        active_chunks,
        top_k=TOP_K
    )

    logger.info(
        f"FAISS results: "
        f"{len(semantic_results)}"
    )

    # =========================================
    # BM25 Keyword Retrieval
    # =========================================

    bm25_results = bm25_retrieve(
        processed_question,
        active_chunks,
        top_k=TOP_K
    )

    logger.info(
        f"BM25 results: "
        f"{len(bm25_results)}"
    )

    # =========================================
    # Combine Results
    # =========================================

    combined_results = (
        semantic_results
        +
        bm25_results
    )

    logger.info(
        f"Combined results: "
        f"{len(combined_results)}"
    )

    # =========================================
    # Remove Duplicate Chunks
    # =========================================

    unique_results = []

    seen_chunks = set()

    for chunk in combined_results:

        chunk_text = chunk.get(
            "chunk",
            ""
        )

        if not chunk_text:
            continue

        if chunk_text not in seen_chunks:

            unique_results.append(
                chunk
            )

            seen_chunks.add(
                chunk_text
            )

    logger.info(
        f"Unique results: "
        f"{len(unique_results)}"
    )

    # =========================================
    # No Results
    # =========================================

    if not unique_results:

        return {
            "success": False,
            "message": (
                "No relevant content found "
                "in the selected PDF."
            ),
            "answer": "",
            "processing_time": round(
                time.time() - start_time,
                2
            ),
            "sources": []
        }

    # =========================================
    # Reranking
    # =========================================

    results = rerank_chunks(
        processed_question,
        unique_results
    )

    logger.info(
        f"Reranked results: "
        f"{len(results)}"
    )

    # =========================================
    # Limit Final Context
    # =========================================

    results = results[:TOP_K]

    logger.info(
        f"Final context chunks: "
        f"{len(results)}"
    )

    # =========================================
    # Log Context
    # =========================================

    for index, chunk in enumerate(
        results,
        start=1
    ):

        logger.info(
            f"Context chunk {index}: "
            f"{chunk.get('chunk', '')[:300]}"
        )

    # =========================================
    # Sources
    # =========================================

    sources = list(
        {
            chunk.get("source")
            for chunk in results
            if chunk.get("source")
        }
    )

    # =========================================
    # Generate Answer
    # =========================================

    # IMPORTANT:
    # Use ORIGINAL question for Gemini.
    # Processed question is only used
    # for retrieval.

    answer = generate_answer(
        original_question,
        results
    )

    logger.info(
        "answer generated successfully"
    )

    # =========================================
    # Processing Time
    # =========================================

    processing_time = round(
        time.time() - start_time,
        2
    )

    logger.info(
        f"RAG completed | "
        f"document_id={document_id} | "
        f"processing_time={processing_time}s"
    )

    # =========================================
    # Final Response
    # =========================================

    return {
        "success": True,
        "answer": answer,
        "processing_time": processing_time,
        "sources": sources
    }