import streamlit as st

def render_model_info(popup_placeholder):
    # Display the popup if show_popup is True
    if st.session_state.show_popup:
        with popup_placeholder.container():
            # Create two columns for the content and close button
            content_col, close_col = st.columns([11, 1])

            with content_col:
                st.markdown("""
                    <style>
                    .custom-warning {
                        background-color: #FFECB3;
                        border-left: 5px solid #FFA000;
                        padding: 10px;
                        margin-bottom: 10px;
                        font-size: 14px;
                    }
                    .custom-warning h4 {
                        color: #FFA000;
                        margin-top: 0;
                    }
                    </style>
                """, unsafe_allow_html=True)

                st.markdown("""
                    <div class="custom-warning">
                        <h4>MASTOPIA System Info</h4>
                        <p><strong>Statement of Purpose:</strong> MASTOPIA is intended to help intelligence analysts to summarize and draw conclusions from vast amounts of textual data.</p>
                        <p><strong>Suggested Use:</strong> Ask questions about the events that are described in the documents. MASTOPIA produces better responses to questions about documents' content than about meta-data of the dataset as a whole.</p>
                        <p><strong>Limitations:</strong> Large language models are known to sometimes produce factually incorrect responses that sound confident (also known as "hallucinations"). It is advised that you verify all claims made by the system's chatbot before including them in your report. Also, due to the size of the dataset, the agents cannot include all documents at once into their analysis. Thus, each of the system's responses will always be based only on a subset of the documents.</p>
                        <p><strong>Data used by the AI:</strong> The dataset that the AI has access to is comprised of 100 documents that describe the events in the fictional city of Vastopolis or provide relevant contextual information. These have been selected to give a comprehensive view of the situation and all stem from reliable sources.</p>
                        <p><strong>Training Data:</strong> The system's underlying large language model has been trained with large amounts of data from the internet. This allows it to process and analyze textual data, even if mentioned individuals, places, or events are fictional. The exact data used for training and validation have not been published by Open AI, the providers of the underlying model.</p>
                        <p><strong>Technical Details:</strong> MASTOPIA is a system that uses multiple agents powered by large language models to fulfil your requests. These have dedicated tasks and are moderated by a supervisor model that combines the individual responses into a single output. Both, the agents and the supervisor, use OpenAI's GPT-4 models. To reduce the input to the model the system automatically selects the documents most closely related to your question through a process called "retrieval-augmented generation". Only those are then considered when generating a response.</p>
                    </div>
                """, unsafe_allow_html=True)
