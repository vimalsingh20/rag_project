# RAG PDF Chatbot

A Retrieval-Augmented Generation (RAG) based chatbot that allows users to upload PDF documents and ask questions in natural language.

The application uses Hybrid Retrieval (FAISS + BM25) along with Google Gemini 2.5 Flash to generate accurate and context-aware responses from uploaded documents.

---

## Features

### Document Processing

- Upload PDF documents
- Extract text from PDF files
- Split documents into chunks
- Generate embeddings using Sentence Transformers
- Store documents and chunks in MySQL
- Per-document FAISS indexing
- Embedding cache for duplicate documents
- Delete uploaded documents
- Active document management

### Hybrid Retrieval

- Semantic Search using FAISS
- Keyword Search using BM25
- Hybrid retrieval combining FAISS and BM25 results
- Duplicate chunk removal
- Reranking of retrieved chunks
- Context-aware answer generation

### LLM Integration

- Google Gemini 2.5 Flash
- Prompt-based answer generation
- Query preprocessing
- Source information in responses

### Authentication & Security

- User registration
- User login
- Password hashing using Argon2
- JWT-based authentication
- Access token
- Refresh token
- Protected API endpoints
- User-specific document access
- User-specific document upload
- User-specific document deletion
- User-specific RAG question answering

### Frontend

- Streamlit frontend
- Modular frontend architecture
- Login and registration interface
- PDF upload interface
- Document management interface
- Chat interface
- Chat history during the current session

### Backend

- FastAPI REST API
- MySQL database integration
- FAISS vector search
- BM25 retrieval
- Logging
- Custom error handling

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Core programming language |
| FastAPI | Backend API |
| Streamlit | Frontend |
| MySQL | Database |
| FAISS | Vector similarity search |
| BM25 | Keyword-based retrieval |
| Sentence Transformers | Text embeddings |
| Google Gemini 2.5 Flash | Answer generation |
| JWT | Authentication |
| Argon2 | Password hashing |

---
