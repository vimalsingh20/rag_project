from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends
)

from fastapi.responses import FileResponse

from api.schemas import QueryRequest
from api.rag_pipeline import ask_rag

import shutil
import os

from pathlib import Path

from datetime import datetime, timedelta

from pypdf import PdfReader

from ingestion.loader import load_pdf
from ingestion.chunking import split_text

from services.embedding import get_embedding

from db.faiss_index import FaissIndex

from config.settings import (
    UPLOAD_FOLDER,
    EMBEDDING_CACHE_FOLDER,
    CACHE_DAYS
)

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

from api.dependencies import get_current_user

from utils.hashing import generate_file_hash
from utils.logger import get_logger


logger = get_logger(__name__)

router = APIRouter()


# =========================================================
# Upload Security Configuration
# =========================================================

MAX_PDF_SIZE = 10 * 1024 * 1024  # 10 MB

ALLOWED_EXTENSION = ".pdf"

ALLOWED_CONTENT_TYPE = "application/pdf"


# =========================================================
# ASK QUESTION
# =========================================================

@router.post("/ask")
def ask_question(
    request: QueryRequest,
    current_user=Depends(get_current_user)
):

    try:

        user_id = current_user["user_id"]

        # =========================================
        # Get Chat Session
        # =========================================

        session = get_chat_session(
            request.session_id,
            user_id
        )

        if session is None:

            return {
                "success": False,
                "message": "Chat session not found."
            }

        # =========================================
        # Get Document From Session
        # =========================================

        document_id = session["document_id"]

        logger.info(
            f"Chat session | "
            f"session_id={request.session_id} | "
            f"document_id={document_id}"
        )

        # =========================================
        # Ask RAG About EXACT Document
        # =========================================

        result = ask_rag(
            request.question,
            user_id,
            document_id
        )

        # =========================================
        # Response Data
        # =========================================

        result["success"] = True

        result["question"] = (
            request.question
        )

        result["session_id"] = (
            request.session_id
        )

        result["document_id"] = (
            document_id
        )

        # =========================================
        # Save Chat Message
        # =========================================

        insert_chat_message(
            session_id=request.session_id,
            question=request.question,
            answer=result.get(
                "answer",
                ""
            ),
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


# =========================================================
# UPLOAD PDF
# =========================================================

@router.post("/upload")
def upload_pdf(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):

    try:

        # =========================================
        # User ID
        # =========================================

        user_id = current_user["user_id"]

        # =========================================
        # Validate Filename
        # =========================================

        if not file.filename:

            return {
                "success": False,
                "message": "Filename is required."
            }

        original_filename = Path(
            file.filename
        ).name

        # Prevent path traversal
        if original_filename != file.filename:

            return {
                "success": False,
                "message": "Invalid filename."
            }

        # =========================================
        # Validate Extension
        # =========================================

        if not original_filename.lower().endswith(
            ALLOWED_EXTENSION
        ):

            return {
                "success": False,
                "message": "Only PDF files are allowed."
            }

        # =========================================
        # Validate Content Type
        # =========================================

        if file.content_type != ALLOWED_CONTENT_TYPE:

            return {
                "success": False,
                "message": (
                    "Invalid file type. "
                    "Please upload a PDF."
                )
            }

        # =========================================
        # Validate File Size
        # =========================================

        file.file.seek(
            0,
            os.SEEK_END
        )

        file_size = file.file.tell()

        file.file.seek(0)

        if file_size == 0:

            return {
                "success": False,
                "message": "The uploaded PDF is empty."
            }

        if file_size > MAX_PDF_SIZE:

            return {
                "success": False,
                "message": (
                    "File too large. "
                    "Maximum allowed size is 10 MB."
                )
            }

        # =========================================
        # User-specific PDF Storage
        # =========================================

        user_upload_folder = os.path.join(
            UPLOAD_FOLDER,
            str(user_id)
        )

        os.makedirs(
            user_upload_folder,
            exist_ok=True
        )

        file_path = os.path.join(
            user_upload_folder,
            original_filename
        )

        # =========================================
        # Save Uploaded PDF
        # =========================================

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        # =========================================
        # Verify Actual PDF
        # =========================================

        try:

            reader = PdfReader(
                file_path
            )

            if len(reader.pages) == 0:

                os.remove(file_path)

                return {
                    "success": False,
                    "message": "PDF contains no pages."
                }

        except Exception as pdf_error:

            logger.warning(
                f"Invalid PDF uploaded: {pdf_error}"
            )

            if os.path.exists(file_path):

                os.remove(file_path)

            return {
                "success": False,
                "message": (
                    "Invalid or corrupted PDF file."
                )
            }

        # =========================================
        # Generate File Hash
        # =========================================

        file_hash = generate_file_hash(
            file_path
        )

        # =========================================
        # Check Existing Document For User
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

                # -----------------------------------------
                # Find Existing Chat Session
                # -----------------------------------------

                session = get_chat_session_by_document(
                    user_id=user_id,
                    document_id=document_id
                )

                # -----------------------------------------
                # Reuse Existing Session
                # -----------------------------------------

                if session:

                    session_id = session["id"]

                # -----------------------------------------
                # Safety Fallback
                # -----------------------------------------

                else:

                    session_id = create_chat_session(
                        user_id=user_id,
                        document_id=document_id,
                        title=original_filename
                    )

                # -----------------------------------------
                # Make Document Active
                # -----------------------------------------

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

                    "filename": original_filename,

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

        # =========================================
        # Prevent Empty PDF Text
        # =========================================

        if not chunks:

            if os.path.exists(file_path):

                os.remove(file_path)

            return {
                "success": False,
                "message": (
                    "Could not extract text "
                    "from the PDF."
                )
            }

        embeddings = get_embedding(
            chunks
        )

        # =========================================
        # Store Document
        # =========================================

        document_id = insert_document(
            user_id,
            original_filename,
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
            title=original_filename
        )

        # =========================================
        # Response
        # =========================================

        return {

            "success": True,

            "message": (
                "PDF uploaded successfully"
            ),

            "filename": original_filename,

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
                "Unable to upload document. "
                "Please try again."
            )
        }


# =========================================================
# GET UPLOADED DOCUMENTS
# =========================================================

@router.get("/documents")
def get_uploaded_documents(
    current_user=Depends(get_current_user)
):

    user_id = current_user["user_id"]

    return get_documents(
        user_id
    )


# =========================================================
# OPEN / VIEW DOCUMENT
# =========================================================

@router.get("/document/{filename}")
def open_document(
    filename: str,
    current_user=Depends(get_current_user)
):

    user_id = current_user["user_id"]

    # =========================================
    # Verify Document Belongs To User
    # =========================================

    document = get_document_by_filename(
        user_id,
        filename
    )

    if document is None:

        return {
            "success": False,
            "message": "Document not found"
        }

    # =========================================
    # User-specific PDF Path
    # =========================================

    file_path = os.path.join(
        UPLOAD_FOLDER,
        str(user_id),
        filename
    )

    if not os.path.exists(
        file_path
    ):

        return {
            "success": False,
            "message": "File not found"
        }

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=filename
    )


# =========================================================
# DELETE DOCUMENT
# =========================================================

@router.delete("/document/{filename}")
def delete_document(
    filename: str,
    current_user=Depends(get_current_user)
):

    try:

        user_id = current_user["user_id"]

        # =========================================
        # User-specific PDF Path
        # =========================================

        file_path = os.path.join(
            UPLOAD_FOLDER,
            str(user_id),
            filename
        )

        if not os.path.exists(
            file_path
        ):

            return {
                "success": False,
                "message": "File not found"
            }

        # =========================================
        # Get User's Document
        # =========================================

        document = get_document_by_filename(
            user_id,
            filename
        )

        if document is None:

            return {
                "success": False,
                "message": (
                    "Document not found in database."
                )
            }

        document_id = document["id"]

        file_hash = document["file_hash"]

        # =========================================
        # Delete PDF File
        # =========================================

        os.remove(
            file_path
        )

        # =========================================
        # Delete Embedding Cache
        # =========================================

        cache_file = (
            f"{EMBEDDING_CACHE_FOLDER}/"
            f"{file_hash}.json"
        )

        if os.path.exists(
            cache_file
        ):

            os.remove(
                cache_file
            )

        # =========================================
        # Delete FAISS Index
        # =========================================

        faiss_db = FaissIndex(
            document_id
        )

        faiss_db.delete_index()

        # =========================================
        # Delete Database Records
        # =========================================

        delete_document_by_id(
            document_id
        )

        return {

            "success": True,

            "message": (
                f"{filename} deleted successfully"
            )
        }

    except Exception as e:

        logger.error(
            f"Error deleting document: {e}"
        )

        return {

            "success": False,

            "message": (
                "Unable to delete document. "
                "Please try again."
            )
        }


# =========================================================
# GET CHAT SESSIONS
# =========================================================

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


# =========================================================
# GET CHAT HISTORY
# =========================================================

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

                "message": (
                    "Chat session not found."
                ),

                "messages": []
            }

        messages = get_chat_messages(
            session_id
        )

        return {

            "success": True,

            "session_id": session_id,

            "document_id": (
                session["document_id"]
            ),

            "messages": messages
        }

    except Exception as e:

        logger.error(
            f"Error fetching chat history: {e}"
        )

        return {

            "success": False,

            "message": (
                "Unable to load chat history."
            ),

            "messages": []
        }


# =========================================================
# CREATE NEW CHAT SESSION
# =========================================================

@router.post("/chat/sessions")
def create_new_chat_session(
    document_id: int,
    current_user=Depends(get_current_user)
):

    try:

        user_id = current_user["user_id"]

        # =========================================
        # Verify Document Belongs To User
        # =========================================

        documents = get_documents(
            user_id
        )

        document_exists = any(
            (
                doc.get("id")
                or doc.get("document_id")
            ) == document_id
            for doc in documents
        )

        if not document_exists:

            return {

                "success": False,

                "message": (
                    "Document not found."
                )
            }

        # =========================================
        # Create New Chat Session
        # =========================================

        session_id = create_chat_session(
            user_id=user_id,
            document_id=document_id,
            title="New Chat"
        )

        return {

            "success": True,

            "session_id": session_id,

            "document_id": document_id,

            "message": (
                "New chat created successfully."
            )
        }

    except Exception as e:

        logger.error(
            f"Error creating chat session: {e}"
        )

        return {

            "success": False,

            "message": (
                "Unable to create new chat."
            )
        }