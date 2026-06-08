from db.mysql_db import get_connection

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
def insert_chunks(document_id,chunks):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO chunks
        (document_id,chunk_id,chunk_text)
        VALUES (%s,%s,%s)
        """
        for idx, chunk in enumerate(chunks):
            cursor.execute(query,(document_id,idx,chunk))
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