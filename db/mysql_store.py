from db.mysql_db import get_connection
import json

from utils.logger import get_logger


logger = get_logger(__name__)

def insert_document(user_id, filename, file_hash, upload_time):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO documents
        (user_id, filename, file_hash, upload_time)
        VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (user_id, filename, file_hash, upload_time)
        )

        conn.commit()

        document_id = cursor.lastrowid

        return document_id

    except Exception as e:
        logger.info(f"Error inserting document: {e}")
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
        logger.info(
            f"{len(chunks)} chunks inserted successfully" )
    except Exception as e:
        logger.info(f"Error inserting chunks: {e}")
        raise
    finally:
        if conn:
            conn.close()
            
            
def get_documents(user_id):

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT *
        FROM documents
        WHERE user_id = %s
        """

        cursor.execute(
            query,
            (user_id,)
        )

        documents = cursor.fetchall()

        documents_list = []

        for document in documents:

            documents_list.append({
                "id": document["id"],
                "filename": document["filename"]
            })

        return documents_list

    except Exception as e:

        logger.info(f"Error Fetching documents: {e}")
        raise

    finally:

        if conn:
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

def get_document_by_hash(user_id, file_hash):

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT *
    FROM documents
    WHERE user_id = %s
    AND file_hash = %s
    """

    cursor.execute(
        query,
        (user_id, file_hash)
    )

    document = cursor.fetchone()

    conn.close()

    return document

def get_document_by_filename(user_id, filename):

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT *
    FROM documents
    WHERE user_id = %s
    AND filename = %s
    """

    cursor.execute(
        query,
        (user_id, filename)
    )

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
    
def has_documents(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT EXISTS(
        SELECT 1
        FROM documents
        WHERE user_id = %s
    )
    """

    cursor.execute(
        query,
        (user_id,)
    )

    result = cursor.fetchone()

    conn.close()

    return bool(result[0])
# clear active document
def clear_active_document(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    UPDATE documents
    SET is_active = FALSE
    WHERE user_id = %s
    """

    cursor.execute(
        query,
        (user_id,)
    )

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
def get_active_document(user_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT *
    FROM documents
    WHERE is_active = TRUE
    AND user_id = %s
    LIMIT 1
    """

    cursor.execute(
        query,
        (user_id,)
    )

    document = cursor.fetchone()

    conn.close()

    return document

def get_active_chunks(user_id):

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
    AND d.user_id = %s
    ORDER BY c.id
    """

    cursor.execute(
        query,
        (user_id,)
    )

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


# version 2 start -- authentication 

def create_user(name, email, password_hash):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO users
        (name, email, password_hash)
        VALUES (%s, %s, %s)
        """

        cursor.execute(
            query,
            (name, email, password_hash)
        )

        conn.commit()

        user_id = cursor.lastrowid

        return user_id

    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise

    finally:
        if conn:
            conn.close()


def get_user_by_email(email):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT *
        FROM users
        WHERE email = %s
        """

        cursor.execute(query, (email,))

        user = cursor.fetchone()

        return user

    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        raise

    finally:
        if conn:
            conn.close()