from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
from api.schemas import QueryRequest
from api.rag_pipeline import ask_rag
import shutil
import os
from datetime import datetime, timedelta
from ingestion.loader import load_pdf
from ingestion.chunking import split_text
from services.embedding import get_embedding
from db.faiss_index import FaissIndex

from config.settings import (UPLOAD_FOLDER,EMBEDDING_CACHE_FOLDER,CACHE_DAYS)

from db.mysql_store import (
    insert_document,
    insert_chunks,
    get_documents,
    delete_document_by_id,
    get_all_chunks,
    get_document_by_hash,
    get_document_by_filename,
    clear_active_document,
    set_active_document
)

from utils.hashing import generate_file_hash

from utils.logger import get_logger


logger = get_logger(__name__)

router = APIRouter()


@router.post("/ask")
def ask_question(request: QueryRequest):

    try:

        result = ask_rag(request.question)

        result["success"] = True
        result["question"] = request.question

        return result

    except Exception:

        return {
            "success": False,
            "question": request.question,
            "answer": "",
            "message": "Unable to process your request. Please try again.",
            "processing_time": 0,
            "sources": []
        }

@router.post("/upload")
def upload_pdf(file: UploadFile = File(...)):

    try:

        file_path = f"{UPLOAD_FOLDER}/{file.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_hash = generate_file_hash(file_path)

        document = get_document_by_hash(file_hash)

        if document:

            upload_time = document["upload_time"]

            if datetime.now() - upload_time < timedelta(days=CACHE_DAYS):

                return {
                    "success": True,
                    "message": "Cached document reused",
                    "filename": file.filename
                }

        text = load_pdf(file_path)

        chunks = split_text(text)

        embeddings = get_embedding(chunks)

        document_id = insert_document(
            file.filename,
            file_hash,
            datetime.now()
        )

        clear_active_document()

        set_active_document(document_id)

        faiss_db = FaissIndex(document_id)

        faiss_db.load_or_create_index()

        faiss_db.add_embeddings(embeddings)

        insert_chunks(
            document_id,
            chunks,
            embeddings
        )

        return {

            "success": True,
            "message": "PDF uploaded successfully",
            "filename": file.filename,
            "total_chunks": len(chunks),
            "faiss_vectors": faiss_db.index.ntotal,
            "metadata_records": len(get_all_chunks())
        }

    except Exception as e:

        return {

            "success": False,
            "message": "Unable to upload document.",
            "error": str(e)
        }

@router.get("/documents")
def get_uploaded_documents():

    return get_documents()


@router.get("/document/{filename}")
def open_document(filename: str):

    file_path = f"uploaded_docs/{filename}"

    if not os.path.exists(file_path):

        return {
            "success":False,
            "message":"File not found"
        }

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=filename
    )

@router.delete("/document/{filename}")
def delete_document(filename: str):

    try:

        file_path = f"uploaded_docs/{filename}"

        if not os.path.exists(file_path):

            return {
                "success": False,
                "message": "File not found"
            }

        document = get_document_by_filename(filename)

        if document is None:

            return {
                "success": False,
                "message": "Document not found in database."
            }

        document_id = document["id"]

        file_hash = document["file_hash"]

        os.remove(file_path)

        cache_file = (
    f"{EMBEDDING_CACHE_FOLDER}/{file_hash}.json"
)

        if os.path.exists(cache_file):

            os.remove(cache_file)

        faiss_db = FaissIndex(document_id)

        faiss_db.delete_index()

        delete_document_by_id(document_id)

        return {

            "success": True,
            "message": f"{filename} deleted successfully"
        }

    except Exception as e:

        return {

            "success": False,
            "message": "Unable to delete document.",
            "error": str(e)
        }