import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def get_agent():
    model_config = st.session_state.config.get_model_config(st.session_state.version)

    llm = ChatOpenAI(
            openai_api_key=st.session_state.config.openai['api_key'],
            model=model_config['name'],
            temperature=model_config['temperature']
        )    
    
    prompt = ChatPromptTemplate.from_messages(
        [    
            ("system", st.session_state.supervisor_prompt),
            ("system", "Below is chat history \n {history_messages}"),
            ("user", "Hi, how are you today?"),
            ("ai", "GENERAL"),
            ("user", "Identify any imminent terrorist threats in the Vastopolis metropolitan area."),
            ("ai", "VAST"),
            ("user", "{user_input}")
        ]
    )

    agent_executor = ( 
            {
                "history_messages" : lambda x: "\n".join(["{} : {}".format(msg['role'], msg['content']) for msg in x["history"]]),
                "user_input": lambda x: x["input"],
            }
            | prompt
            | llm
            | StrOutputParser()
            | (lambda text: {"next_action" : text})
            )

    return agent_executor