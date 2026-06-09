import faiss 
import numpy as np 
import os 
from db.mysql_store import get_all_embeddings
dimension = 384

INDEX_PATH = "saved_index/faiss.index"

if os.path.exists(INDEX_PATH):
    index = faiss.read_index(INDEX_PATH)
    
    print('\nFaiss index loaded sucessfully.')
    
else:
    index = faiss.IndexFlatL2(dimension)
    
    print("\nNew faiss index created.")
    
def add_to_faiss(embeddings):
    embedding_array = np.array(
        embeddings,
        dtype = np.float32
    )   
    index.add(embedding_array)
    faiss.write_index(
        index,
        INDEX_PATH
    ) 
    
    print("\nfaiss index saved")
    
def rebuild_faiss_index(records):
    global index
    dimension = 384
    index = faiss.IndexFlatL2(dimension)
    embeddings = []
    for record in records:
        embeddings.append(record["embedding"])
    if embeddings:
        embedding_array = np.array(
            embeddings,
            dtype=np.float32)

        index.add(embedding_array)
    faiss.write_index(index,INDEX_PATH )

    print("\nFAISS index rebuilt successfully.")    
    

def rebuild_faiss_index_from_mysql():
    global index
    index = faiss.IndexFlatL2(384)
    embeddings = get_all_embeddings()
    if embeddings:
        embedding_array = np.array(
            embeddings,
            dtype=np.float32
        )
        index.add(embedding_array)

    faiss.write_index(
        index,
        INDEX_PATH
    )

    print(
        "\nFAISS rebuilt from MySQL."
    )    