from db.mysql_store import (
    get_expired_documents,
    delete_document_by_id
)

from db.faiss_index import (
    rebuild_faiss_index_from_mysql
)

def cleanup_expired_records():

    expired_documents = get_expired_documents()

    for document in expired_documents:

        delete_document_by_id(
            document["id"]
        )

    rebuild_faiss_index_from_mysql()

    print(
        "\nExpired documents cleaned."
    )