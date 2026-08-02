
# RAG PDF Chatbot

A Retrieval-Augmented Generation (RAG) based chatbot that allows users to upload PDF documents and ask questions in natural language. The application combines Hybrid Retrieval (FAISS + BM25) with Google Gemini 2.5 Flash to generate accurate and context-aware responses.

---

## Features

- Upload and manage PDF documents
- Hybrid Retrieval (FAISS + BM25)
- Semantic Search using Sentence Transformers
- Google Gemini 2.5 Flash integration
- MySQL-based document and chunk storage
- Per-document FAISS indexing
- Embedding cache for duplicate documents
- Prompt management
- Logging and custom error handling
- FastAPI backend with Streamlit frontend

---

## Tech Stack

- Python
- FastAPI
- Streamlit
- MySQL
- FAISS
- BM25
- Sentence Transformers
- Google Gemini 2.5 Flash

---

## Project Structure

```text
rag_project/
│── api/
│── config/
│── db/
│── ingestion/
│── prompts/
│── services/
│── utils/
│── streamlit_app.py
│── requirements.txt
│── README.md
```

---

## Installation

```bash
git clone <repository-url>
cd rag_project
pip install -r requirements.txt
```

---

## Run the Application

### Start FastAPI

```bash
uvicorn api.app:app --reload
```

### Start Streamlit

```bash
streamlit run streamlit_app.py
```

---

## Roadmap

### Version 1.0
- Hybrid Retrieval (FAISS + BM25)
- Google Gemini Integration
- MySQL Storage
- Per-document FAISS Index
- Streamlit + FastAPI Architecture

### Version 2.0 (Planned)
- User Authentication
- Multi-user Support
- Chat History
- Conversation Memory
- Multiple LLM Support (Gemini + Ollama)
- Improved UI/UX
- Docker Deployment
- RAG Evaluation Framework

---

## Current Status

- Version 1.0 Released
- Version 2.0 In Development

---

## Author

**Vimal Singh**

B.Tech Computer Science Engineering