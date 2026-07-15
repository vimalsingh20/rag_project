# RAG PDF Chatbot

A Retrieval-Augmented Generation (RAG) based PDF Chatbot that enables users to upload PDF documents and ask natural language questions. The application retrieves the most relevant document chunks using Hybrid Retrieval (FAISS + BM25) and generates context-aware responses using Google Gemini 2.5 Flash.

---

##  Features

-  Upload and manage PDF documents
-  Hybrid Retrieval (FAISS + BM25)
-  Semantic Search using Sentence Transformers
-  Google Gemini 2.5 Flash Integration
-  MySQL-based document and chunk storage
-  Per-document FAISS indexing
-  Embedding cache for duplicate documents
-  Prompt management
-  Logging and custom error handling
-  Streamlit frontend with FastAPI backend

---

##  Tech Stack

- Python
- FastAPI
- Streamlit
- FAISS
- Sentence Transformers
- Google Gemini API
- MySQL

---

##  Project Structure

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

##  Installation

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

## Future Improvements

- JWT Authentication
- Multi-user Support
- Chat History
- Conversation Memory
- Multiple LLM Support (Ollama, OpenAI, Groq)
- Docker Deployment
- CI/CD Pipeline

---

##  Version

**Current Release:** `v1.0`

---

## Author

**Vimal Singh**

B.Tech Computer Science Engineering
