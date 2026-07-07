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
    type=["pdf"])

if uploaded_file is not None:
    files = {
        "file": uploaded_file}
    response = requests.post(
        "http://127.0.0.1:8000/upload",
        files=files)
    message = response.json()["message"]
    if message == "Cached document reused":

        st.sidebar.success(
            "Document already processed and reused from cache.")
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
            filename = doc["filename"]
            col1, col2 = st.sidebar.columns([4, 1])
            with col1:
                st.markdown(
                    f"[{filename}]"
                    f"(http://127.0.0.1:8000/document/{filename})"
                )
            with col2:
                if st.button(
                    "🗑",
                    key=f"delete_{filename}"
                ):
                    st.session_state[
                        f"confirm_delete_{filename}"
                    ] = True
            if st.session_state.get(f"confirm_delete_{filename}",False):
                st.sidebar.warning(
                    f"Delete {filename} ?")
                yes_col, no_col = st.sidebar.columns(2)

                with yes_col:
                    if st.button(
                        "Yes",
                        key=f"yes_{filename}"):

                        response = requests.delete(
                            f"http://127.0.0.1:8000/document/{filename}")

                        st.sidebar.success(
                            response.json()["message"])
                        st.rerun()

                with no_col:

                    if st.button(
                        "No",
                        key=f"no_{filename}"
                    ):

                        st.session_state[
                            f"confirm_delete_{filename}"
                        ] = False

                        st.rerun()
    else:
        st.sidebar.info(
            "No documents uploaded yet.")
except Exception as e:
    st.sidebar.error(
        f"Unable to load documents.{e}")

st.sidebar.markdown("---")
question = st.text_input(
    "Ask a question about the document")
if st.button("Get Answer"):
    with st.spinner(
        "Generating answer..."):

        payload = {
            "question": question}

        response = requests.post(
            "http://127.0.0.1:8000/ask",
            json=payload)

        data = response.json()

        if not data.get("success", True):
            st.warning(data["message"])
            st.stop()

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
        f"Response generated in "
        f"{chat['processing_time']} sec")
    if chat["sources"]:
        st.markdown(
            "Sources Used")
        for source in chat["sources"]:
            st.write(f"{source}")