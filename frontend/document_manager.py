import streamlit as st

from frontend.api_client import (
    upload_document,
    get_documents,
    delete_document,
    get_document_url
)


def show_document_manager():

    # =========================================
    # Upload Document
    # =========================================

    st.sidebar.header("Upload Document")

    uploaded_file = st.sidebar.file_uploader(
        "Upload PDF",
        type=["pdf"]
    )

    if uploaded_file is not None:

        try:

            data = upload_document(
                uploaded_file
            )

            if data.get("message") == "Cached document reused":

                st.sidebar.success(
                    "Document already processed "
                    "and reused from cache."
                )

            else:

                st.sidebar.success(
                    data.get(
                        "message",
                        "PDF uploaded successfully."
                    )
                )

        except Exception:

            st.sidebar.error(
                "Unable to upload document."
            )

    # =========================================
    # Clear Chat
    # =========================================

    if st.sidebar.button("Clear Chat"):

        st.session_state.chat_history = []

        st.rerun()

    # =========================================
    # Uploaded Documents
    # =========================================

    st.sidebar.markdown("---")

    st.sidebar.subheader(
        "Uploaded Documents"
    )

    try:

        documents = get_documents()

        if documents:

            for doc in documents:

                filename = doc["filename"]

                # ---------------------------------
                # Document + Delete Button
                # ---------------------------------

                col1, col2 = st.sidebar.columns(
                    [4, 1]
                )

                # Open document
                with col1:

                    document_url = get_document_url(
                        filename
                    )

                    st.markdown(
                        f"[{filename}]"
                        f"({document_url})"
                    )

                # Delete button
                with col2:

                    if st.button(
                        "🗑",
                        key=f"delete_{filename}"
                    ):

                        st.session_state[
                            f"confirm_delete_{filename}"
                        ] = True

                # ---------------------------------
                # Delete Confirmation
                # ---------------------------------

                if st.session_state.get(
                    f"confirm_delete_{filename}",
                    False
                ):

                    st.sidebar.warning(
                        f"Delete {filename}?"
                    )

                    yes_col, no_col = (
                        st.sidebar.columns(2)
                    )

                    # YES
                    with yes_col:

                        if st.button(
                            "Yes",
                            key=f"yes_{filename}"
                        ):

                            try:

                                data = delete_document(
                                    filename
                                )

                                if data.get("success"):

                                    st.sidebar.success(
                                        data.get(
                                            "message",
                                            "Document deleted successfully."
                                        )
                                    )

                                    st.session_state[
                                        f"confirm_delete_{filename}"
                                    ] = False

                                    st.rerun()

                                else:

                                    st.sidebar.error(
                                        data.get(
                                            "message",
                                            "Unable to delete document."
                                        )
                                    )

                            except Exception:

                                st.sidebar.error(
                                    "Unable to delete document."
                                )

                    # NO
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
                "No documents uploaded yet."
            )

    except Exception:

        st.sidebar.error(
            "Unable to load documents."
        )