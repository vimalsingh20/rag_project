
from datetime import datetime



from db.mysql_store import (
    insert_document,
    insert_chunks
)




document_id = insert_document(
    "chat2.pdf",
    "hash555",
    datetime.now()
)

print(
    "Document ID:",
    document_id
)

chunks = [
    "vimal_singh",
    "sawan_singh",
    "rahul_tatrari"
]

insert_chunks(
    document_id,
    chunks
)