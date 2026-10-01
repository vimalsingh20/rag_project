import base64

import streamlit as st

from frontend.api_client import (
    get_documents,
    get_document,
    delete_document,
    upload_document
)


# =========================================
# Document Manager
# =========================================

def show_document_manager():

    st.sidebar.header("Document Manager")

    # =========================================
    # Upload Document
    # =========================================

    uploaded_file = st.sidebar.file_uploader(
        "Upload PDF",
        type=["pdf"],
        key="pdf_uploader"
    )

    if uploaded_file is not None:

        if st.sidebar.button(
            "Upload PDF",
            key="upload_pdf_button"
        ):

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

    st.sidebar.subheader(
        "Uploaded Documents"
    )

    try:

        documents = get_documents()

        if not documents:

            st.sidebar.info(
                "No documents uploaded yet."
            )

            return

        for doc in documents:

            filename = doc["filename"]

            # =================================
            # Document Name
            # =================================

            st.sidebar.markdown(
                f"📄 **{filename}**"
            )

            col1, col2 = st.sidebar.columns(
                [1, 1]
            )

            # =================================
            # View PDF
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
            # Delete PDF
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
            # Delete Confirmation
            # =================================

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

                # ---------------------------------
                # Confirm Delete
                # ---------------------------------

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

                            # Remove currently viewed PDF
                            if (
                                st.session_state.get(
                                    "viewed_filename"
                                ) == filename
                            ):

                                st.session_state.pop(
                                    "viewed_pdf",
                                    None
                                )

                                st.session_state.pop(
                                    "viewed_filename",
                                    None
                                )

                            st.sidebar.success(
                                "Document deleted successfully."
                            )

                            st.rerun()

                        except Exception:

                            st.sidebar.error(
                                "Unable to delete document."
                            )

                # ---------------------------------
                # Cancel Delete
                # ---------------------------------

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
    # Download PDF
    # =========================================

    st.download_button(
        label="⬇ Download PDF",
        data=pdf_data,
        file_name=filename,
        mime="application/pdf",
        key=f"download_{filename}"
    )

    # =========================================
    # PDF Viewer
    # =========================================

    import base64

    pdf_base64 = base64.b64encode(
        pdf_data
    ).decode("utf-8")

    pdf_html = f"""
    <html>
    <body style="margin:0; padding:0;">

        <iframe
            id="pdfViewer"
            width="100%"
            height="800px"
            style="border:none;">
        </iframe>

        <script>

            const base64Data = "{pdf_base64}";

            const byteCharacters = atob(base64Data);

            const byteNumbers = new Array(
                byteCharacters.length
            );

            for (
                let i = 0;
                i < byteCharacters.length;
                i++
            ) {{
                byteNumbers[i] =
                    byteCharacters.charCodeAt(i);
            }}

            const byteArray = new Uint8Array(
                byteNumbers
            );

            const blob = new Blob(
                [byteArray],
                {{
                    type: "application/pdf"
                }}
            );

            const pdfUrl =
                URL.createObjectURL(blob);

            document
                .getElementById("pdfViewer")
                .src = pdfUrl;

        </script>

    </body>
    </html>
    """

    import streamlit.components.v1 as components

    components.html(
        pdf_html,
        height=820,
        scrolling=False
    )