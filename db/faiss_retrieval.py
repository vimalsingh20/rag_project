import numpy as np
from db.faiss_index import index
from db.runtime_store import store

def faiss_retrieve(query_embedding,top_k=3):
    print("FAISS vectors:", index.ntotal)
    print("Store records:", len(store.records))
    query_array = np.array(
        [query_embedding],
        dtype=np.float32)
    distances, indices = index.search(
        query_array,
        top_k)
    results = []
    for idx, distance in zip(
        indices[0],distances[0]):
        if idx == -1:
            continue
        if idx >= len(store.records):

            print(f"Invalid index: {idx}")
            continue
        print(
            store.records[idx]["chunk"])
        results.append(
            store.records[idx])
    return results