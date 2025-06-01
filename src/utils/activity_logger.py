import json
import os
from datetime import datetime
import pytz
import streamlit as st

from src.components.google_drive import save_files

class ActivityLogger:
    def __init__(self): 
        self.config = st.session_state.config
        self.session_log_file = None # YEsh added this to store everything in a single file.
        if self.config.logging_enabled:
             #Yesh changed this
            # os.makedirs(self.config.get_logging_handlers()['file']['path'], exist_ok=True)
            os.makedirs(self.config.file_handler['path'], exist_ok=True)
    #Yesh added this to store everything in a single file.
    def _get_session_log_file(self, user_id: str) -> str:
        """Get or create the session log file name"""
        if 'session_log_file' not in st.session_state:
            timestamp = datetime.now(pytz.timezone(self.config.logging_format['timezone']))
            timestamp = timestamp.strftime(self.config.logging_format['timestamp_format'])
            st.session_state.session_log_file = f"{user_id}_session_{timestamp}.json"
        return st.session_state.session_log_file

    def save_activity(self, user_id: str, activity_data: dict):
        if not self.config.logging_enabled:
            return
        
        os.makedirs('./', exist_ok=True)
        if "user_timestamp" not in activity_data:
            user_timestamp = datetime.now(pytz.timezone(self.config.logging_format['timezone']))
            user_timestamp = user_timestamp.strftime(self.config.logging_format['timestamp_format'])

            activity_data = {
                    **activity_data,
                    "user_timestamp": user_timestamp
                }
            
        if activity_data.get("user_activity") == "chat_input":
            activity_data.update({
                "user_message": activity_data.get("user_message", ""),
                "assistant_reply": activity_data.get("assistant_reply", ""),
                "reply_timestamp": activity_data.get("reply_timestamp", ""),
                "version": st.session_state.get("version", ""),
                "developer_mode": st.session_state.get("developer_mode", False)
            })

        if self.config.file_handler['enabled']:
            # Yesh changed this to store everything in a single file.
            # filename = self.config.get_filename_template(
            #     user_id=user_id,
            #     timestamp=activity_data['user_timestamp']
            # )
            filename = self._get_session_log_file(user_id)
            existing_data = []
            if os.path.exists(filename):
                try:
                    with open(filename, 'r') as file:
                        existing_data = json.load(file)
                except json.JSONDecodeError:
                    existing_data = []

            # Append new activity
            existing_data.append(activity_data)

            # Write back all data
            with open(filename, 'w') as file:
                json.dump(existing_data, file, default=str, indent=self.config.file_handler['indent'])

            if self.config.google_drive_enabled:
                save_files(user_id, filename)

        if self.config.google_drive_enabled:
                save_files(user_id, filename)