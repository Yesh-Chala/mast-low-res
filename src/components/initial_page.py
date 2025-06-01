import pytz
import streamlit as st
from datetime import datetime

def render_initial_page(session_manager, activity_logger):
    st.title("Welcome to Integrated MASTOPIA")
    
    # Version selection before login
    # version = st.radio(
    #     "Select MASTOPIA Version",
    #     ["Version 1: High-MAST High-PERFORMANCE",
    #      "Version 2: Low-MAST High-PERFORMANCE",
    #      "Version 3: High-MAST Low-PERFORMANCE",
    #      "Version 4: Low-MAST Low-PERFORMANCE"],
    #     index=0  # Default to latest version
    # )
    # Yesh changed this to Low-MAST Low-PERFORMANCE by default
    version = "Version 4: High-MAST High-PERFORMANCE"
    

    # Add checkbox for developer mode
    # Yesh removed this for low mast
    # developer_mode = st.checkbox("Enable Developer Mode", value=False)
    developer_mode = False # Yesh changed this to False for low mast by default
    # if 'state_dict' not in st.session_state:
    #     st.session_state.state_dict = {}
        # print("generated state_dict")

    user_id = st.text_input("Enter your designated user ID")
    if st.button("Continue"):
        if validate_user_id(user_id):
            st.session_state.version = version
            st.session_state.user_id = user_id
            st.session_state.page = "main"
            st.session_state.is_new_user = True  # Mark as new user
            st.session_state.developer_mode = developer_mode  # Store developer mode state

            if 'initial_timestamp' not in st.session_state:
                st.session_state.initial_timestamp = datetime.now(pytz.timezone('MST')).strftime("%Y-%m-%d_%H:%M:%S") # Record the timestamp in MST

            session_manager.initialize_user_session(version, user_id)
            activity_logger.save_activity(
                user_id,
                {"user_activity": "new_user_login", "selected_version": version, "developer_mode": developer_mode}
            )
            st.rerun()


        else:
            st.warning("Please make sure that you copied the full user ID from the survey. It should be a long sequence of letters and/or numbers.")

    


def validate_user_id(user_id: str) -> bool:
    return len(user_id.strip()) >= 0



            
