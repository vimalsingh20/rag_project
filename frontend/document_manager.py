import streamlit as st

from frontend.api_client import (
    get_documents,
    get_document,
    delete_document,
    upload_document,
    get_chat_sessions
)


# =========================================================
# HELPERS
# =========================================================

def clear_pdf_viewer():

    st.session_state["viewed_pdf"] = None
    st.session_state["viewed_filename"] = None


def clear_active_document():

    st.session_state["active_document_id"] = None

    st.session_state[
        "active_document_filename"
    ] = None

    st.session_state[
        "active_session_id"
    ] = None

    st.session_state[
        "chat_history"
    ] = []

    st.session_state[
        "history_loaded_for"
    ] = None


def normalize_documents(data):

    if isinstance(data, list):

        return data

    if isinstance(data, dict):

        return data.get(
            "documents",
            []
        )

    return []


# =========================================================
# SET ACTIVE DOCUMENT
# =========================================================

def set_active_document(doc):

    document_id = (
        doc.get("id")
        or doc.get("document_id")
    )

    filename = doc.get(
        "filename",
        ""
    )

    # -----------------------------------------
    # Active document
    # -----------------------------------------

    st.session_state[
        "active_document_id"
    ] = document_id

    st.session_state[
        "active_document_filename"
    ] = filename

    # -----------------------------------------
    # Reset chat state
    # -----------------------------------------

    st.session_state[
        "active_session_id"
    ] = None

    st.session_state[
        "chat_history"
    ] = []

    st.session_state[
        "history_loaded_for"
    ] = None

    # -----------------------------------------
    # Find existing session
    # -----------------------------------------

    try:

        data = get_chat_sessions(
            document_id
        )

        if isinstance(data, dict):

            sessions = data.get(
                "sessions",
                []
            )

        elif isinstance(data, list):

            sessions = data

        else:

            sessions = []

        if sessions:

            first_session = sessions[0]

            if isinstance(
                first_session,
                dict
            ):

                session_id = (
                    first_session.get("id")
                    or first_session.get(
                        "session_id"
                    )
                )

            else:

                session_id = first_session

            st.session_state[
                "active_session_id"
            ] = session_id

    except Exception:

        st.session_state[
            "active_session_id"
        ] = None


# =========================================================
# LOAD PDF FOR VIEW
# =========================================================

def load_pdf_for_view(doc):

    filename = doc.get(
        "filename",
        ""
    )

    if not filename:

        return False

    try:

        response = get_document(
            filename
        )

        response.raise_for_status()

        # -----------------------------------------
        # Remove previous PDF first
        # -----------------------------------------

        clear_pdf_viewer()

        # -----------------------------------------
        # Load selected PDF
        # -----------------------------------------

        st.session_state[
            "viewed_pdf"
        ] = response.content

        st.session_state[
            "viewed_filename"
        ] = filename

        return True

    except Exception:

        clear_pdf_viewer()

        return False


# =========================================================
# DOCUMENT MANAGER
# =========================================================

def show_document_manager():

    st.sidebar.header(
        "Document Manager"
    )

    # =====================================================
    # SELECT PDF
    # =====================================================

    uploaded_file = st.sidebar.file_uploader(
        "Upload PDF",
        type=["pdf"],
        key="pdf_uploader"
    )

    # =====================================================
    # UPLOAD BUTTON
    # =====================================================

    if st.sidebar.button(
        "Upload PDF",
        key="upload_pdf_button"
    ):

        if uploaded_file is None:

            st.sidebar.warning(
                "Please select a PDF first."
            )

        else:

            try:

                with st.sidebar.spinner(
                    "Uploading PDF..."
                ):

                    data = upload_document(
                        uploaded_file
                    )

                # =================================================
                # UPLOAD SUCCESS
                # =================================================

                if data.get(
                    "success",
                    False
                ):

                    st.sidebar.success(
                        data.get(
                            "message",
                            "PDF uploaded successfully."
                        )
                    )

                    # =============================================
                    # IMPORTANT:
                    # Uploaded document becomes ACTIVE for CHAT
                    # =============================================

                    st.session_state[
                        "active_document_id"
                    ] = data.get(
                        "document_id"
                    )

                    st.session_state[
                        "active_document_filename"
                    ] = data.get(
                        "filename",
                        uploaded_file.name
                    )

                    st.session_state[
                        "active_session_id"
                    ] = data.get(
                        "session_id"
                    )

                    # =============================================
                    # Reset chat history
                    # =============================================

                    st.session_state[
                        "chat_history"
                    ] = []

                    st.session_state[
                        "history_loaded_for"
                    ] = None

                    # =============================================
                    # IMPORTANT:
                    # DO NOT automatically open PDF
                    # =============================================

                    clear_pdf_viewer()

                    st.rerun()

                else:

                    st.sidebar.error(
                        data.get(
                            "message",
                            "Unable to upload PDF."
                        )
                    )

            except Exception as e:

                st.sidebar.error(
                    f"Unable to upload PDF: {e}"
                )

    st.sidebar.markdown("---")

    # =====================================================
    # UPLOADED DOCUMENTS
    # =====================================================

    st.sidebar.subheader(
        "Uploaded Documents"
    )

    try:

        documents_data = get_documents()

        documents = normalize_documents(
            documents_data
        )

    except Exception:

        st.sidebar.error(
            "Unable to load documents."
        )

        return

    # =====================================================
    # NO DOCUMENTS
    # =====================================================

    if not documents:

        st.sidebar.info(
            "No documents uploaded yet."
        )

        return

    # =====================================================
    # DOCUMENT LIST
    # =====================================================

    for doc in documents:

        document_id = (
            doc.get("id")
            or doc.get("document_id")
        )

        filename = doc.get(
            "filename",
            "Unknown"
        )

        # -----------------------------------------
        # Document name
        # -----------------------------------------

        st.sidebar.markdown(
            f"📄 **{filename}**"
        )

        # -----------------------------------------
        # Active document
        # -----------------------------------------

        if (
            st.session_state.get(
                "active_document_id"
            )
            == document_id
        ):

            st.sidebar.caption(
                "🟢 Active document"
            )

        # =================================================
        # BUTTONS
        # =================================================

        col1, col2, col3 = (
            st.sidebar.columns(
                [1, 1, 1]
            )
        )

        # =================================================
        # CHAT
        # =================================================

        with col1:

            if st.button(
                "💬 Chat",
                key=f"chat_{document_id}"
            ):

                set_active_document(
                    doc
                )

                # -----------------------------------------
                # Chat mode should hide PDF
                # -----------------------------------------

                clear_pdf_viewer()

                st.rerun()

        # =================================================
        # VIEW
        # =================================================

        with col2:

            if st.button(
                "👁 View",
                key=f"view_{document_id}"
            ):

                # -----------------------------------------
                # Make selected document active
                # -----------------------------------------

                set_active_document(
                    doc
                )

                # -----------------------------------------
                # Open ONLY when View is clicked
                # -----------------------------------------

                success = load_pdf_for_view(
                    doc
                )

                if not success:

                    st.sidebar.error(
                        "Unable to open PDF."
                    )

                st.rerun()

        # =================================================
        # DELETE
        # =================================================

        with col3:

            if st.button(
                "🗑 Delete",
                key=f"delete_{document_id}"
            ):

                st.session_state[
                    f"confirm_delete_{document_id}"
                ] = True

        # =================================================
        # DELETE CONFIRMATION
        # =================================================

        if st.session_state.get(
            f"confirm_delete_{document_id}",
            False
        ):

            st.sidebar.warning(
                f"Delete {filename}?"
            )

            yes_col, no_col = (
                st.sidebar.columns(2)
            )

            # ---------------------------------------------
            # YES
            # ---------------------------------------------

            with yes_col:

                if st.button(
                    "Yes",
                    key=f"yes_{document_id}"
                ):

                    try:

                        delete_document(
                            filename
                        )

                        st.session_state[
                            f"confirm_delete_{document_id}"
                        ] = False

                        # ---------------------------------
                        # Clear active document
                        # ---------------------------------

                        if (
                            st.session_state.get(
                                "active_document_id"
                            )
                            == document_id
                        ):

                            clear_active_document()

                        # ---------------------------------
                        # Clear viewed PDF
                        # ---------------------------------

                        if (
                            st.session_state.get(
                                "viewed_filename"
                            )
                            == filename
                        ):

                            clear_pdf_viewer()

                        st.sidebar.success(
                            "Document deleted successfully."
                        )

                        st.rerun()

                    except Exception as e:

                        st.sidebar.error(
                            f"Unable to delete document: {e}"
                        )

            # ---------------------------------------------
            # NO
            # ---------------------------------------------

            with no_col:

                if st.button(
                    "No",
                    key=f"no_{document_id}"
                ):

                    st.session_state[
                        f"confirm_delete_{document_id}"
                    ] = False

                    st.rerun()


# =========================================================
# PDF VIEWER
# =========================================================

def show_pdf_viewer():

    pdf_data = st.session_state.get(
        "viewed_pdf"
    )

    filename = st.session_state.get(
        "viewed_filename"
    )

    # =====================================================
    # NOTHING TO VIEW
    # =====================================================

    if not pdf_data or not filename:

        return

    st.markdown("---")

    # =====================================================
    # PDF TITLE
    # =====================================================

    st.subheader(
        f"📄 {filename}"
    )

    # =====================================================
    # DOWNLOAD
    # =====================================================

    st.download_button(
        label="⬇ Download PDF",
        data=pdf_data,
        file_name=filename,
        mime="application/pdf",
        key=f"download_pdf_{filename}"
    )

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

    # =====================================================
    # PDF VIEWER
    # =====================================================

    try:

        st.pdf(
            pdf_data,
            height=850
        )

    except Exception as e:

        st.error(
            f"Unable to display PDF: {e}"
        )