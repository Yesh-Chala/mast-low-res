import streamlit as st

def apply_custom_styles():
            
    # add custom styling to remove the "blocking" cursor
    st.markdown(
        """
        <style>
        textarea {
            cursor: default!important;
        }
        </style>
        """, unsafe_allow_html=True
    )