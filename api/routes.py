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
from db.faiss_index import (rebuild_faiss_index_from_mysql)
from utils.hashing import generate_file_hash
from datetime import datetime, timedelta
from fastapi.responses import FileResponse
from db.mysql_store import (insert_document,insert_chunks)
from db.mysql_store import get_documents
from db.mysql_store import (delete_document_from_db)
from db.mysql_store import get_all_chunks
from db.mysql_store import (get_document_by_hash,get_document_by_filename)
import os 

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
    file: UploadFile = File(...)):
    file_path = f"uploaded_docs/{file.filename}"
    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer)
    # Generate content hash
    file_hash = generate_file_hash(file_path)
    # Duplicate content checking (MySQL)
    document = get_document_by_hash(file_hash)
    if document:
        upload_time = document["upload_time"]
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
        file_hash)
    # Store in MySQL
    try:
        print("Before MySQL Insert")
        document_id = insert_document(
            file.filename,
            file_hash,
            datetime.now())
        print("Document ID:", document_id)
        insert_chunks(document_id,chunks,embeddings)
        print("Chunks inserted")
    except Exception as e:
        print(
            f"MySQL Storage Error: {e}")
    return {
        "message": "PDF uploaded successfully",
        "filename": file.filename,
        "total_chunks": len(chunks),
        "faiss_vectors": index.ntotal,
        "metadata_records": len(get_all_chunks())
    }
"""@router.get("/documents")
def get_documents():  
    documents={}
    for record in store.records:
        document_name = record['document']
        if document_name not in documents:
            
            documents[document_name]={
                "document":document_name,
                "upload_time":record['upload_time'],
                "status":"Indexed"                }
           
    
    return list(documents.values())"""
    
    
@router.get("/documents")
def get_uploaded_documents():

    return get_documents()    


@router.get("/document/{filename}")
def open_document(filename: str):
    file_path = f"uploaded_docs/{filename}"
    print("Current Working Directory:", os.getcwd())
    print("Trying Path:", file_path)
    print("Exists:", os.path.exists(file_path))
    if not os.path.exists(file_path):
        return {"error":"File not found"}
    
    return FileResponse(path=file_path,
                        media_type="application/pdf",
                        filename=filename)
    
    

@router.delete("/document/{filename}")
def delete_document(filename: str):
    file_path = f"uploaded_docs/{filename}"
    if not os.path.exists(file_path):
        return {
            "message": "File not found"}
    document = get_document_by_filename(filename)
    file_hash = None
    if document:
        file_hash = document["file_hash"]
    os.remove(file_path)
    if file_hash:
        cache_file = (
            f"embedding_cache/{file_hash}.json")
        if os.path.exists(cache_file):
            os.remove(cache_file)
    delete_document_from_db(filename)
    rebuild_faiss_index_from_mysql()

    return {
        "message": f"{filename} deleted successfully"
    }