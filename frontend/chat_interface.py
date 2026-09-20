import streamlit as st

from frontend.api_client import ask_question


def show_chat_interface():

    st.sidebar.markdown("---")

    question = st.text_input(
        "Ask a question about the document"
    )

    if st.button("Get Answer"):

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            with st.spinner(
                "Generating answer..."
            ):

                try:

                    data = ask_question(
                        question
                    )

                    if data["success"]:

                        st.session_state.chat_history.append(
                            {
                                "question": question,
                                "answer": data["answer"],
                                "processing_time": data["processing_time"],
                                "sources": data["sources"]
                            }
                        )

                    else:

                        st.error(
                            data.get(
                                "message",
                                "Unable to process your question."
                            )
                        )

                except Exception:

                    st.error(
                        "Unable to connect to the server."
                    )

    # =========================================
    # Chat History
    # =========================================

    for chat in st.session_state.chat_history:

        st.markdown("Question")

        st.info(
            chat["question"]
        )

        st.markdown("Answer")

        st.success(
            chat["answer"]
        )

        st.caption(
            f"Response generated in "
            f"{chat['processing_time']} sec"
        )

        if chat["sources"]:

            st.markdown(
                "Sources Used"
            )

            for source in chat["sources"]:

                st.write(
                    source
                )