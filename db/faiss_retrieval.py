import numpy as np
from db.faiss_index import index

from db.mysql_store import get_all_chunks
def faiss_retrieve(query_embedding,top_k=3):
    all_chunks = get_all_chunks()

    print("FAISS vectors:", index.ntotal)
    print("MySQL chunks:", len(all_chunks))
    query_array = np.array(
        [query_embedding],
        dtype=np.float32)
    distances, indices = index.search(
        query_array,
        top_k)
    results = []
    all_chunks = get_all_chunks()
    for idx, distance in zip(
        indices[0],distances[0]):
        if idx == -1:
            continue
        if idx >= len(all_chunks):

            print(f"Invalid index: {idx}")
            continue
        print(
            all_chunks[idx]["chunk"])
        results.append(
            all_chunks[idx])
    return results