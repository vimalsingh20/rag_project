from datetime import datetime, timedelta
import json
import os
from utils.embedding_cache import save_embedding_cache
from db.faiss_index import rebuild_faiss_index

METADATA_PATH = "saved_index/records.json"
def is_expired(upload_time, days=7):
    upload_date = datetime.fromisoformat(upload_time)
    expiry_date = upload_date + timedelta(days=days)
    return datetime.now() > expiry_date
def cleanup_expired_records(store):
    valid_records = []
    expired_records = {}
    for record in store.records:
        if not is_expired(record["upload_time"]):

            valid_records.append(record)

        else:
            file_hash = record["file_hash"]
            if file_hash not in expired_records:
                expired_records[file_hash] = []
            expired_records[file_hash].append(record)
    for file_hash, records in expired_records.items():
        save_embedding_cache(file_hash,records)
    store.records = valid_records
    rebuild_faiss_index(store.records)
    with open(METADATA_PATH, "w") as file:
        json.dump(
            store.records,file,indent=4)

    print("\nExpired records archived and cleaned.")