from db.keyword_retrieval import keyword_retrieve
from db.runtime_store import store

question = "what is deep learning"

results = keyword_retrieve(
    question,
    store.records,
    top_k=3
)

print("\nKEYWORD RETRIEVAL RESULTS:\n")

for idx, chunk in enumerate(results):

    print(f"\nRESULT {idx + 1}:\n")

    print(chunk["chunk"])