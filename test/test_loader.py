from ingestion.loader import load_pdf
from ingestion.chunking import split_text
from services.embedding import get_embedding

from db.vector_store import VectorStore
from db.retrieval import retrive_chunks

from services.generator import generate_answer
# Step 1: Load PDF
text = load_pdf("data/sample.pdf")
print("text loaded sucessfully")
print("Text Length " ,len(text))

# Step 2: Chunking
chunks = split_text(text)
print("Chunks sucessfully")
print("Total chunks",len(chunks))

# Step 3:create  Embedding
embeddings = get_embedding(chunks)

print("Embeddings:", len(embeddings))
print("Vector size:", len(embeddings[0]))

# store embedding
store = VectorStore()

store .add_embedding(chunks,embeddings,'sample.pdf')

print('\n Embedding Stored Sucessfully')

# user query
query = "What is Basic NLP Preprocessing steps"

# queary embeddings
query_embedding = get_embedding([query])[0]
print("\n Query Embedding Created")

# strucutral Retrival 

results = retrive_chunks(
    query_embedding,
    store.get_records(),
    top_k =3,
    threshold=0.5
)

print("\n --- Retrieved Chunks --- \n")

for idx, result in enumerate(results, start=1):

    print(f"\nResult {idx}:\n")
    
    print ("Document:")
    print(result['document'])
    
    print("\n Chunk ID:")
    print(result['chunk_id'])
    
    print('\n Similarity Score :')
    print(result['chunk'])
    
    print("-" *50)
    
    print("\n --- Day 7 Structured Retrival test end ---")
    
    answer = generate_answer(query,results)
    
    print("\n === Final Answer ===")
    
    print(answer)     
