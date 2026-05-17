import numpy as np 
from db.faiss_index import index 
from db.runtime_store import store

def faiss_retrieve(
    query_embedding,
    top_k=3
):
    
    query_array = np.array(
        [query_embedding],
        dtype = np.float32
    )
    distances, indices = index.search(query_array,top_k )
    print("\nFAISS INDICES:")
    print(indices)
    print("\nDISTANCES:")
    print(distances)
    results = []
    
    for idx, distance in zip(indices[0],distances[0]):
        if idx == -1:
            continue
        """if distance > 1.5:
            continue"""
        print("\nRetrieved Chunk:")
        print(store.records[idx]["chunk"])
        results.append(
            store.records[idx]
        )
    print("\nTOTAL RETRIEVED CHUNKS:")
    print(len(results))
    return results
