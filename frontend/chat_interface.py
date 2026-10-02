import streamlit as st

from frontend.api_client import (
    ask_question,
    get_chat_history
)


# =========================================
# Load Chat History
# =========================================

def load_chat_history(session_id):

    try:

        data = get_chat_history(
            session_id
        )

        if data.get("success"):

            st.session_state.chat_history = (
                data.get("messages", [])
            )

        else:

            st.session_state.chat_history = []

    except Exception as e:

        st.session_state.chat_history = []

        st.error(
            "Unable to load chat history."
        )


# =========================================
# Chat Interface
# =========================================

def show_chat_interface():

    # =========================================
    # Active Session
    # =========================================

    session_id = st.session_state.get(
        "active_session_id"
    )

    filename = st.session_state.get(
        "active_document_filename"
    )

    # =========================================
    # No Active Document
    # =========================================

    if not session_id:

        st.info(
            "Upload or select a PDF to start chatting."
        )

        return

    # =========================================
    # Current Document
    # =========================================

    if filename:

        st.subheader(
            f"💬 Chat — {filename}"
        )

    # =========================================
    # Load Chat History
    # =========================================

    history_loaded_for = st.session_state.get(
        "history_loaded_for"
    )

    if history_loaded_for != session_id:

        load_chat_history(
            session_id
        )

        st.session_state[
            "history_loaded_for"
        ] = session_id

    # =========================================
    # Ask Question
    # =========================================

    question = st.text_input(
        "Ask a question about the document",
        key="chat_question"
    )

    # =========================================
    # Get Answer
    # =========================================

    if st.button(
        "Get Answer",
        key="get_answer_button"
    ):

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

            return

        with st.spinner(
            "Generating answer..."
        ):

            try:

                # ---------------------------------
                # Get Active Session
                # ---------------------------------

                session_id = st.session_state.get(
                    "active_session_id"
                )

                if not session_id:

                    st.error(
                        "Please upload or select a PDF first."
                    )

                    return

                # ---------------------------------
                # Send Question To Backend
                # ---------------------------------

                data = ask_question(
                    question,
                    session_id
                )

                # ---------------------------------
                # Backend Error
                # ---------------------------------

                if not data.get("success"):

                    st.error(
                        data.get(
                            "message",
                            "Unable to process your question."
                        )
                    )

                    return

                # ---------------------------------
                # Success
                # ---------------------------------

                # Backend has already saved the message
                # into chat_messages table.
                #
                # Therefore we reload the history
                # instead of manually appending it.

                st.session_state[
                    "history_loaded_for"
                ] = None

                st.rerun()

            except Exception as e:

                st.error(
                    f"Unable to process your question: {str(e)}"
                )

    # =========================================
    # Chat History
    # =========================================

    chat_history = st.session_state.get(
        "chat_history",
        []
    )

    if not chat_history:

        st.info(
            "No conversation yet. Ask your first question."
        )

        return

    # =========================================
    # Display Conversation
    # =========================================
    
    for chat in reversed(chat_history):

        # -----------------------------------------
        # Question
        # -----------------------------------------

        st.markdown(
            "### Question"
        )

        st.info(
            chat.get(
                "question",
                ""
            )
        )

        # -----------------------------------------
        # Answer
        # -----------------------------------------

        st.markdown(
            "### Answer"
        )

        st.success(
            chat.get(
                "answer",
                ""
            )
        )

        # -----------------------------------------
        # Processing Time
        # -----------------------------------------

        processing_time = chat.get(
            "processing_time",
            0
        )

        st.caption(
            f"Response generated in "
            f"{processing_time} sec"
        )

        # -----------------------------------------
        # Sources
        # -----------------------------------------

        sources = chat.get(
            "sources",
            []
        )

        if sources:

            st.markdown(
                "**Sources Used**"
            )

            for source in sources:

                st.write(
                    source
                )