import streamlit as st
import requests

st.set_page_config(
    page_title="RAG PDF Chatbot",
    layout="wide")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
st.title("RAG PDF Chatbot")
st.sidebar.header("Upload Document")

if st.sidebar.button("Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()

uploaded_file = st.sidebar.file_uploader(
    "Upload PDF",
    type=["pdf"]
)

if uploaded_file is not None:

    files = {
        "file": uploaded_file
    }

    response = requests.post(
        "http://127.0.0.1:8000/upload",
        files=files
    )

    message = response.json()["message"]

    if message == "Cached document reused":

        st.sidebar.success(
            "Document already processed and reused from cache."
        )

    else:

        st.sidebar.success(message)
st.sidebar.markdown("---")
st.sidebar.subheader("Uploaded Documents")

try:

    documents_response = requests.get(
        "http://127.0.0.1:8000/documents")
    documents = documents_response.json()
    
    if documents:
        for doc in documents:

            st.sidebar.link_button(
                label = f"{doc['document']}",
                url = f"http://127.0.0.1:8000/document/{doc['document']}"
            )
    else:
        st.sidebar.info(
            "No documents uploaded yet."
        )
except Exception:
    st.sidebar.error(
        "Unable to load documents."
    )
st.sidebar.markdown("---")
question = st.text_input(
    "Ask a question about the document"
)
if st.button("Get Answer"):
    with st.spinner("Generating answer..."):
        payload = {
            "question": question
        }
        response = requests.post(
            "http://127.0.0.1:8000/ask",
            json=payload
        )
        
        data = response.json()
        answer = data["answer"]
        processing_time = data["processing_time"]
        sources = data["sources"]
        st.session_state.chat_history.append(
            {
                "question": question,
                "answer": answer,
                "processing_time": processing_time,
                "sources": sources
            }
        )
for chat in st.session_state.chat_history:
    st.markdown("Question")
    st.info(chat["question"])

    st.markdown("Answer")
    st.success(chat["answer"])
    st.caption(
        f"Response generated in {chat['processing_time']} sec"
    )

    if chat["sources"]:

        st.markdown("Sources Used")

        for source in chat["sources"]:

            st.write(f"{source}")