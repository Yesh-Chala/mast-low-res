import streamlit as st
import operator
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from typing import Annotated, Sequence, TypedDict

from src.agents import supervisor, retriever, general_ai
from src.utils.vector_store import load_vector_retriever

class AgentState(TypedDict):
    input: Annotated[Sequence[BaseMessage], operator.add]
    output: Annotated[str, "Final answer"]
    next_action: Annotated[str, "Next action"]
    history: Annotated[list, "message histories for context"]


class GraphModel:
    def __init__(self):
        self.config = st.session_state.config
        performance_config, mast_config = self.config.get_version_configs(st.session_state.version)
        
        self.retriever = load_vector_retriever(
            mast_config['retriever']['path'],
            self.config.openai['api_key']
        )

    def get_compiled_graph(self):
        graph_builder = StateGraph(AgentState)
        # Add nodes
        graph_builder.add_node("Supervisor", supervisor.get_agent())
        graph_builder.add_node("Retriever", retriever.get_agent(self.retriever))
        graph_builder.add_node("GeneralAI", general_ai.get_agent())
        # Add edges
        graph_builder.add_conditional_edges("Supervisor", 
                                            lambda state: state["next_action"], 
                                            {"VAST" : "Retriever", "GENERAL" : "GeneralAI"})
        graph_builder.add_edge("Retriever", END)
        graph_builder.add_edge("GeneralAI", END)

        graph_builder.set_entry_point("Supervisor")
        graph = graph_builder.compile()
        return graph


    def execute(self, input_message, recursion_limit=5, max_iterations=1):
        graph = self.get_compiled_graph()

        # Update memory with the new input
        input_string = str(input_message['input'][0].content)
        print(">> user input: ", input_string )

        result = graph.stream(input_message,
                                 {"max_iterations": max_iterations})

        return result


    # def execute(self, input_message, recursion_limit=5, max_iterations=1):
    #     graph = self.get_compiled_graph()

    #     # Update memory with the new input
    #     input_string = str(input_message['input'][0].content)
    #     print(">> user input: ", input_string)

    #     result_generator = graph.stream(
    #         input_message,
    #         {"max_iterations": max_iterations},
    #         stream_mode="updates"
    #     )
        
    #     unified_output = {
    #         "input": input_string,
    #         "steps": [],
    #         "final_output": ""
    #     }
    #     try:
    #         for update in result_generator:
    #             for node, output in update.items():
    #                 print("===,", node) 
    #                 print("====", output)
    #                 step = {"node": node, "output": output}
    #                 unified_output["steps"].append(step)
    #                 if "output" in output:
    #                     unified_output["final_output"] = output["output"]
    #     except Exception as e:
    #         unified_output["error"] = str(e)

    #     return unified_output

    #     # return result_generator

