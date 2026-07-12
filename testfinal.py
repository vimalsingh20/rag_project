from db.faiss_index import FaissIndex

obj = FaissIndex(15)

print(obj.document_id)
print(obj.index_dir)
print(obj.index_path)