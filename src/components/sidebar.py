import os
import json
import streamlit as st
import re
from datetime import datetime
from streamlit_extras.stylable_container import stylable_container 

def highlight_match(match):
    original_text = match.group()
    return f":red[{original_text}]"


# Implement the search_documents function
def search_documents(query):
    # Get the path to the JSON file
    file_path = os.path.join(os.getcwd(), "dataset", "faiss_index_high.json")
    
    # Load the JSON data
    with open(file_path, "r") as json_file:
        data_dict = json.load(json_file)

    relevant_documents = []

    for doc_id, doc_content in data_dict.items():
        title = doc_content['title']
        date = doc_content['date']
        content = doc_content['content']

        # if query.lower() in doc_id.lower() + title.lower() + date.lower() + content.lower():
        if re.search(query, doc_id, re.IGNORECASE) or re.search(query, title, re.IGNORECASE) or re.search(query, date, re.IGNORECASE) or re.search(query, content, re.IGNORECASE):
            highlighted_title = re.sub(query, highlight_match, title, flags=re.IGNORECASE)
            highlighted_doc_id = re.sub(query, highlight_match, doc_id, flags=re.IGNORECASE)
            relevant_documents.append({"id": highlighted_doc_id, "title": highlighted_title, "date": date, "content": content})

    
    if relevant_documents:
        for _, doc in enumerate(relevant_documents):
            # Generate a unique key for each expander using index
            with st.expander(f"{doc['id']}: {doc['title']}", expanded=False):
                st.write(f"Document ID: {doc['id']}")
                st.write(f"Title: {doc['title']}")
                st.write(f"Date: {doc['date']}")
                st.text_area(
                    label = "Document Content", 
                    value = f"{doc['content']}",
                    disabled = True,
                    height = 500
                )
    else:
        st.text("No relevant documents found.")

    # return ""
    

def reset_prompt():
    config = st.session_state.config
    st.session_state.general_prompt = config.prompts['general']
    st.session_state.supervisor_prompt = config.prompts['supervisor']
    st.session_state.retriever_prompt = config.get_retriever_config(st.session_state.version)['prompt']
    st.session_state.mast_prompt = config.get_mast_prompt(st.session_state.version)


def render_sidebar(session_manager, activity_logger):
    config = st.session_state.config
    # Add prompt manipulation section if developer mode is enabled
    if st.session_state.get('developer_mode', False):
        with st.sidebar:
            with stylable_container(
                key="prompt_manipulation",
                css_styles="""
                {
                    background-color: #bcf1bc;
                    border-left: 5px solid green;
                    max-width: 100%;
                    padding-left: 10px;
                    margin: 5px;
                }
                .stTextArea {
                    padding-right: 20px;
                }
                .stTextArea textarea {
                    font-size: 14px;
                    width: 100%;
                    word-wrap: break-word;
                }
            """
            ):
                st.markdown('<div>', unsafe_allow_html=True)
                st.subheader("Prompt Manipulation (Dev Mode Only)")
                st.session_state.reset_prompt = False

                with st.form("sidebar_form", border=False):
                    # Use session state values for text areas
                    general_prompt = st.text_area(
                        "General Prompt",
                        value=st.session_state.general_prompt,
                        height=100,
                        key="general_prompt_area",
                    )
                    
                    supervisor_prompt = st.text_area(
                        "Supervisor Prompt",
                        value=st.session_state.supervisor_prompt,
                        height=100,
                        key="supervisor_prompt_area",
                    )

                    retriever_prompt = st.text_area(
                        "Retriever Prompt",
                        value=st.session_state.retriever_prompt,
                        height=100,
                        key="retriever_prompt_area",
                    )
                    
                    mast_prompt = st.text_area(
                        "MAST Prompt",
                        value=st.session_state.mast_prompt,
                        height=150,
                        key="mast_prompt_area",
                    )
                    save_button = st.form_submit_button("Save Prompt Changes")


                if save_button:                 
                    # Update session state with values from text areas
                    st.session_state.general_prompt = general_prompt
                    st.session_state.supervisor_prompt = supervisor_prompt
                    st.session_state.retriever_prompt = retriever_prompt
                    st.session_state.mast_prompt = mast_prompt
                
                    st.sidebar.success("Prompts updated successfully!")
                    
                    # Log the activity
                    activity_logger.save_activity(
                        st.session_state.user_id,
                        {
                            "user_activity": "update_prompts",
                            "general_prompt": general_prompt,
                            "supervisor_prompt": supervisor_prompt,
                            "retriever_prompt": retriever_prompt,
                            "mast_prompt": mast_prompt
                        }
                    )

                st.markdown('</div>', unsafe_allow_html=True)

    # Yesh removed thi for low mast
    # with st.sidebar:
    #     st.title("Choose Mode")
    #     analysis_style = st.selectbox(
    #         "Analysis Style",
    #         options=["Standard", "Detailed", "Concise", "Technical"],
    #         key="analysis_style_dropdown"
    #     )
            
    # Add a sidebar for document search
    with st.sidebar:
        st.title("Search Documents")
        search_query = st.text_input("Enter document id or keyword")
        if search_query:
            search_documents(search_query)
            activity_logger.save_activity(st.session_state.user_id, {"user_activity": "keyword_search", 
                                                        "search_query": search_query})


    with st.sidebar:
        st.title("Document List")
        input_file = config.get_retriever_config(st.session_state.version)["input_file"]
        with open(input_file, 'r') as json_file:
            documents = json.load(json_file)

        documents = dict(sorted(documents.items(), key=lambda item: int(item[0])))

        document_ids = list(documents.keys())
        document_titles = [documents[id]['title'] for id in document_ids]

        document_options = ["Select a document"] + [f"{id}: {title}" for id, title in zip(document_ids, document_titles)]

        # Display a selectbox to choose document
        selected_doc = st.selectbox("Choose a document", document_options)

        if selected_doc != "Select a document":
            selected_doc_index = int(selected_doc.split(":")[0].strip())-1
            # Main content area to display selected document content
            st.write(f"Document ID: {document_ids[selected_doc_index]}")
            st.write(f"Title: {document_titles[selected_doc_index]}")
            st.write(f"Date: {documents[document_ids[selected_doc_index]]['date']}")
            st.text_area(
                label = "Document Content", 
                value = f"{documents[document_ids[selected_doc_index]]['content']}.",
                disabled = True,
                height = 500
            )

            activity_logger.save_activity(st.session_state.user_id, {"user_activity": "select_document", 
                                        "document_id": document_ids[selected_doc_index]})

