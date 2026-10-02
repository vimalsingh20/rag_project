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
    set_active_document,
    create_chat_session,
    get_chat_session,
    get_chat_sessions,
    insert_chat_message,
    get_chat_messages,
    get_chat_session_by_document


)

from fastapi import Depends
from api.dependencies import get_current_user

from utils.hashing import generate_file_hash

from utils.logger import get_logger


logger = get_logger(__name__)

router = APIRouter()


@router.post("/ask")
def ask_question(
    request: QueryRequest,
    current_user=Depends(get_current_user)
):

    try:

        user_id = current_user["user_id"]
        session = get_chat_session(
            request.session_id,
            user_id
        )

        if session is None:

            return {
                "success": False,
                "message": "Chat session not found."
            }
        result = ask_rag(
            request.question,
            user_id
        )

        result["success"] = True
        result["question"] = request.question
        result["session_id"] = request.session_id
        insert_chat_message(
            session_id=request.session_id,
            question=request.question,
            answer=result.get("answer", ""),
            processing_time=result.get(
                "processing_time",
                0
            ),
            sources=result.get(
                "sources",
                []
            )
        )

        return result

    except Exception as e:

        logger.error(
            f"Error processing question: {e}"
        )

        return {

            "success": False,

            "question": request.question,

            "answer": "",

            "message": (
                "Unable to process your request. "
                "Please try again."
            ),

            "processing_time": 0,

            "sources": []
        }
        
@router.post("/upload")
def upload_pdf(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):

    try:

        user_id = current_user["user_id"]

        # =========================================
        # Save uploaded PDF
        # =========================================

        file_path = f"{UPLOAD_FOLDER}/{file.filename}"

        with open(file_path, "wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        # =========================================
        # Generate file hash
        # =========================================

        file_hash = generate_file_hash(
            file_path
        )

        # =========================================
        # Check existing document for this user
        # =========================================

        document = get_document_by_hash(
            user_id,
            file_hash
        )

        # =========================================
        # Cached Document
        # =========================================

        if document:

            upload_time = document["upload_time"]

            if (
                datetime.now() - upload_time
                < timedelta(days=CACHE_DAYS)
            ):

                document_id = document["id"]

                # Find existing chat session
                session = get_chat_session_by_document(
                    user_id=user_id,
                    document_id=document_id
                )

                # Reuse existing session
                if session:

                    session_id = session["id"]

                # Safety fallback
                else:

                    session_id = create_chat_session(
                        user_id=user_id,
                        document_id=document_id,
                        title=file.filename
                    )

                # Make this document active
                clear_active_document(
                    user_id
                )

                set_active_document(
                    document_id
                )

                return {

                    "success": True,

                    "message": (
                        "Cached document reused"
                    ),

                    "filename": file.filename,

                    "document_id": document_id,

                    "session_id": session_id,

                    "cached": True
                }

        # =========================================
        # New Document Processing
        # =========================================

        text = load_pdf(
            file_path
        )

        chunks = split_text(
            text
        )

        embeddings = get_embedding(
            chunks
        )

        # =========================================
        # Store Document
        # =========================================

        document_id = insert_document(
            user_id,
            file.filename,
            file_hash,
            datetime.now()
        )

        # =========================================
        # Set Active Document
        # =========================================

        clear_active_document(
            user_id
        )

        set_active_document(
            document_id
        )

        # =========================================
        # Create FAISS Index
        # =========================================

        faiss_db = FaissIndex(
            document_id
        )

        faiss_db.load_or_create_index()

        faiss_db.add_embeddings(
            embeddings
        )

        # =========================================
        # Store Chunks
        # =========================================

        insert_chunks(
            document_id,
            chunks,
            embeddings
        )

        # =========================================
        # Create Chat Session
        # =========================================

        session_id = create_chat_session(
            user_id=user_id,
            document_id=document_id,
            title=file.filename
        )

        # =========================================
        # Response
        # =========================================

        return {

            "success": True,

            "message": (
                "PDF uploaded successfully"
            ),

            "filename": file.filename,

            "document_id": document_id,

            "session_id": session_id,

            "total_chunks": len(chunks),

            "faiss_vectors": (
                faiss_db.index.ntotal
            ),

            "metadata_records": (
                len(get_all_chunks())
            ),

            "cached": False
        }

    except Exception as e:

        logger.error(
            f"Error uploading PDF: {e}"
        )

        return {

            "success": False,

            "message": (
                "Unable to upload document."
            ),

            "error": str(e)
        }
@router.get("/documents")
def get_uploaded_documents(
    current_user = Depends(get_current_user)
):

    user_id = current_user["user_id"]

    return get_documents(user_id)

@router.get("/document/{filename}")
def open_document(
    filename: str,
    current_user = Depends(get_current_user)
):

    user_id = current_user["user_id"]

    document = get_document_by_filename(
        user_id,
        filename
    )

    if document is None:

        return {
            "success": False,
            "message": "Document not found"
        }

    file_path = f"{UPLOAD_FOLDER}/{filename}"

    if not os.path.exists(file_path):

        return {
            "success": False,
            "message": "File not found"
        }

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=filename
    )
   
   
@router.delete("/document/{filename}")
def delete_document(
    filename: str,
    current_user=Depends(get_current_user)
):

    try:

        user_id = current_user["user_id"]

        file_path = f"{UPLOAD_FOLDER}/{filename}"

        if not os.path.exists(file_path):
            return {
                "success": False,
                "message": "File not found"
            }

        document = get_document_by_filename(
            user_id,
            filename
        )

        if document is None:
            return {
                "success": False,
                "message": "Document not found in database."
            }

        document_id = document["id"]
        file_hash = document["file_hash"]

        # Delete PDF file
        os.remove(file_path)

        # Delete embedding cache
        cache_file = (
            f"{EMBEDDING_CACHE_FOLDER}/{file_hash}.json"
        )

        if os.path.exists(cache_file):
            os.remove(cache_file)

        # Delete FAISS index
        faiss_db = FaissIndex(document_id)
        faiss_db.delete_index()

        # Delete database records
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
        
        
@router.get("/chat/sessions/{document_id}")
def get_document_chat_sessions(
    document_id: int,
    current_user=Depends(get_current_user)
):

    user_id = current_user["user_id"]

    sessions = get_chat_sessions(
        user_id,
        document_id
    )

    return {
        "success": True,
        "sessions": sessions
    }
    
    
@router.get("/chat/history/{session_id}")
def get_chat_history(
    session_id: int,
    current_user=Depends(get_current_user)
):

    try:

        user_id = current_user["user_id"]

        session = get_chat_session(
            session_id,
            user_id
        )

        if session is None:

            return {
                "success": False,
                "message": "Chat session not found.",
                "messages": []
            }

        messages = get_chat_messages(
            session_id
        )

        return {
            "success": True,
            "session_id": session_id,
            "document_id": session["document_id"],
            "messages": messages
        }

    except Exception as e:

        logger.error(
            f"Error fetching chat history: {e}"
        )

        return {
            "success": False,
            "message": "Unable to load chat history.",
            "messages": []
        }