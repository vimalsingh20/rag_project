from db.mysql_db import get_connection
import json
def insert_document(filename,file_hash,upload_time):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO documents
        (filename,file_hash,upload_time)
        VALUES (%s,%s,%s)
        """
        cursor.execute(query,(filename,file_hash,upload_time))
        conn.commit()
        document_id = cursor.lastrowid
        return document_id
    except Exception as e:
        print(f"Error inserting document: {e}")
        raise
    finally:
        if conn:
            conn.close()
            
            
def insert_chunks(document_id,chunks,embeddings):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO chunks
        (document_id,chunk_id,chunk_text,embedding)
        VALUES (%s,%s,%s,%s)
        """
        for idx, (chunk,embedding) in enumerate (zip (chunks,embeddings)):
            cursor.execute(query,(document_id,idx,chunk,json.dumps (embedding.tolist())))
        conn.commit()
        print(
            f"{len(chunks)} chunks inserted successfully" )
    except Exception as e:
        print(f"Error inserting chunks: {e}")
        raise
    finally:
        if conn:
            conn.close()
            
            
def get_documents():
    conn = None 
    try:
        conn = get_connection()
        cursor = conn.cursor()   
        query = """select * from documents"""     
        cursor.execute(query)   
        documents = cursor.fetchall()          
        documents_list =[]
        for i in documents:
            document = {
               "id": i[0],
               "filename": i[1]}
            documents_list.append(document)
        return documents_list
    except Exception as e:
        print(f"Error Fetching documents: {e}")  
        raise
    finally:
        if conn:
            conn.close()
            
            
from db.mysql_db import get_connection

def delete_document_from_db(filename):
    conn = get_connection()
    cursor = conn.cursor()
    query = """ DELETE FROM documents WHERE filename = %s"""
    cursor.execute(query,(filename,))
    conn.commit()
    print(f"{filename} deleted successfully")
    conn.close()
    
    
def get_all_chunks():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """SELECT *FROM chunks ORDER BY id """
    cursor.execute(query)
    rows = cursor.fetchall()
    chunks = []
    for row in rows:
        chunks.append({
            "chunk": row["chunk_text"],
            "chunk_id": row["chunk_id"],
            "document_id": row["document_id"]
        })
    conn.close()
    return chunks

def get_all_embeddings():

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT embedding
    FROM chunks
    WHERE embedding IS NOT NULL
    ORDER BY id
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    conn.close()

    embeddings = []

    for row in rows:

        embeddings.append(
            json.loads(
                row["embedding"]
            )
        )

    return embeddings


def get_document_by_hash(file_hash):

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT *
    FROM documents
    WHERE file_hash = %s
    """

    cursor.execute(query, (file_hash,))

    document = cursor.fetchone()

    conn.close()

    return document

def get_document_by_filename(filename):

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT *
    FROM documents
    WHERE filename = %s
    """

    cursor.execute(query, (filename,))

    document = cursor.fetchone()

    conn.close()

    return document


def get_expired_documents(days=30):

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT *
    FROM documents
    WHERE upload_time < NOW() - INTERVAL %s DAY
    """

    cursor.execute(query, (days,))
    documents = cursor.fetchall()
    conn.close()
    return documents


def delete_document_by_id(document_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM chunks WHERE document_id = %s",
        (document_id,))
    cursor.execute(
        "DELETE FROM documents WHERE id = %s",
        (document_id,))
    conn.commit()
    conn.close()
    
def has_documents():
    chunks = get_all_chunks()
    return len(chunks) > 0 

# clear active document
def clear_active_document():
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    UPDATE documents
    SET is_active = FALSE
    """

    cursor.execute(query)

    conn.commit()
    conn.close()
    
# set active document
def set_active_document(document_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    UPDATE documents
    SET is_active = TRUE
    WHERE id = %s
    """

    cursor.execute(query, (document_id,))

    conn.commit()
    conn.close()
    
# get active document
def get_active_document():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT *
    FROM documents
    WHERE is_active = TRUE
    LIMIT 1
    """

    cursor.execute(query)

    document = cursor.fetchone()

    conn.close()

    return document

def get_active_chunks():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT
        c.chunk_text,
        c.chunk_id,
        c.document_id
    FROM chunks c
    JOIN documents d
    ON c.document_id = d.id
    WHERE d.is_active = TRUE
    ORDER BY c.id
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    conn.close()

    chunks = []

    for row in rows:
        chunks.append({
            "chunk": row["chunk_text"],
            "chunk_id": row["chunk_id"],
            "document_id": row["document_id"]
        })

    return chunks           