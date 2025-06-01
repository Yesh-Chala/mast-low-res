import streamlit as st
import streamlit_analytics2 as streamlit_analytics

from src.utils.session_manager import SessionManager
from src.utils.activity_logger import ActivityLogger
from src.components.sidebar import *
from src.components.initial_page import render_initial_page
from src.components.chat_interface import render_chat_interface
from src.components.model_info import render_model_info
from src.components.styles import apply_custom_styles

def main():
    session_manager = SessionManager()
    logger = ActivityLogger()    

    # Initialize the session state
    if "page" not in st.session_state:
        st.session_state.page = "initial"

    # Display the appropriate page based on the session state
    if st.session_state.page == "initial":
        render_initial_page(session_manager, logger)
    else:
        with streamlit_analytics.track():
            render_main_app(session_manager, logger)



def render_header(activity_logger):
    popup_placeholder = st.empty()
    # Initialize the popup state in session state if it doesn't exist
    if 'show_popup' not in st.session_state:
        st.session_state.show_popup = False

    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("MASTOPIA")
    with col2:
        if st.session_state.version.startswith("Version 1:") or st.session_state.version.startswith("Version 3:"):
            if st.button("Model Info"):
                st.session_state.show_popup = not st.session_state.show_popup
                if 'user_id' in st.session_state:
                    activity_logger.save_activity(
                        st.session_state.user_id, 
                        {
                            "user_activity": "open_model_info" if st.session_state.show_popup else "close_model_info", 
                        }
                    )
    return popup_placeholder


def render_main_app(session_manager, logger):
    
    popup_placeholder = render_header(logger)
    apply_custom_styles()

    # Check if user_id exists in session state
    if 'user_id' not in st.session_state:
        st.error("User ID not found. Please start from the initial page.")
        return

    user_id = st.session_state.user_id
    version = st.session_state.version

    # Check if this is a new user
    if 'is_new_user' not in st.session_state:
        # You might want to check against a database or file to see if this user_id exists
        # For this example, we'll assume it's a new user if 'is_new_user' isn't in session state
        st.session_state.is_new_user = True

    # Initialize session for new users
    if st.session_state.is_new_user:
        # session_manager.initialize_session(st.session_state.version, user_id)
        render_initial_page(session_manager, logger)
        st.session_state.is_new_user = False  # Mark user as not new anymore
        st.rerun()

    new_session_container = st.container()

    # Create a popover for confirmation and stop button
    with new_session_container:
        # Use columns to align horizontally

        with st.popover("Start New Session"):
            st.write("Are you sure you want to start a new session?\n\nThis will clear all the current chat history.")
            if st.button("Confirm", key="confirm_new_session"):
                logger.save_activity(user_id, {"user_activity": "click_start_new_session_button"})
                session_manager.initialize_session(version, user_id)
                st.rerun()

    render_model_info(popup_placeholder)

    render_chat_interface(session_manager, logger)
    render_sidebar(session_manager, logger)


if __name__ == "__main__":
    with streamlit_analytics.track():
        main()





###########
# Run App #
###########

# streamlit run streamlit_app.py --server.enableCORS false --server.enableXsrfProtection false