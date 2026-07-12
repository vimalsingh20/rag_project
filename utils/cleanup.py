from db.mysql_store import (
    get_expired_documents,
    delete_document_by_id
)

from db.faiss_index import FaissIndex


def cleanup_expired_records():

    expired_documents = get_expired_documents()

    for document in expired_documents:

        faiss_db = FaissIndex(document["id"])

        faiss_db.delete_index()

        delete_document_by_id(
            document["id"]
        )

    print("\nExpired documents cleaned.")