import streamlit as st
import requests
st.set_page_config(
    page_title="RAG PDF Chatbot",
    layout="wide"
)

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

    if message == "Duplicate file detected":

        st.sidebar.success(
            "Document already available and ready for questions."
        )

    else:

        st.sidebar.success(message)
question = st.text_input(
    "Ask a question about the document"
)

if st.button("Get Answer"):
    with st.spinner("Generating answer..."):
        payload = {
            "question": question}
        response = requests.post(
            "http://127.0.0.1:8000/ask",
            json=payload
        )
        answer = response.json()['answer']
        st.session_state.chat_history.append(
            {
                "question": question,
                "answer": answer} )
for chat in st.session_state.chat_history:
    st.markdown("Question")
    st.info(chat["question"])
    st.markdown("Answer")
    st.success(chat["answer"])
          
    if "sources" in chat and chat["sources"]:

        st.markdown("Sources Used")

        for source in chat["sources"]:

            st.write(f"- {source}")   