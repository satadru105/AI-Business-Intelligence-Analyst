import streamlit as st

from modules.ai_analyst import answer_question


def render_ai_chat_assistant(df):

    st.markdown("---")

    st.header("🤖 AI Analyst Chat Assistant")

    st.write(
        "Ask questions about your business data and get "
        "AI-powered analyst insights."
    )

    # ---------------------------------------------------------
    # Example questions
    # ---------------------------------------------------------

    st.subheader("💬 Example Questions")

    example_questions = [
        "What is the overall business performance?",
        "Which region is performing best?",
        "Which region is performing worst?",
        "What are the major business anomalies?",
        "Which products need attention?",
        "What recommendations should management follow?",
    ]

    cols = st.columns(3)

    for i, question in enumerate(example_questions):

        with cols[i % 3]:

            if st.button(
                question,
                key=f"example_question_{i}",
                use_container_width=True
            ):

                st.session_state[
                    "selected_chat_question"
                ] = question

    # ---------------------------------------------------------
    # Question input
    # ---------------------------------------------------------

    default_question = st.session_state.get(
        "selected_chat_question",
        ""
    )

    question = st.text_input(
        "Ask the AI Analyst",
        value=default_question,
        placeholder="Example: Why did sales decrease?",
        key="ai_chat_question"
    )

    # ---------------------------------------------------------
    # Ask button
    # ---------------------------------------------------------

    if st.button(
        "🤖 Ask AI Analyst",
        type="primary",
        use_container_width=True,
        key="ask_ai_analyst"
    ):

        if not question.strip():

            st.warning(
                "⚠️ Please enter a question first."
            )

            return

        with st.spinner(
            "🤖 AI Analyst is analyzing your business data..."
        ):

            try:

                answer = answer_question(
                    df,
                    question
                )

                st.session_state[
                    "last_ai_question"
                ] = question

                st.session_state[
                    "last_ai_answer"
                ] = answer

            except Exception as e:

                st.error(
                    f"❌ AI Analyst error: {e}"
                )

    # ---------------------------------------------------------
    # Display answer
    # ---------------------------------------------------------

    if "last_ai_answer" in st.session_state:

        st.markdown("---")

        st.subheader("🧠 AI Analyst Response")

        st.info(
            st.session_state["last_ai_answer"]
        )

        st.caption(
            f"Question: "
            f"{st.session_state.get('last_ai_question', '')}"
        )