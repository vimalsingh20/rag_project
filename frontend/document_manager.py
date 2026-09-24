import streamlit as st

from frontend.api_client import (
    get_documents,
    get_document,
    delete_document
)


def show_document_manager():

    st.sidebar.header("Document Manager")

    # =========================================
    # Upload Document
    # =========================================

    uploaded_file = st.sidebar.file_uploader(
        "Upload PDF",
        type=["pdf"]
    )

    if uploaded_file is not None:

        from frontend.api_client import upload_document

        try:

            data = upload_document(
                uploaded_file
            )

            if data.get("message") == "Cached document reused":

                st.sidebar.success(
                    "Document already processed and reused from cache."
                )

            else:

                st.sidebar.success(
                    data.get(
                        "message",
                        "Document uploaded successfully."
                    )
                )

            st.rerun()

        except Exception:

            st.sidebar.error(
                "Unable to upload document."
            )

    st.sidebar.markdown("---")

    # =========================================
    # Uploaded Documents
    # =========================================

    st.sidebar.subheader("Uploaded Documents")

    try:

        documents = get_documents()

        if not documents:

            st.sidebar.info(
                "No documents uploaded yet."
            )

            return

        for doc in documents:

            filename = doc["filename"]

            # ---------------------------------
            # Document name
            # ---------------------------------

            st.sidebar.markdown(
                f"📄 **{filename}**"
            )

            col1, col2 = st.sidebar.columns(2)

            # =================================
            # VIEW PDF
            # =================================

            with col1:

                if st.button(
                    "👁 View",
                    key=f"view_{filename}"
                ):

                    try:

                        response = get_document(
                            filename
                        )

                        st.session_state[
                            "viewed_pdf"
                        ] = response.content

                        st.session_state[
                            "viewed_filename"
                        ] = filename

                        st.rerun()

                    except Exception:

                        st.sidebar.error(
                            "Unable to open PDF."
                        )

            # =================================
            # DELETE
            # =================================

            with col2:

                if st.button(
                    "🗑 Delete",
                    key=f"delete_{filename}"
                ):

                    st.session_state[
                        f"confirm_delete_{filename}"
                    ] = True

            # =================================
            # DELETE CONFIRMATION
            # =================================

            if st.session_state.get(
                f"confirm_delete_{filename}",
                False
            ):

                st.sidebar.warning(
                    f"Delete {filename}?"
                )

                yes_col, no_col = st.sidebar.columns(2)

                with yes_col:

                    if st.button(
                        "Yes",
                        key=f"yes_{filename}"
                    ):

                        try:

                            delete_document(
                                filename
                            )

                            st.session_state[
                                f"confirm_delete_{filename}"
                            ] = False

                            st.sidebar.success(
                                "Document deleted successfully."
                            )

                            st.rerun()

                        except Exception:

                            st.sidebar.error(
                                "Unable to delete document."
                            )

                with no_col:

                    if st.button(
                        "No",
                        key=f"no_{filename}"
                    ):

                        st.session_state[
                            f"confirm_delete_{filename}"
                        ] = False

                        st.rerun()

    except Exception:

        st.sidebar.error(
            "Unable to load documents."
        )


# =========================================
# PDF Viewer
# =========================================

def show_pdf_viewer():

    if "viewed_pdf" not in st.session_state:

        return

    if "viewed_filename" not in st.session_state:

        return

    filename = st.session_state[
        "viewed_filename"
    ]

    pdf_data = st.session_state[
        "viewed_pdf"
    ]

    st.markdown("---")

    st.subheader(
        f"📄 {filename}"
    )

    # =========================================
    # Download Button
    # =========================================

    st.download_button(
        label="⬇ Download PDF",
        data=pdf_data,
        file_name=filename,
        mime="application/pdf"
    )

    # =========================================
    # PDF Viewer
    # =========================================

    import base64

    pdf_base64 = base64.b64encode(
        pdf_data
    ).decode("utf-8")

    pdf_display = f"""
    <iframe
        src="data:application/pdf;base64,{pdf_base64}"
        width="100%"
        height="800"
        type="application/pdf">
    </iframe>
    """

    st.markdown(
        pdf_display,
        unsafe_allow_html=True
    )