from fastapi import APIRouter
from api.schemas import QueryRequest
from api.rag_pipeline import ask_rag
from fastapi import UploadFile, File
import shutil
from ingestion.loader import load_pdf
from ingestion.chunking import split_text
from services.embedding import get_embedding
from db.runtime_store import store
from db.faiss_index import add_to_faiss
from db.faiss_index import index
from utils.hashing import generate_file_hash
from datetime import datetime, timedelta

router = APIRouter()
@router.post("/ask")
def ask_question(request: QueryRequest):
    question = request.question
    result = ask_rag(question)
    return {
        "question": question,
        "answer": result['answer'],
        "processing_time":result['processing_time'],
        "sources": result['sources']
    }
@router.post("/upload")
def upload_pdf(
    file: UploadFile = File(...)
):
    file_path = f"uploaded_docs/{file.filename}"
    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )      
        
    # Generate content hash
    file_hash = generate_file_hash(file_path)
    # Duplicate content checking
    for record in store.records:

        if record["file_hash"] == file_hash:

            upload_time = datetime.fromisoformat(
            record["upload_time"]
        )

            if datetime.now() - upload_time < timedelta(days=15):

                return {
                "message": "Cached document reused",
                "filename": file.filename
            }
              
    # Load PDF text
    text = load_pdf(file_path)
    # Split text into chunks
    chunks = split_text(text)
    # Generate embeddings
    embeddings = get_embedding(chunks)
    # Add vectors into FAISS
    add_to_faiss(embeddings)
    # Store metadata records
    store.add_embedding(
        chunks,
        embeddings,
        file.filename,
        file_hash
    )
    return {
        "message": "PDF uploaded successfully",
        "filename": file.filename,
        "total_chunks": len(chunks),
        "faiss_vectors": index.ntotal,
        "metadata_records": len(store.records)
    }
    
    
@router.get("/documents")
def get_documents():  
    documents={}
    for record in store.records:
        document_name = record['document']
        if document_name not in documents:
            
            documents[document_name]={
                "document":document_name,
                "upload_time":record['upload_time'],
                "status":"Indexed"                }
           
    
    return list(documents.values())