import faiss 
import numpy as np 
from services.embedding import get_embedding

chunks = [
    "NLP is natural language",
    "machine learning is used in ai",
    "deep learning uses neural network"
]

embedding = get_embedding(chunks)

embedding_array = np.array(embedding,dtype = np.float32)

dimension = embedding_array.shape[1]

print("Embedding dimension",dimension)

index = faiss.IndexFlatL2(dimension)

index.add(embedding_array)

print("Total vectors in index:",index.ntotal)

query = "what is nlp?"
query_embedding = get_embedding([query])
query_array = np.array(
    query_embedding ,
    dtype = np.float32
)

k = 2 
distances , indices = index.search(
    query_array,
    k
)

print("\n Nearest vector Id")

print(indices)

print("\nDistances")
print(distances)