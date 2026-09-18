import os
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

LLM_MODEL = "models/gemini-2.5-flash"

CHUNK_SIZE = 300
CHUNK_OVERLAP = 50

TOP_K = 3

FAISS_DIMENSION = 384

CACHE_DAYS = 15

UPLOAD_FOLDER = "uploaded_docs"
EMBEDDING_CACHE_FOLDER = "embedding_cache"
VECTOR_INDEX_FOLDER = "saved_index/vector_indexes"

GOOGLE_API_ENV = "GOOGLE_API_KEY"


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
)

REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 15)
)